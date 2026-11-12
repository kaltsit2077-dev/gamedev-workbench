"""Bounded, read-only Godot text analysis; clues, never a semantic ownership proof."""
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gd_references import bindings,constant_value,calls
from gd_classes import class_evidence,IDENTIFIER

EXCLUDED = {'addons', 'tests', 'node_modules', 'vendor', 'build', 'dist'}
EXTENSIONS = {'.gd', '.tscn', '.tres', '.gdshader'}

def gd_lines(text):
    """Yield (line number, code with strings/comments masked, string spans)."""
    triple = None
    for number, line in enumerate(text.splitlines(), 1):
        mask=list(line); literals=[]; i=0
        while i < len(line):
            if triple:
                end=line.find(triple,i)
                stop=len(line) if end<0 else end+3
                mask[i:stop]=' '*(stop-i); i=stop
                if end>=0: triple=None
                continue
            if line[i]=='#':
                mask[i:]=' '*(len(line)-i); break
            if line[i] in {'"', "'"}:
                quote=line[i]; start=i
                if line[i:i+3]==quote*3:
                    triple=quote*3; mask[i:i+3]=' '*3; i+=3; continue
                i+=1
                while i<len(line):
                    if line[i]=='\\': i+=2; continue
                    if line[i]==quote: i+=1; break
                    i+=1
                literals.append((start,i,line[start+1:i-1]))
                mask[start:i]=' '*(i-start)
                continue
            i+=1
        yield number,''.join(mask),literals,line

def find_cycles(edges, nodes):
    graph={n:[] for n in nodes}
    for edge in edges:
        if edge['source'] in graph and edge['target'] in graph and edge['kind']!='path-literal':
            graph[edge['source']].append(edge['target'])
    color={}; cycles=[]
    for root in sorted(graph):
        if color.get(root): continue
        trail=[root]; color[root]=1; stack=[(root,iter(sorted(set(graph[root]))))]
        while stack:
            node,children=stack[-1]
            child=next(children,None)
            if child is None:
                color[node]=2; stack.pop(); trail.pop(); continue
            if color.get(child)==1 and len(cycles)<200:
                cycles.append(trail[trail.index(child):]+[child])
            elif not color.get(child):
                color[child]=1; trail.append(child); stack.append((child,iter(sorted(set(graph[child])))))
    return cycles

