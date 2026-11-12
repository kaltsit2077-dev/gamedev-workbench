"""A read-only offline task/artifact view; no chat backend or hidden execution."""
import hashlib
import json
from pathlib import Path
from creative_workspace import check_workspace
from workspace_io import local_path, read_json
from analysis_reports import write_new


def render_workspace(directory):
    root = Path(directory).resolve(strict=True)
    report = check_workspace(root); workspace = read_json(local_path(root, 'workspace.json'))
    artifacts = {}; total = 0
    for task in workspace['tasks']:
        for name in task['outputs']:
            if name in artifacts: continue
            path = local_path(root, name)
            if not path.is_file(): artifacts[name] = {'text': '产物缺失', 'sha256': None}; continue
            if path.stat().st_size > 64_000: raise ValueError('Workspace preview artifact exceeds 64 KB')
            raw = path.read_bytes(); total += len(raw)
            if total > 500_000: raise ValueError('Workspace preview exceeds 500 KB total')
            artifacts[name] = {'text': raw.decode('utf-8'), 'sha256': hashlib.sha256(raw).hexdigest()}
    payload = json.dumps({'workspace': workspace, 'report': report, 'artifacts': artifacts}, ensure_ascii=True, separators=(',', ':'))
    payload = payload.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return TEMPLATE.replace('__DATA__', payload)


def export_workspace(directory, output):
    write_new(output, render_workspace(directory))
    return {'output': str(output), 'state': 'draft', 'mode': 'offline read-only snapshot', 'engine_started': False,
            'ai_execution': 'Use the current host assistant with the selected task export; no model backend is running here.'}


