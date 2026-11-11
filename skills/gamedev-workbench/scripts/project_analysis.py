"""Bounded, read-only Godot text analysis; clues, never a semantic ownership proof."""
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re

EXCLUDED = {'addons', 'tests', 'node_modules', 'vendor', 'build', 'dist'}
EXTENSIONS = {'.gd', '.tscn', '.tres'}

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
            'source_fingerprints':{},'scope':{'excluded_directories':sorted(excluded),'hidden_and_symlinks':'excluded','max_files':max_files,'max_bytes_per_file':max_bytes},
            'limits':['No AST/type/scope resolution; bare member matches may be shadowed by locals.',
                      'Matching property names on different receivers do not prove shared state.',
                      'Dynamic paths, UIDs, runtime groups and signal calls are not a complete dependency graph.',
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
    paths=[]
    def walk_error(error):
        report['warnings'].append('Directory could not be scanned: '+type(error).__name__)
    for directory,dirs,files in os.walk(root,followlinks=False,onerror=walk_error):
        dirs[:]=sorted(d for d in dirs if not d.startswith('.') and d not in excluded
                       and not (Path(directory)/d).is_symlink()
                       and (Path(directory)/d).resolve().is_relative_to(root)
                       and not (Path(directory)/d/'.gdignore').exists())
        for name in sorted(files):
            path=Path(directory)/name
            if name.startswith('.') or path.suffix not in EXTENSIONS or path.is_symlink() or not path.resolve().is_relative_to(root): continue
            if len(paths)>=max_files:
                break
            paths.append(path)
        if len(paths)>=max_files:
            report['warnings'].append('File limit reached; scan may be incomplete')
            break
    def add_ref(source,number,target,kind):
        relative=target.removeprefix('res://')
        resolved=(root/relative).resolve()
        status='outside-project' if not resolved.is_relative_to(root) else ('exists' if resolved.exists() else 'missing')
        report['references'].append({'source':source,'line':number,'target':relative,'kind':kind,'status':status})
    for path in paths:
        name=path.relative_to(root).as_posix()
        try:
            if path.stat().st_size>max_bytes:
                report['warnings'].append('File too large: '+name); continue
            raw=path.read_bytes(); text=raw.decode('utf-8-sig')
        except (OSError,UnicodeError) as exc:
            report['warnings'].append(name+': '+type(exc).__name__); continue
        report['source_fingerprints'][name]=hashlib.sha256(raw).hexdigest(); report['files'].append(name)
        if path.suffix!='.gd':
            for number,line in enumerate(text.splitlines(),1):
                if line.lstrip().startswith('[ext_resource'):
                    for target in re.findall(r'\bpath="(res://[^"\n]+)"',line): add_ref(name,number,target,'ext-resource')
            continue
        lines=list(gd_lines(text)); members=set()
        for number,code,literals,line in lines:
            match=re.match(r'^(?:@\w+(?:\([^\n]*?\))?\s+)*var\s+(\w+)',code)
            if match:
                members.add(match[1]); report['members'].append({'file':name,'line':number,'name':match[1]})
        method='<initialization>'
        for number,code,literals,line in lines:
            match=re.match(r'^(?:static\s+)?func\s+(\w+)',code)
            if match: method=match[1]
            literal_call_starts=set()
            for start,end,value in literals:
                if not value.startswith('res://'): continue
                prefix=code[:start]
                call=re.search(r'\b(preload|load)\s*\(\s*$',prefix)
                kind=call[1] if call else ('extends' if prefix.strip()=='extends' else 'path-literal')
                if call: literal_call_starts.add(call.start())
                dynamic='%' in value or bool(re.match(r'\s*[+%]',code[end:]))
                if dynamic:
                    report['dynamic_references'].append({'source':name,'line':number,'kind':kind,'reason':'formatted/concatenated path'})
                else: add_ref(name,number,value,kind)
            for call in re.finditer(r'\b(?:preload|load)\s*\(',code):
                if call.start() not in literal_call_starts:
                    report['dynamic_references'].append({'source':name,'line':number,'kind':'load','reason':'computed argument'})
            if method=='<initialization>': continue
            for assign in re.finditer(r'(?<![\w.])([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*(\+=|-=|\*=|/=|=(?!=))',code):
                target,operator=assign.groups()
                if '.' in target or target in members:
                    report['state_write_clues'].append({'file':name,'line':number,'method':method,'target':target,'operator':operator,
                        'binding':'receiver unresolved' if '.' in target and not target.startswith('self.') else 'member name match; local shadowing unresolved'})
    report['cycles']=find_cycles(report['references'],report['files'])
    return report
