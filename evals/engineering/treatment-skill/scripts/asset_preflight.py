"""Manifest-bounded asset dependencies/metadata; never imports assets or proves rights."""
import hashlib
import json
from pathlib import Path
import struct
import urllib.parse

def audit_assets(project,manifest):
    root=Path(project).resolve(); errors=[]; warnings=[]; assets=[]
    result={'kind':'asset-preflight','passed':False,'errors':errors,'warnings':warnings,'assets':assets,
            'limits':['License fields are caller declarations, not verified rights.','PNG checks cover header dimensions, not full decoding or visual quality.','Dependency checks do not prove engine import, materials or runtime appearance.']}
    if not root.is_dir(): raise ValueError('Asset root must be a directory')
    entries=manifest.get('assets') if isinstance(manifest,dict) else None
    if not isinstance(entries,list) or not 1<=len(entries)<=1000: errors.append('assets must contain 1..1000 entries'); return result
    seen=set(); hashes={}
    def resolve(relative):
        if not isinstance(relative,str) or not relative: raise ValueError('Invalid asset path')
        relative=relative.removeprefix('res://')
        if '://' in relative or Path(relative).is_absolute(): raise ValueError('External/absolute path not allowed')
        path=root/relative
        if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path,*path.parents] if p!=root and p.is_relative_to(root)):
            raise ValueError('Asset path escapes root or traverses a symlink')
        return path.resolve()
    for entry in entries:
        if not isinstance(entry,dict): errors.append('Asset entry must be an object'); continue
        name=entry.get('path'); item={'path':name,'format_checks':'file-and-declaration-only'}; assets.append(item)
        if not isinstance(name,str): errors.append('Asset path must be a string'); continue
        if name in seen: errors.append('Duplicate manifest path: '+str(name))
        seen.add(str(name))
        try:
            path=resolve(name)
            if not path.is_file(): raise ValueError('Asset missing')
            if path.stat().st_size>50_000_000: raise ValueError('Asset exceeds 50 MB preflight bound')
            raw=path.read_bytes(); digest=hashlib.sha256(raw).hexdigest(); item.update(bytes=len(raw),sha256=digest)
            hashes.setdefault(digest,[]).append(name)
            if not isinstance(entry.get('license'),str) or entry['license'].casefold().strip() in {'','unknown','tbd'}:
                warnings.append(str(name)+': license declaration missing/unknown')
            if path.suffix.lower()=='.png':
                item['format_checks']='png-header'
                if len(raw)<33 or raw[:8]!=b'\x89PNG\r\n\x1a\n' or raw[12:16]!=b'IHDR': raise ValueError('Invalid PNG header')
                width,height=struct.unpack('>II',raw[16:24]); item.update(width=width,height=height)
                if not width or not height: raise ValueError('Zero-size PNG')
                if 'expected_size' in entry and entry['expected_size']!=[width,height]: errors.append(str(name)+': dimensions differ from manifest')
            gltf=None
            if path.suffix.lower()=='.gltf': gltf=json.loads(raw.decode('utf-8'))
            elif path.suffix.lower()=='.glb':
                if len(raw)<20: raise ValueError('Truncated GLB')
                magic,version,length=struct.unpack('<4sII',raw[:12]); chunk_length,chunk_type=struct.unpack('<II',raw[12:20])
                if magic!=b'glTF' or version!=2 or length!=len(raw) or chunk_type!=0x4e4f534a or chunk_length%4 or 20+chunk_length>len(raw): raise ValueError('Invalid GLB header/JSON chunk')
                gltf=json.loads(raw[20:20+chunk_length].decode('utf-8').rstrip('\x00 '))
            if gltf is not None:
                item['format_checks']='gltf-dependencies'
                if not isinstance(gltf,dict): raise ValueError('glTF JSON must be an object')
                dependencies=[]; item['dependencies']=dependencies
                for part in ['buffers','images']:
                    values=gltf.get(part,[])
                    if not isinstance(values,list): raise ValueError('Invalid glTF '+part)
                    for value in values:
                        if not isinstance(value,dict): raise ValueError('Invalid glTF dependency')
                        uri=value.get('uri')
                        if not uri: continue
                        if not isinstance(uri,str): raise ValueError('Invalid glTF URI')
                        if uri.startswith('data:'): continue
                        parsed=urllib.parse.urlsplit(uri)
                        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment: raise ValueError('External or complex URI not supported')
                        decoded=urllib.parse.unquote(parsed.path)
                        if Path(decoded).is_absolute(): raise ValueError('Absolute glTF URI not allowed')
                        relative=path.parent.relative_to(root)/decoded
                        dependency=resolve(relative.as_posix()); dependencies.append(dependency.relative_to(root).as_posix())
                        if not dependency.is_file(): errors.append(str(name)+': missing dependency '+decoded)
            item['metadata_checked']=True
        except (OSError,UnicodeError,ValueError,TypeError,struct.error) as error:
            errors.append(str(name)+': '+str(error)); item['metadata_checked']=False
    result['duplicate_content']=[names for names in hashes.values() if len(names)>1]
    result['passed']=not errors and not warnings
    return result
