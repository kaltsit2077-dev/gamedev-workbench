"""Export bounded native PNG evidence as a standalone, offline HTML viewer."""
import base64
import json
from pathlib import Path, PurePosixPath
import struct

MAX_REPORT = 4_000_000
MAX_IMAGE = 5_000_000
MAX_TOTAL = 50_000_000
MAX_PIXELS = 16_000_000


def load_evidence(directory):
    root = Path(directory).resolve(strict=True)
    report_path = root / 'report.json'
    if report_path.is_symlink() or report_path.stat().st_size > MAX_REPORT:
        raise ValueError('Report must be a regular local JSON file below 4 MB')
    report = json.loads(report_path.read_text(encoding='utf-8'))
    if not isinstance(report, dict) or type(report.get('passed')) is not bool:
        raise ValueError('Report requires a boolean passed field')
    checks, frames = report.get('checks'), report.get('frames')
    if not isinstance(checks, list) or len(checks) > 5000 or not isinstance(frames, list) or len(frames) > 200:
        raise ValueError('Expected checks (max 5000) and frames (max 200) lists')
    for item in checks:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str) or type(item.get('passed')) is not bool:
            raise ValueError('Each check requires name and boolean passed')
    if report['passed'] and any(not c['passed'] for c in checks):
        raise ValueError('Report claims passed despite a failed check')
    if report['passed'] and not checks:
        raise ValueError('A passed report must contain checks')
    images, total = [], 0
    for item in frames:
        if not isinstance(item, dict) or not isinstance(item.get('image'), str):
            raise ValueError('Each frame requires a relative PNG image path')
        name = item['image']
        relative = PurePosixPath(name)
        if not name or '\\' in name or ':' in name or relative.is_absolute() or '..' in relative.parts or relative.suffix.lower() != '.png':
            raise ValueError('Frame path must be a relative local PNG without traversal')
        candidate = root
        for part in relative.parts:
            candidate = candidate / part
            if candidate.is_symlink():
                raise ValueError('Frame paths cannot contain symlinks')
        if not candidate.resolve(strict=True).is_relative_to(root) or not candidate.is_file():
            raise ValueError('Frame escapes evidence directory or is not a file')
        size = candidate.stat().st_size
        total += size
        if size > MAX_IMAGE or total > MAX_TOTAL:
            raise ValueError('Evidence exceeds 5 MB per image or 50 MB total')
        raw = candidate.read_bytes()
        if len(raw) < 33 or raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[8:16] != b'\x00\x00\x00\rIHDR':
            raise ValueError('Frame is missing a PNG IHDR header')
        width, height = struct.unpack('>II', raw[16:24])
        if width < 1 or height < 1 or width * height > MAX_PIXELS:
            raise ValueError('Frame dimensions exceed 16 million pixels or are empty')
        for key, actual in [('width', width), ('height', height)]:
            if key in item and (type(item[key]) is not int or item[key] != actual):
                raise ValueError('Frame dimensions disagree with PNG: ' + name)
        images.append({'name': name, 'width': width, 'height': height,
                       'data': 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')})
    return report, images


def render_gallery(report, images):
    # The only data insertion is JSON in an inert element, with HTML delimiters escaped.
    payload = json.dumps({'report': report, 'images': images}, ensure_ascii=True, separators=(',', ':'))
    payload = payload.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return TEMPLATE.replace('__EVIDENCE_PAYLOAD__', payload)


def export_gallery(directory, output):
    from analysis_reports import write_new
    report, images = load_evidence(directory)
    write_new(output, render_gallery(report, images))
    return {'output': str(output), 'frames': len(images), 'checks': len(report['checks']),
            'report_passed': report['passed'], 'engine_started': False,
            'limits': ['PNG headers checked; full decoding and visual correctness require review.',
                       'Displays recorded evidence; not a new engine run or physical input verification.']}


TEMPLATE = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'nonce-gdw-offline-view'; base-uri 'none'; form-action 'none'">
<title>GameDev Workbench · 画面证据</title>
<style>
:root{color-scheme:dark;--ink:#e4ecee;--muted:#a8b8c1;--bg:#101c28;--panel:#192b38;--line:#3d5663;--teal:#75d6cc;--amber:#ffd28b;--red:#ffaaa0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 'Segoe UI','Microsoft YaHei',sans-serif}
header,main,footer{max-width:1440px;margin:auto;padding:24px 32px}header{border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:24px}h1{font-size:clamp(26px,3vw,40px);line-height:1.15;margin:8px 0}h2{font-size:22px;margin:0 0 14px}p{max-width:75ch;margin:8px 0;color:var(--muted)}button,select{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:8px 12px}button{cursor:pointer}button:disabled{opacity:.45;cursor:default}button:hover:not(:disabled){border-color:var(--teal)}:focus-visible{outline:3px solid var(--amber);outline-offset:3px}label{display:grid;gap:6px}select{max-width:100%;min-width:0}.status{color:var(--teal);font-weight:600}.status.fail{color:var(--red)}.scope{padding:12px 0 22px;border-bottom:1px solid var(--line)}.toolbar{display:flex;align-items:end;gap:16px;flex-wrap:wrap;margin:22px 0}.toolbar p{margin-left:auto}.compare{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px}.pane{min-width:0}.frame-control{display:grid;grid-template-columns:1fr auto auto;gap:8px;align-items:end}.screen{margin:12px 0 0;min-height:240px;display:flex;align-items:center;justify-content:center;background:#07111b;border:1px solid var(--line);border-radius:5px;overflow:hidden}.screen img{width:100%;height:clamp(240px,38vw,540px);object-fit:contain;display:block}.caption{color:var(--muted);font-size:14px;overflow-wrap:anywhere;margin:8px 0 24px}.evidence{display:grid;grid-template-columns:1fr 2fr;gap:32px;margin-top:24px;border-top:1px solid var(--line);padding-top:24px}.toggle{display:flex;gap:8px;align-items:center}.checks{max-height:390px;overflow:auto;margin:0;padding-left:24px}.checks li{padding:5px 8px;border-bottom:1px solid #263e4d;overflow-wrap:anywhere}.checks li::marker{color:var(--teal)}.checks li.failed{color:var(--red)}.diagnostics{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px;color:var(--amber)}footer{border-top:1px solid var(--line);font-size:14px;color:var(--muted)}.empty{padding:32px;color:var(--muted)}
.screen img[hidden]{display:none}
@media(max-width:760px){header,main,footer{padding:20px}header{align-items:start;flex-direction:column}.compare,.evidence{grid-template-columns:1fr}.toolbar p{margin-left:0}.screen img{height:340px}.frame-control{grid-template-columns:minmax(0,1fr) auto auto}}
</style></head><body>
<header><div><div>GameDev Workbench</div><h1>把检查结果，放回画面中看。</h1><p>同一份报告，两个观察位置。图片保留原始字节，可按视口与时间点逐帧对照。</p></div><button id="download">下载报告 JSON</button></header>
<main><section class="scope"><strong id="status" class="status"></strong><p id="summary"></p><p>这是已保存的样例记录。本页不运行引擎；合成输入、OS 自动化与真人操作需要分别验收。检查数量不代表游戏质量或性能。</p></section>
<div class="toolbar"><label>筛选视口<select id="viewport"><option value="all">全部视口</option></select></label><p id="count" aria-live="polite"></p></div>
<div class="compare" id="comparison"></div>
<section class="evidence"><div><h2>检查明细</h2><label class="toggle"><input id="failed" type="checkbox">只看未通过的检查</label><p id="checkCount" aria-live="polite"></p><h2 style="margin-top:24px">环境与诊断</h2><div id="diagnostics" class="diagnostics"></div></div><ol id="checks" class="checks"></ol></section>
</main><footer>离线文件 · 无外部脚本、字体或网络请求 · PNG 头部与路径经过预检；完整解码及视觉正确性仍需人工查看。</footer>
<script type="application/json" id="evidence">__EVIDENCE_PAYLOAD__</script>
<script nonce="gdw-offline-view">
'use strict';
const {report,images}=JSON.parse(document.getElementById('evidence').textContent);
const el=id=>document.getElementById(id), make=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
el('status').textContent=report.passed?'报告记录：通过':'报告记录：未通过';el('status').classList.toggle('fail',!report.passed);
el('summary').textContent=`${report.checks.filter(c=>c.passed).length} / ${report.checks.length} 项检查通过；${images.length} 张原始截图。${report.engine_version||'未记录引擎版本'}`;
el('diagnostics').textContent=JSON.stringify({input:report.input??'未记录',performance:report.performance??'未记录',exit_code:report.exit_code??'未记录',diagnostics:report.diagnostics??[]},null,2);
const dimensions=[...new Set(images.map(f=>`${f.width}×${f.height}`))];for(const d of dimensions){const option=make('option',d);option.value=d;el('viewport').append(option);}
let filtered=images;const panes=[];
for(let i=0;i<2;i++){
 const pane=make('section');pane.className='pane';const label=make('label',i===0?'观察位置 A':'观察位置 B');
 const controls=make('div');controls.className='frame-control';const select=make('select');select.setAttribute('aria-label',`观察位置 ${i===0?'A':'B'} 的截图`);label.append(select);controls.append(label);
 const prev=make('button','上一张'),next=make('button','下一张');controls.append(prev,next);const figure=make('div');figure.className='screen';const img=make('img');figure.append(img);const caption=make('p');caption.className='caption';
 pane.append(controls,figure,caption);el('comparison').append(pane);
 const show=()=>{const f=filtered[Number(select.value)];if(!f){img.hidden=true;img.removeAttribute('src');caption.textContent='此报告没有截图。可先查看检查明细，或用 --graphical 重新运行样例。';prev.disabled=next.disabled=true;return;}img.hidden=false;img.src=f.data;img.alt=f.name;caption.textContent=`${f.name} · ${f.width} × ${f.height}`;prev.disabled=Number(select.value)===0;next.disabled=Number(select.value)===filtered.length-1;};
 select.addEventListener('change',show);prev.addEventListener('click',()=>{select.value=String(Number(select.value)-1);show();});next.addEventListener('click',()=>{select.value=String(Number(select.value)+1);show();});panes.push({select,show});
}
function filter(){const value=el('viewport').value;filtered=images.filter(f=>value==='all'||`${f.width}×${f.height}`===value);el('count').textContent=`当前可查看 ${filtered.length} 张截图；两侧可独立切换。`;panes.forEach((p,i)=>{p.select.replaceChildren();filtered.forEach((f,n)=>{const o=make('option',f.name);o.value=String(n);p.select.append(o);});p.select.disabled=!filtered.length;p.select.value=String(i===0?0:Math.min(1,filtered.length-1));p.show();});}
el('viewport').addEventListener('change',filter);filter();
function checks(){const list=report.checks.filter(c=>!el('failed').checked||!c.passed);el('checks').replaceChildren();for(const c of list){const li=make('li',`${c.passed?'通过':'未通过'} · ${c.name}`);li.classList.toggle('failed',!c.passed);el('checks').append(li);}el('checkCount').textContent=list.length?`显示 ${list.length} 项`:'此筛选下没有检查项。';}
el('failed').addEventListener('change',checks);checks();
el('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(report,null,2)+'\n'],{type:'application/json'}));const a=make('a');a.href=url;a.download='report.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
</script></body></html>
'''
