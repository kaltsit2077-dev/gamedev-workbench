"""Readable, conservative reports over existing read-only analysis snapshots."""
import html
import json
from pathlib import Path
import re

def validate_snapshot(data):
    if not isinstance(data,dict) or data.get('format_version')!=1 or data.get('engine')!='godot':
        raise ValueError('Expected a format_version=1 Godot analysis snapshot')
    for key in ['files','references','state_write_clues','cycles','warnings','autoloads']:
        if not isinstance(data.get(key),list): raise ValueError('Missing/invalid snapshot list: '+key)
    for key in ['scope','source_fingerprints']:
        if not isinstance(data.get(key),dict): raise ValueError('Missing/invalid snapshot object: '+key)
    for key in ['references','state_write_clues','autoloads']:
        if not all(isinstance(row,dict) for row in data[key]): raise ValueError('Invalid row in '+key)
    if not all(isinstance(k,str) and isinstance(v,str) for k,v in data['source_fingerprints'].items()):
        raise ValueError('Invalid source fingerprint map')

def read_analysis(path):
    path=Path(path)
    if path.stat().st_size>20_000_000: raise ValueError('Analysis input exceeds 20 MB')
    data=json.loads(path.read_text(encoding='utf-8'))
    validate_snapshot(data)
    return data

def write_new(path,text):
    # Exclusive creation also prevents an output alias from replacing an input.
    with Path(path).open('x',encoding='utf-8',newline='\n') as file: file.write(text)

def cell(value):
    value=html.escape(str(value),quote=True).replace('\r',' ').replace('\n',' ⏎ ')
    return re.sub(r'([\\`|\[\]()_*#!])',r'\\\1',value)

def render_analysis(report,max_rows=40):
    validate_snapshot(report)
    if not 1<=max_rows<=200: raise ValueError('max_rows must be between 1 and 200')
    lines=['# 工程分析阅读稿','',
           '这是文本扫描线索，需结合项目约束、源码和行为验证判断；不证明完整依赖或状态所有权。','',
           '入口：'+cell(report.get('entry') or '未解析'),'',
           '扫描文件：'+str(len(report['files']))+'；引用线索：'+str(len(report['references']))+'；状态写入线索：'+str(len(report['state_write_clues']))+'。','',
           '## 扫描范围与限制','',cell(json.dumps(report['scope'],ensure_ascii=False)),'']
    for warning in report['warnings']: lines.append('- 扫描警告：'+cell(warning))
    for limit in report.get('limits',[]): lines.append('- '+cell(limit))
    def table(title,rows,columns):
        lines.extend(['','## '+title,'','| '+' | '.join(label for label,key in columns)+' |',
                      '| '+' | '.join('---' for _ in columns)+' |'])
        for row in rows[:max_rows]: lines.append('| '+' | '.join(cell(row.get(key,'')) for label,key in columns)+' |')
        if len(rows)>max_rows: lines.extend(['',f'省略 {len(rows)-max_rows} 条；完整内容保留在原始 JSON。'])
    table('Autoload',report['autoloads'],[('名称','name'),('路径','path')])
    table('资源引用',report['references'],[('来源','source'),('目标','target'),('类型','kind'),('路径状态','status')])
    table('状态写入线索',report['state_write_clues'],[('文件','file'),('方法','method'),('目标','target'),('操作','operator'),('绑定限制','binding')])
    lines.extend(['','## 循环线索',''])
    for cycle in report['cycles'][:max_rows]: lines.append('- '+cell(' → '.join(str(x) for x in cycle)))
    if len(report['cycles'])>max_rows: lines.append(f'省略 {len(report["cycles"])-max_rows} 条循环线索。')
    lines.extend(['','动态引用未被解析的数量：'+str(len(report.get('dynamic_references',[])))+'。',
                  '未发现某条引用，不等于该依赖不存在。循环列表是扫描器发现的线索，不是全部循环的枚举。',''])
    return '\n'.join(lines)

def compare_analysis(before,after):
    validate_snapshot(before); validate_snapshot(after)
    old=before['source_fingerprints']; new=after['source_fingerprints']
    def rows(data,key,fields):
        return {tuple(str(row.get(field,'')) for field in fields) for row in data[key]}
    def difference(key,fields):
        left=rows(before,key,fields); right=rows(after,key,fields)
        encode=lambda values:[dict(zip(fields,row)) for row in sorted(values)]
        return encode(right-left),encode(left-right)
    refs_added,refs_removed=difference('references',['source','target','kind','status'])
    writes_added,writes_removed=difference('state_write_clues',['file','method','target','operator'])
    auto_added,auto_removed=difference('autoloads',['name','path'])
    def cycles(data):
        result=set()
        for cycle in data['cycles']:
            if not isinstance(cycle,list) or not all(isinstance(x,str) for x in cycle): raise ValueError('Invalid cycle')
            nodes=cycle[:-1] if len(cycle)>1 and cycle[0]==cycle[-1] else cycle
            if nodes: result.add(min(tuple(nodes[i:]+nodes[:i]) for i in range(len(nodes))))
        return result
    old_cycles=cycles(before); new_cycles=cycles(after)
    return {'format_version':1,'kind':'analysis-comparison','scope_comparable':before['scope']==after['scope'] and not before['warnings'] and not after['warnings'],
            'before_snapshot':before.get('snapshot_utc'),'after_snapshot':after.get('snapshot_utc'),
            'files_added':sorted(new.keys()-old.keys()),'files_removed':sorted(old.keys()-new.keys()),
            'files_modified':sorted(k for k in old.keys()&new.keys() if old[k]!=new[k]),
            'entry_changed':before.get('entry')!=after.get('entry'),'autoloads_added':auto_added,'autoloads_removed':auto_removed,
            'references_added':refs_added,'references_removed':refs_removed,
            'new_unresolved_references':[r for r in refs_added if r['status'] in {'missing','outside-project'}],
            'write_clues_added':writes_added,'write_clues_removed':writes_removed,
            'cycles_added':[list(c)+[c[0]] for c in sorted(new_cycles-old_cycles)],
            'cycles_removed':[list(c)+[c[0]] for c in sorted(old_cycles-new_cycles)],
            'warnings_before':before['warnings'],'warnings_after':after['warnings'],
            'limits':['Caller must confirm that snapshots describe the same project.',
                      'Different or incomplete scan scopes make additions/removals provisional.',
                      'Line shifts are ignored; changes are structural text clues, not semantic regressions.',
                      'New writes do not prove competing writers; removed cycles do not prove acyclicity.']}