TEMPLATE = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-gdw-workspace'; base-uri 'none'; form-action 'none'">
<title>GameDev Workbench · 创作工作区</title><style>
:root{color-scheme:dark;--bg:#101c28;--panel:#192b38;--line:#3d5663;--text:#e4ecee;--muted:#a8b8c1;--accent:#75d6cc;--warn:#ffd28b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 'Segoe UI','Microsoft YaHei',sans-serif}header,main,footer{max-width:1400px;margin:auto;padding:24px 32px}header{border-bottom:1px solid var(--line)}h1{font-size:clamp(26px,3vw,38px);line-height:1.2;margin:10px 0}h2{font-size:24px;margin:0}h3{font-size:18px;margin:16px 0 8px}p{color:var(--muted);max-width:78ch;margin:8px 0}button,select{font:inherit;color:var(--text);background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:9px 12px;max-width:100%}button{cursor:pointer}button:hover{border-color:var(--accent)}button[aria-pressed=true]{border-color:var(--accent);color:var(--accent)}:focus-visible{outline:3px solid var(--warn);outline-offset:3px}.layout{display:grid;grid-template-columns:210px minmax(0,1fr);gap:32px}nav{display:grid;gap:8px;align-content:start}nav button{text-align:left}.detail{min-width:0}.summary{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}.state{color:var(--warn)}.requirements{padding-left:22px}.requirements li{padding:3px 0}.filebar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:24px 0 12px}label{display:grid;gap:6px;min-width:0;flex:1}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#07111b;border:1px solid var(--line);border-radius:5px;padding:20px;min-height:250px;margin:0;font:15px/1.6 Consolas,'Microsoft YaHei',monospace}.hash{font-size:13px;color:var(--muted);overflow-wrap:anywhere}.checks{border-top:1px solid var(--line);margin-top:24px;padding-top:16px}.checks ul{padding-left:22px}.checks li{padding:3px 0}footer{font-size:14px;border-top:1px solid var(--line);color:var(--muted)}
@media(max-width:680px){header,main,footer{padding:20px}.layout{grid-template-columns:1fr;gap:24px}nav{display:flex;flex-wrap:wrap;gap:8px}nav button{flex:1 1 130px}pre{padding:12px;font-size:14px}.summary button{width:100%}}
</style></head><body><header><div>GameDev Workbench / 创作工作区</div><h1 id="title"></h1><p id="status"></p><p>这是可编辑设计文件的只读快照。先检查需求与产物，再把选中的任务包交给当前 AI 助手继续处理；本页不连接模型或启动引擎。</p></header>
<main><div class="layout"><nav id="tasks" aria-label="创作阶段"></nav><section class="detail" aria-live="polite"><div class="summary"><div><h2 id="taskTitle"></h2><span class="state">设计草案 · 待审查与实现</span></div><button id="download">下载当前任务包</button></div><p id="dependencies"></p><h3>关联需求</h3><ul id="requirements" class="requirements"></ul><div class="filebar"><label>产物文件<select id="files"></select></label></div><pre id="content"></pre><p id="hash" class="hash"></p><div class="checks"><h3>工作区检查</h3><p id="checkSummary"></p><ul id="failures"></ul><p>结构检查不验收设计质量、游戏实现或玩家体验。编辑源文件后需重新导出本页。</p></div></section></div></main><footer>本地文件 · 无外部请求 · 全部阶段初始为草案 · 素材、场景与代码仍需在目标引擎中实现和验证。</footer>
<script type="application/json" id="data">__DATA__</script><script nonce="gdw-workspace">
'use strict';const {workspace,report,artifacts}=JSON.parse(document.getElementById('data').textContent),el=id=>document.getElementById(id),make=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
const names={experience:'体验目标',mechanics:'机制与数值',narrative:'剧情与分支',art:'风格与制作规格',ui:'界面与交互',assets:'资产与导入',implementation:'引擎实现交接',verification:'验收与证据'};let selected=0;
el('title').textContent=workspace.title;el('status').textContent=`目标：${workspace.engine} · ${workspace.tasks.length} 个阶段 · ${workspace.requirements.length} 条需求 · 草案快照`;
el('checkSummary').textContent=`${report.checks.filter(c=>c.passed).length} / ${report.checks.length} 项结构/有限模型检查通过；游戏实现未验收。`;
for(const c of report.checks.filter(c=>!c.passed))el('failures').append(make('li',c.name));
const buttons=workspace.tasks.map((t,i)=>{const b=make('button',names[t.id]||t.id);b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>show(i));el('tasks').append(b);return b;});
function file(){const name=el('files').value,artifact=artifacts[name];el('content').textContent=artifact?.text||'尚无产物';el('hash').textContent=artifact?.sha256?`快照 SHA-256：${artifact.sha256}`:'此文件尚未生成。';}
function show(index){selected=index;const task=workspace.tasks[index];buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===index)));el('taskTitle').textContent=names[task.id]||task.id;el('dependencies').textContent=task.depends_on.length?'前置阶段：'+task.depends_on.map(id=>names[id]||id).join('、'):'从体验目标开始。';el('requirements').replaceChildren();for(const id of task.requirements){const r=workspace.requirements.find(r=>r.id===id);el('requirements').append(make('li',`${id}：${r?.text||'未知需求'}`));}el('files').replaceChildren();for(const name of task.outputs){const o=make('option',name);o.value=name;el('files').append(o);}file();}
el('files').addEventListener('change',file);show(0);
el('download').addEventListener('click',()=>{const task=workspace.tasks[selected];const bundle={schema_version:1,engine:workspace.engine,task,requirements:workspace.requirements.filter(r=>task.requirements.includes(r.id)),artifacts:Object.fromEntries(task.outputs.map(name=>[name,artifacts[name]])),instruction:'Read the actual project rules before implementation. Preserve unverified states; provide editable artifacts and separate evidence. This export is a draft, not approval to publish or install tools.'};const url=URL.createObjectURL(new Blob([JSON.stringify(bundle,null,2)+'\n'],{type:'application/json'}));const a=make('a');a.href=url;a.download=`task-${task.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
</script></body></html>
'''