def analyze_project(project, include_tests=False, include_addons=False, max_files=3000, max_bytes=2_000_000):
    root=Path(project).expanduser().resolve()
    if not root.is_dir() or not (root/'project.godot').is_file():
        raise ValueError('A directory containing project.godot is required')
    if max_files<1 or max_bytes<1: raise ValueError('Limits must be positive')
    excluded=EXCLUDED-({'tests'} if include_tests else set())-({'addons'} if include_addons else set())
    report={'format_version':1,'snapshot_utc':datetime.now(timezone.utc).isoformat(),
            'engine':'godot','execution':'read-only text scan; no engine invoked','entry':None,'autoloads':[],
            'declared_features':None,'actual_engine_version':'unverified','files':[], 'references':[],
            'dynamic_references':[], 'members':[], 'state_write_clues':[], 'cycles':[], 'warnings':[],
            'uid_metadata_files':[], 'uid_references':[], 'uid_conflicts':[],
            'class_definitions':[], 'class_references':[],
            'source_fingerprints':{},'scope':{'analysis_revision':3,'uid_metadata_limit':max_files,'excluded_directories':sorted(excluded),'hidden_and_symlinks':'excluded','max_files':max_files,'max_bytes_per_file':max_bytes},
            'limits':['No AST/type/scope resolution; bare member matches may be shadowed by locals.',
                      'Matching property names on different receivers do not prove shared state.',
                      'Source UID mappings and finite constant expressions are clues; engine cache, runtime paths, groups and signals remain incomplete.',
                      'Named inheritance resolves simple root-level bases only against scanned class_name declarations; unindexed bases may be built-in, excluded or missing. Type annotations, calls and nested bases are not inferred.',
                      'No private file content or credentials are collected; output can still reveal project structure.']}
    config=root/'project.godot'
    if config.is_symlink() or config.stat().st_size>max_bytes: raise ValueError('project.godot is symlinked or exceeds the file limit')
    raw=config.read_bytes(); report['source_fingerprints']['project.godot']=hashlib.sha256(raw).hexdigest()
    section=''
    for line in raw.decode('utf-8-sig').splitlines():
        line=line.strip()
        if line.startswith('['): section=line.strip('[]'); continue
        match=re.match(r'([^=]+)=(.*)',line)
        if not match: continue
        key,value=match.groups(); key=key.strip(); value=value.strip()
        if section=='application' and key=='run/main_scene': report['entry']=value.strip('"')
        if section=='application' and key=='config/features': report['declared_features']=value
        if section=='autoload': report['autoloads'].append({'name':key,'path':value.strip('"').lstrip('*')})
    paths=[]; metadata=[]
    def walk_error(error):
        report['warnings'].append('Directory could not be scanned: '+type(error).__name__)
    for directory,dirs,files in os.walk(root,followlinks=False,onerror=walk_error):
        dirs[:]=sorted(d for d in dirs if not d.startswith('.') and d not in excluded
                       and not (Path(directory)/d).is_symlink()
                       and (Path(directory)/d).resolve().is_relative_to(root)
                       and not (Path(directory)/d/'.gdignore').exists())
        for name in sorted(files):
            path=Path(directory)/name
            if name.startswith('.') or path.is_symlink() or not path.resolve().is_relative_to(root): continue
            if path.suffix in {'.uid','.import'}:
                if len(metadata)<max_files: metadata.append(path)
                elif 'UID metadata limit reached' not in report['warnings']: report['warnings'].append('UID metadata limit reached')
                continue
            if path.suffix not in EXTENSIONS: continue
            if len(paths)>=max_files:
                break
            paths.append(path)
        if len(paths)>=max_files:
            report['warnings'].append('File limit reached; scan may be incomplete')
            break
    texts={}; uid_paths={}
    for path in paths+metadata:
        name=path.relative_to(root).as_posix()
        try:
            if path.stat().st_size>max_bytes: raise ValueError('file limit')
            raw=path.read_bytes(); text=raw.decode('utf-8-sig'); texts[name]=text
        except (OSError,UnicodeError,ValueError) as exc:
            report['warnings'].append(name+': '+type(exc).__name__); continue
        report['source_fingerprints'][name]=hashlib.sha256(raw).hexdigest()
        uid=None; target=None
        if path.suffix=='.uid': uid=text.strip(); target=name[:-4]
        elif path.suffix=='.import':
            section=''
            for row in text.splitlines():
                if row.startswith('['): section=row
                match=re.match(r'uid="(uid://[a-z0-9]+)"',row)
                if section=='[remap]' and match: uid=match[1]; target=name[:-7]
        elif path.suffix in {'.tscn','.tres'}:
            header=text.splitlines()[0] if text.splitlines() else ''
            match=re.search(r'\buid="(uid://[a-z0-9]+)"',header)
            if header.startswith(('[gd_scene','[gd_resource')) and match: uid=match[1]; target=name
        if uid and re.fullmatch(r'uid://[a-z0-9]+',uid): uid_paths.setdefault(uid,set()).add(target)
        if path in metadata: report['uid_metadata_files'].append(name)
    report['uid_conflicts']=[{'uid':uid,'paths':sorted(targets)} for uid,targets in sorted(uid_paths.items()) if len(targets)>1]
    report['class_definitions'],report['class_references']=class_evidence(texts,gd_lines)
    def uid_target(uid,source,number,fallback=None):
        candidates=sorted(uid_paths.get(uid,()))
        status='ambiguous' if len(candidates)>1 else ('source-resolved' if candidates else 'unknown')
        item={'source':source,'line':number,'uid':uid,'status':status,'candidates':candidates}
        if fallback:
            item['fallback']=fallback
            if len(candidates)==1 and candidates[0]!=fallback.removeprefix('res://'): item['path_disagrees']=True
        report['uid_references'].append(item)
        return 'res://'+candidates[0] if len(candidates)==1 else None
    if report['entry'] and report['entry'].startswith('uid://'): report['entry_resolution']=uid_target(report['entry'],'project.godot',0)
    def add_ref(source,number,target,kind,resolution=None):
        original=target
        if target.startswith('uid://'):
            target=uid_target(target,source,number)
            if not target: return
            resolution='source-uid'
        relative=target.removeprefix('res://')
        resolved=(root/relative).resolve()
        status='outside-project' if not resolved.is_relative_to(root) else ('exists' if resolved.exists() else 'missing')
        item={'source':source,'line':number,'target':relative,'kind':kind,'status':status}
        if resolution: item.update(resolution=resolution,expression_value=original)
        report['references'].append(item)
    for item in report['class_references']:
        if item['status']=='source-resolved':
            add_ref(item['source'],item['line'],'res://'+item['candidates'][0],'extends-class','source-class-index')
            report['references'][-1]['class_name']=item['name']
    for path in paths:
        name=path.relative_to(root).as_posix()
        if name not in texts: continue
        text=texts[name]; report['files'].append(name)
        if path.suffix!='.gd':
            for number,line in enumerate(text.splitlines(),1):
                if line.lstrip().startswith('[ext_resource'):
                    targets=re.findall(r'\bpath="(res://[^"\n]+)"',line)
                    uid=re.search(r'\buid="(uid://[a-z0-9]+)"',line)
                    resolved_uid=uid_target(uid[1],name,number,targets[0] if targets else None) if uid else None
                    for target in targets:
                        add_ref(name,number,target,'ext-resource')
                        if resolved_uid and report['references'][-1]['status']=='missing':
                            report['references'][-1].update(status='missing-path-with-uid-candidate',uid_candidate=resolved_uid)
                    if resolved_uid and resolved_uid not in targets: add_ref(name,number,resolved_uid,'uid-resolution')
            continue
        lines=list(gd_lines(text)); members=set(); constants,scopes=bindings(lines)
        for number,code,literals,line in lines:
            match=re.match(r'^(?:@\w+(?:\([^\n]*?\))?\s+)*var\s+(\w+)',code)
            if match:
                members.add(match[1]); report['members'].append({'file':name,'line':number,'name':match[1]})
        method='<initialization>'
        for number,code,literals,line in lines:
            match=re.match(r'^(?:static\s+)?func\s+(\w+)',code)
            if match: method=match[1]
            resource_calls=list(calls(code,line))
            for kind,start,end,expression in resource_calls:
                try:
                    value=constant_value(expression or '',constants,scopes.get(method,()))
                    if not isinstance(value,str) or not value.startswith(('res://','uid://')): raise ValueError('not a resource path')
                    add_ref(name,number,value,kind,'finite-constant-expression')
                except (ValueError,SyntaxError,TypeError,KeyError,OverflowError):
                    report['dynamic_references'].append({'source':name,'line':number,'kind':kind,'reason':'runtime/shadowed/unsupported argument'})
            for start,end,value in literals:
                if any(first<=start<last for kind,first,last,expression in resource_calls): continue
                if not value.startswith(('res://','uid://')): continue
                prefix=code[:start]
                kind='extends' if re.fullmatch(r'(?:class_name\s+'+IDENTIFIER+r'\s+)?extends',prefix.strip()) else 'path-literal'
                dynamic='%' in value or bool(re.match(r'\s*[+%]',code[end:]))
                if dynamic:
                    report['dynamic_references'].append({'source':name,'line':number,'kind':kind,'reason':'formatted/concatenated path'})
                else: add_ref(name,number,value,kind)
            if method=='<initialization>': continue
            for assign in re.finditer(r'(?<![\w.])([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*(\+=|-=|\*=|/=|=(?!=))',code):
                target,operator=assign.groups()
                if '.' in target or (target in members and target not in scopes.get(method,set())):
                    report['state_write_clues'].append({'file':name,'line':number,'method':method,'target':target,'operator':operator,
                        'binding':'receiver unresolved' if '.' in target and not target.startswith('self.') else 'member name match; local shadowing unresolved'})
    report['cycles']=find_cycles(report['references'],report['files'])
    return report
