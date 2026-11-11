"""Create editable, requirement-linked creative packs; check structure, not fun."""
import json
from pathlib import Path
import shutil
from workspace_io import local_path, new_json, read_json

ENGINES = {'godot', 'unity', 'unreal', 'web', 'blender'}


def validate_brief(brief):
    keys = {'schema_version', 'title', 'engine', 'audience', 'experience', 'mechanics', 'art_direction', 'features'}
    if not isinstance(brief, dict) or set(brief) != keys or type(brief['schema_version']) is not int or brief['schema_version'] != 1:
        raise ValueError('Brief requires schema_version=1 and the documented fields only')
    if not isinstance(brief['engine'], str) or brief['engine'] not in ENGINES: raise ValueError('Unknown engine')
    for key in ['title', 'audience', 'experience', 'art_direction']:
        if not isinstance(brief[key], str) or not 1 <= len(brief[key].strip()) <= 4000:
            raise ValueError('Invalid brief '+key)
    for key in ['mechanics', 'features']:
        if not isinstance(brief[key], list) or not 1 <= len(brief[key]) <= 30 or not all(isinstance(x, str) and 0 < len(x.strip()) <= 1000 for x in brief[key]):
            raise ValueError('Invalid brief '+key)


def create_workspace(brief, output):
    validate_brief(brief)
    root = Path(output).absolute()
    if root.exists() or root.is_symlink(): raise ValueError('Workspace output must not exist')
    # Check parent aliases before creating any content.
    if any(p.is_symlink() for p in root.parents): raise ValueError('Workspace parent cannot be symlinked')
    skill = Path(__file__).resolve().parents[1]
    requirements = [{'id': f'req-{i:03}', 'text': text} for i, text in enumerate(brief['features'], 1)]
    ids = [r['id'] for r in requirements]
    stages = [('experience', [], ['design/experience.md']),
              ('mechanics', ['experience'], ['design/mechanics.md', 'design/economy.json']),
              ('narrative', ['mechanics'], ['design/narrative.json']),
              ('art', ['experience'], ['art/direction.md']),
              ('ui', ['mechanics', 'art'], ['ui/spec.json']),
              ('assets', ['art', 'ui'], ['assets/manifest.json', 'assets/signal-mark.svg']),
              ('implementation', ['ui', 'narrative', 'assets'], ['delivery/implementation.md']),
              ('verification', ['implementation'], ['delivery/acceptance.md'])]
    tasks = [{'id': name, 'depends_on': deps, 'requirements': ids, 'outputs': outputs, 'state': 'draft'} for name, deps, outputs in stages]
    manifest = {'schema_version': 1, 'kind': 'creative-workspace', 'title': brief['title'], 'engine': brief['engine'],
                'state': 'draft', 'requirements': requirements, 'tasks': tasks,
                'limits': ['Scaffolded editable design artifacts; no AI service, engine integration or art/model production was executed.',
                           'Requirement links are initial planning coverage, not proof of implementation or human approval.']}
    docs = {
        'README.md': '# '+brief['title']+'\n\n状态：draft。此包是可编辑的设计起点；示例叙事、经济和图标均待替换/审查。\n\n'
                     '修改 brief.json 与各设计文件后，用 check-workspace 检查连接。更新需求时同步工作区中的 requirement 与任务链接；结构通过不表示游戏已实现。\n',
        'design/experience.md': '# 体验目标\n\n受众：'+brief['audience']+'\n\n目标：'+brief['experience']+'\n\n待验证：玩家在何时作出什么选择？怎样观察目标是否成立？\n',
        'design/mechanics.md': '# 机制与原型\n\n'+'\n'.join('- '+x for x in brief['mechanics'])+'\n\n待设计：核心循环、状态所有者、失败恢复、最小可玩切片。economy.json 是示例策略，须按实际游戏替换。\n',
        'art/direction.md': '# 风格与资产方向\n\n'+brief['art_direction']+'\n\n待制作：风格参考（URL/许可/用途）、轮廓与色彩规则、模型/纹理/声音规格、预算、导入验证。现有 SVG 是本工具原创占位资源，不代表最终美术。\n',
        'delivery/implementation.md': '# 引擎实现交接\n\n目标：'+brief['engine']+'\n\n待实现：读取项目约束；确认状态归属、场景装配、输入与存档契约；逐项实现需求；登记实际代码/场景路径和回退方式。\n',
        'delivery/acceptance.md': '# 验收计划\n\n'+'\n'.join('- '+r['id']+'：'+r['text']+'；待补实际断言/画面/人工记录。' for r in requirements)+'\n\n分别记录解析、行为、渲染、输入、性能与试玩；未运行保持 not-run。\n'}
    root.mkdir(parents=True)
    for folder in ['design', 'art', 'ui', 'assets', 'delivery']:
        (root/folder).mkdir()
    for name, content in docs.items():
        target = local_path(root, name); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8', newline='\n')
    new_json(root/'brief.json', brief); new_json(root/'workspace.json', manifest)
    shutil.copyfile(skill/'LICENSE', root/'LICENSE')
    for name in ['narrative.json', 'economy.json']:
        shutil.copyfile(skill/'assets/design'/name, root/'design'/name)
    new_json(root/'ui/spec.json', {'schema_version': 1, 'state': 'draft', 'engine': brief['engine'], 'requirements': ids,
                                 'screens': [{'id': 'main', 'actions': ['start', 'settings', 'return'], 'focus_restore': 'pending'}],
                                 'viewports': [[640, 360], [960, 540], [360, 640]], 'large_text': 'pending', 'implementation': 'not-run'})
    shutil.copyfile(skill/'assets/design/signal-mark.svg', root/'assets/signal-mark.svg')
    asset = read_json(skill/'assets/design/assets.json')['assets'][0]
    new_json(root/'assets/manifest.json', {'assets': [asset]})
    return {'workspace': str(root), 'state': 'draft', 'tasks': len(tasks), 'engine_started': False,
            'next': 'Edit the linked artifacts, review requirements, then check-workspace; no game has been implemented.'}


def check_workspace(directory):
    root = Path(directory).resolve(strict=True)
    data = read_json(local_path(root, 'workspace.json'))
    checks = []
    def check(name, passed): checks.append({'name': name, 'passed': bool(passed)})
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data.get('schema_version') != 1 or data.get('kind') != 'creative-workspace':
        raise ValueError('Unknown workspace format')
    brief = read_json(local_path(root, 'brief.json')); validate_brief(brief)
    check('brief engine agrees with workspace', data.get('engine') == brief['engine'])
    reqs = data.get('requirements'); tasks = data.get('tasks')
    if not isinstance(reqs, list) or not 1 <= len(reqs) <= 30 or not isinstance(tasks, list) or not 1 <= len(tasks) <= 100:
        raise ValueError('Bounded requirements and tasks required')
    if not all(isinstance(r, dict) and isinstance(r.get('id'), str) and 0 < len(r['id']) <= 100 and isinstance(r.get('text'), str) and 0 < len(r['text']) <= 1000 for r in reqs):
        raise ValueError('Invalid requirements')
    req_ids = {r['id'] for r in reqs}; check('unique requirement ids', len(req_ids) == len(reqs))
    check('brief requirements match workspace', [r['text'] for r in reqs] == brief['features'])
    if not all(isinstance(t, dict) and isinstance(t.get('id'), str) and t['id'] for t in tasks):
        raise ValueError('Invalid task records')
    by_id = {t['id']: t for t in tasks}; check('unique task ids', len(by_id) == len(tasks))
    covered = set(); graph = {}
    for task in tasks:
        for field in ['depends_on', 'requirements', 'outputs']:
            if not isinstance(task.get(field), list) or len(task[field]) > 100 or not all(isinstance(x, str) for x in task[field]):
                raise ValueError('Invalid task '+field)
        check(task['id']+': known dependencies', set(task['depends_on']) <= by_id.keys())
        check(task['id']+': valid requirement links', bool(task['requirements']) and set(task['requirements']) <= req_ids)
        covered.update(task['requirements']); graph[task['id']] = task['depends_on']
        check(task['id']+': outputs declared', bool(task['outputs']))
        for name in task['outputs']: check(task['id']+': output '+name, local_path(root, name).is_file())
        check(task['id']+': remains draft until separately verified', task.get('state') == 'draft')
    remaining = set(graph); done = set()
    while remaining:
        ready = {n for n in remaining if set(graph[n]) <= done}
        if not ready: break
        done.update(ready); remaining -= ready
    check('task dependency graph is acyclic and closed', not remaining)
    check('every requirement has a task', covered == req_ids)
    ui = read_json(local_path(root, 'ui/spec.json')) if local_path(root, 'ui/spec.json').is_file() else {}
    check('UI requirements and engine agree', isinstance(ui, dict) and ui.get('engine') == data.get('engine')
          and isinstance(ui.get('requirements'), list) and all(isinstance(x, str) for x in ui['requirements'])
          and set(ui['requirements']) == set(by_id.get('ui', {}).get('requirements', [])))
    from narrative_checks import check_narrative
    from economy_simulation import simulate_economy
    from asset_preflight import audit_assets
    nested = {'narrative': check_narrative(read_json(local_path(root, 'design/narrative.json'))),
              'economy': simulate_economy(read_json(local_path(root, 'design/economy.json'))),
              'assets': audit_assets(local_path(root, 'assets'), read_json(local_path(root, 'assets/manifest.json')))}
    for key, result in nested.items(): check(key+' finite model/preflight', result['passed'])
    return {'schema_version': 1, 'kind': 'workspace-check', 'passed': all(c['passed'] for c in checks),
            'state': 'draft', 'checks': checks, 'specialist_results': nested, 'engine_started': False,
            'limits': ['Structural linkage and finite model checks only; design, UI, art, gameplay and implementation need review.',
                       'Draft artifacts do not become production-ready because this report passed.']}
