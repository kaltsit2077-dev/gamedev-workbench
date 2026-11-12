# 专项工具配方

以下从安装后的技能根目录执行；完整项目可将 python scripts/workbench.py 换成 python tools/gdw.py。JSON 输出中保留失败与未知，--output 采用独占创建，不覆盖原报告。

## 工程解析

analyze-project 在文本场景/资源头、.uid 旁车与 .import 的 remap 节建立源 UID 索引，读取范围与普通扫描一致且单独有界。冲突/未知 UID 不猜测；UID 与备用路径不一致会记录，备用路径缺失而存在 UID 候选不直接当确定断链。没有加载 .godot 缓存或调用引擎 ResourceUID，因此源映射不等于引擎实际结果。UID 原理参见 [Godot ResourceUID](https://docs.godotengine.org/en/stable/classes/class_resourceuid.html)。

仅折叠单行的字面量、模块常量、字符串相加和简单 %s/%d 替换。参数/局部变量遮蔽、运行时值、方法调用和其他语法保留未知；不执行 eval 或游戏脚本。显式 self 写入与未解析接收者继续分开，不能把同名属性认定为竞争写者。

## 菜单、分层效果与实体输入

```text
python scripts/workbench.py check-ui-effects --case menu --engine "Godot官方路径" --scratch "引擎可写缓存" --output-dir "新的证据目录" --graphical
python scripts/workbench.py manual-input --engine "Godot官方路径" --scratch "引擎可写缓存" --output-dir "引擎可写的新人工证据目录"
```

menu 是可操作的原创终端菜单：嵌套确认/返回栈、长文本滚动、20..30 字号、焦点恢复、减少运动选项，效果由同一个时钟驱动 Shader 双环/闪光与绘制火花。默认 basic 案例保持兼容。graphical 在五视口、两个字号和四个效果时刻采样；不是性能压测。

自动检查使用有类型的合成键盘/鼠标/手柄事件。manual-input 不发自动 OS 输入，打开最长 30 分钟的窗口，记录相关按键与鼠标事件计数及菜单行为，不记录任意输入文字。操作者需要打开 Options、改变字号、用 Escape 返回、用鼠标重播效果并点击 Finish。窗口事件不能独立证明实体来源，需结合操作者确认；未完成不能改成通过。未连接实体手柄不等于手柄已验证。窗口不在前台时先将它激活，勿用机器人输入充当人工验收。需要 OS 自动化时显式加 --mode os-automation，结果会保留 operator_completed=false，与人工会话分开。

## 离线画面浏览

```text
python scripts/workbench.py gallery "上一步的UI证据目录" --output "新的画面浏览.html"
```

双击 HTML 即可离线查看，不需要引擎、Python 服务或网络。可按视口筛选，在 A/B 两侧独立逐张比较，查看失败检查及下载原始报告 JSON。直接嵌入原 PNG 字节，不修图；不把旧截图计作新渲染，也不把帧采样当作视频。无截图的 headless 报告会保留检查明细和空态。

输入限 report.json 4 MB、5000 项检查、200 帧，每帧 5 MB / 1600 万像素、合计 50 MB；仅检查 PNG 头部尺寸，不替代完整解码。拒绝越根/网络路径、符号链接、尺寸不符、失败检查却声明通过的报告，且不覆盖已有输出。报告可能带有项目文件名，分享前自行检查内容。

## 叙事状态图

```text
python scripts/workbench.py check-narrative assets/design/narrative.json --output "新的剧情检查.json"
```

JSON 声明 start、最多 12 个布尔 flags、最多 256 个 nodes。节点 id 唯一；choices 中 to 指向目标，require 是当前布尔条件，set 是选中后的赋值；ending=true 节点没有出边。按「节点+变量状态」探索，检查断链、软锁、无法到达任何结局的状态；循环有出口时允许。不可达节点单列，不自动认定为写作错误。最多 50000 个状态，达到预算则 complete=false，不声称已经穷举。只覆盖此有限模型，不解析自然语言、脚本条件、整数资源或叙事质量。

## 整数经济模拟

```text
python scripts/workbench.py simulate-economy assets/design/economy.json --output "新的经济模拟.json"
```

steps 为 1..10000，initial_currency/base_income 为非负整数。upgrades 声明 id、正整数 cost、income_bonus、max_level、price_growth_percent。每步先按当前等级结算收入，再买一项最便宜的可负担升级，同价按 id；升级后价格按百分比递增并向上取整。income_scale_percent 提供不同收入假设，收入逐步向下取整。输出首购时刻、等级、收支守恒、购买轨迹（最多 200 条）。这不是玩家预测、自动平衡或收益承诺；改变策略需要独立实现与验证。

## 资产依赖预检

```text
python scripts/workbench.py audit-assets assets/design --manifest assets/design/assets.json --output "新的资产预检.json"
```

只读取清单明确列出的本地路径（最多 1000 项，每项至多 50 MB）。检查文件/根边界/符号链接、内容 hash、重复内容与许可声明；PNG 可带 expected_size=[宽,高] 检查头部尺寸；glTF/GLB 检查 JSON、头部和外部 images/buffers 依赖，拒绝越根或外部 URI，不联网下载。其他格式只核对文件与声明。没有证明图片可完整解码、模型可导入、材质正确或许可真实有效。

## 评估与实际费用记录

```text
python scripts/workbench.py summarize-evals "实际记录.json" --output "新的评估汇总.json"
```

records 每项包含 run_id、task、repetition、arm（a/b）、model_configuration、passed、elapsed_seconds、rework_rounds（可为 null）。usage.source 区分 unavailable、estimate、provider_record；实际记录可带 input_tokens、output_tokens、cost_usd 和可追溯 reference。reference 用可公开的记录标识，不放令牌或账号。估算不计入实际费用总额，任一费用缺失则总额为 null，不能用墙钟或文件字数估算 token。

模型配置不同/未声明或缺一组时不组成配对；结果是描述统计，不是因果或显著提效证据。工具不连接账单 API，也不能独立验证调用者提供的发票。完整项目另提供 tools/repeated_eval.py，准备一致输入、核验冻结的任务/验收 hash、在临时副本验收真实产物；需要另用宿主派发独立代理。

## Unity / Unreal 原创编辑器案例

```text
python scripts/workbench.py verify-editor-case unity --editor "Unity编辑器路径" --expect 6000.3 --scratch "可写缓存" --output-dir "新的Unity证据"
python scripts/workbench.py verify-editor-case unreal --editor "UnrealEditor-Cmd路径" --expect 5.6 --scratch "可写缓存" --output-dir "新的Unreal证据"
```

示例版本是声明目标，不是本机成功记录；按实际准备的版本明确指定 --expect。Unity 原创 Editor C# 检查状态通知与 GameObject 创建/变换/清理；Unreal 原创 Python 检查临时世界与 Actor 生命周期。后者只在独立样例项目启用引擎内置 Python 插件，不是运行时玩法语言。相关官方入口：[Unity 命令行](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html)、[Unreal 编辑器 Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)。

运行器复制本包案例，不启动用户项目；编辑器仍使用其正常用户环境与已有许可。没有二进制则 blocked，不安装编辑器或激活许可；有二进制时必须同时满足报告、非空检查、版本、标记和退出码。单元测试中的模拟只验证运行器失败处理，不能计为引擎执行。需要编辑器选取/Inspector/撤回等实际操作缺口后，再比较 MCP。

## 0.7 创作工作区与任务工作页

```text
python scripts/workbench.py create-workspace assets/design/brief.json --output "新的创作工作区"
python scripts/workbench.py check-workspace "新的创作工作区" --output "新的结构检查.json"
python scripts/workbench.py workspace-page "新的创作工作区" --output "新的工作页.html"
```

brief 字段固定为 schema_version=1、title、engine、audience、experience、mechanics、art_direction、features；engine 为 godot/unity/unreal/web/blender。文字字段非空且不超过 4000 字，mechanics/features 各 1..30 条、每条至多 1000 字。创建拒绝覆盖，且不运行模型、引擎或上游安装器。

工作区包含 brief.json、workspace.json 和 design/art/ui/assets/delivery 的可编辑文件。workspace 声明需求 ID、任务依赖与输出路径；初始任务全部 draft，初始需求连接属于规划，需审查后细化。UI 的 requirement 列表与 UI 任务保持一致。check-workspace 检查任务 DAG、路径、产物、需求一致性及有限叙事/经济/资产模型；通过仍是设计草案。示例数据与 SVG 为原创起点，须替换或审查，许可证随包复制。

工作页不联网，展示阶段、需求、文件内容与快照 hash，可下载带选中任务/关联需求/产物的 JSON。交给当前宿主助手继续工作时，还需读取真实项目规则；下载任务包不授予发布或安装权限。本页只读，不提供独立聊天后台。预览文本每项 64 KB、总量 500 KB，输出拒绝覆盖；编辑源文件后重新导出。

## 项目声明的测试计划

测试配置是 JSON，示意如下。sources 的 null 仅可用于待冻结草案，执行计划需要真实 hash：

```json
{
  "schema_version": 1,
  "engine": "godot",
  "expected_version": "4.7.2",
  "sources": {"tests/settings_probe.gd": null},
  "tests": [{
    "id": "settings",
    "argv": ["{engine}", "--headless", "--path", "{project}", "--script", "res://tests/settings_probe.gd"],
    "cwd": ".",
    "timeout_seconds": 60,
    "effects": "说明会写入的缓存、存档或其他文件；预先遵守项目约束。",
    "required_checks": ["settings behavior"]
  }]
}
```

```text
python scripts/workbench.py freeze-project-tests "项目目录" --config "测试草案.json" --output "新的冻结计划.json"
python scripts/workbench.py project-tests "项目目录" --config "新的冻结计划.json" --engine "编辑器路径"
python scripts/workbench.py project-tests "项目目录" --config "新的冻结计划.json" --engine "编辑器路径" --execute --output-dir "项目之外的新证据目录"
```

冻结只读取明确选中的源码，预览不执行。执行器使用 argv 列表，不隐式调用 shell；占位符为 {engine}/{project}/{output}/{python}。显式选择的项目代码在正常用户环境运行，**不会自动隔离或复制真实项目**；先核对副作用及项目关于编辑器/并发缓存的约定，需要副本时先建立副本。1..20 项测试、每项 1..300 秒；最多 200 个选中源文件、每个 5 MB。源 hash 按 CRLF/LF 规范化，变动后须新建快照；未选中的文件不在该检查范围。

测试通过环境变量 GDW_TEST_REPORT 得到本项专用 native.json 目标，写入原生证据：

```json
{"engine":"godot","engine_version":"4.7.2.stable.official.ed1daf0bf","passed":true,"checks":[{"name":"settings behavior","passed":true}]}
```

执行器同时要求退出 0、引擎标识、版本前缀、非空/唯一的检查、required_checks 完整且全部布尔通过；缺证据、空检查、超时或声明矛盾均失败。选中源码执行后变化也会判失败。run.json 保留原生报告、每项时长、失败原因与源码指纹；它不能独立证明测试本身完整或诚实，更不代表渲染/输入/性能通过。读取日志与证据有界，但本执行器不是完整进程资源/权限隔离器。

完整项目的 assets/project-tests.json 配合 godot-demo 原创副本可复现该流程。建议将测试入口与项目回归一起版本化。

## 五类后端入口与共同报告

```text
python scripts/workbench.py capabilities
python scripts/workbench.py run-adapter-case godot --editor "官方Godot路径" --expect 4.7.2 --scratch "引擎可写缓存" --output-dir "新证据目录"
python scripts/workbench.py run-adapter-case web --editor "Node可执行文件" --expect "本机实际版本前缀" --scratch "可写缓存" --output-dir "新的JS证据"
python scripts/workbench.py run-adapter-case blender --editor "Blender可执行文件" --expect "明确版本前缀" --scratch "可写缓存" --output-dir "新的Blender证据"
```

Unity/Unreal 采用同一入口各自指定 kind、编辑器与期望版本。共同报告 schema_version=1、kind=execution-report，status 为 passed/failed/blocked，保留 native 与各验证维度。缺少可执行文件会写 blocked 报告，不自动安装。

Godot 在副本跑菜单 headless；Unity/Unreal 沿用各自原创编辑器案例；Web 案例只在 Node 中验证状态事件/取消订阅与重置，不能充当浏览器 UI 验证；Blender 案例准备后台创建/变换/对象与 mesh 清理，尚无真实运行记录。没有新增 MCP 连接。

官方参考：[Godot CLI](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)、[Unity CLI](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html)、[Unreal Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)、[Node EventTarget](https://nodejs.org/api/events.html#class-eventtarget)、[Blender CLI](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)。文档来源不等于本机引擎成功运行。

## Git 协作现场：只读

需要 PATH 中的 Git；选择仓库根，不是子目录。从技能根执行：

```text
python scripts/workbench.py review-git "仓库根目录" --output "仓库外的新报告.json"
python scripts/workbench.py review-git "仓库根目录" --base "本地基准引用" --max-paths 2000 --output "新的集成检查.json"
```

默认最多检查 2000 个变更路径（可设 1..10000），已识别文本类型每文件最多 1 MB；Git 命令超时 20 秒、输出上限 5 MB，跟踪路径上限 100000。超限/缺失基准/读不到 HEAD 或历史图保留不完整或错误，不假装通过。--base 比较该本地提交与当前工作树，省略时只看索引/工作树改动；从不联网更新引用。

报告含 head、branch、upstream、local_divergence（仅本地引用）、operations、changes、unmerged_paths、findings、warnings 和 scan_complete。assessment 为 blocked-by-unmerged-index / requires-review / partial / no-listed-issues；最后一种只表示本工具列出的检查没发现问题。完整三段冲突标记只作 possible 提示，示例文本也可能触发。元数据提示只覆盖所观察到的移动/删除和跟踪路径，不是资源引用全扫描或语义冲突证明。

禁用可选索引锁写入、fsmonitor、配置过滤器、外部 diff 和 textconv；不检查子模块内部，不运行 hook、不 fetch/暂存/合并/提交。过滤器禁用时，过滤资源的差异解释可能不同。路径按 UTF-8 解码（无效字节替代）；文件和 HEAD 在扫描中仍可能被其他进程改变，报告不是原子快照。将完整报告留在私有工程，公开证据只包含经核对的脱敏摘要。

CLI 检出未解决索引返回 2；其他完整报告返回 0（包括 review/partial），参数/执行错误返回 2。返回 0 不等于可安全合并，应检查报告字段并遵守项目流程。

## 模块依赖边界：check-boundaries

项目已明确模块归属与方向后，把相关决策对应为规则。已有规则能复用就沿用，不额外复制架构说明。先对准备检查的实际树重新扫描，再检查该快照：

```text
python scripts/workbench.py analyze-project "Godot项目" --output "新的分析.json"
python scripts/workbench.py check-boundaries "新的分析.json" --rules "项目模块规则.json" --output "新的边界报告.json"
```

规则例（路径相对于被分析的游戏根，而非规则文件；按真实项目调整）：

```json
{"schema_version":1,"modules":[
  {"id":"ui","paths":["scripts/ui/","scenes/ui/"],"allow":["state"]},
  {"id":"state","paths":["scripts/state/"],"allow":[]}
]}
```

同模块引用隐式允许；跨模块只允许 allow 列出的 ID。paths 是大小写敏感的精确文件或以 / 结尾的目录，不展开 glob；禁止绝对路径、反斜杠、父级穿越、空段/点段、重叠选择器与未知 ID。最多 64 模块 / 512 选择器。工具只读 JSON，不读当前源码、不执行引擎或联网。

状态为 no-observed-violations / violations / partial。只有已观察范围无违规、且未留下本检查已知未知项时 CLI 返回 0；其余返回 2。coverage 独立保留不完整状态，有确定违规时不会被其他未知覆盖。报告给出来源/目标/模块、引用类型、快照时间、规范化 JSON 输入 hash 和扫描范围；行号只表示该快照位置。

检查 load/preload/extends/ext-resource/uid-resolution 的已解析引用。普通路径字符串仅为 weak-reference，不直接判违规；动态/未知 UID、失效路径、未归属/未观察模块和扫描警告保留 partial。入口/autoload 注册、运行时调用、信号/注入依赖、状态写者以及完整语义图不在本检查范围。扫描器排除范围仍生效；旧快照符合规则不代表当前树符合。

分析 JSON 上限 20 MB、规则 2 MB；最多 30000 个扫描文件、100000 条资源引用，各不确定性列表最多 100000 项。JSON 指纹采用排序键/紧凑 UTF-8 序列化；不是 Git 提交或当前文件新鲜度证明。输出拒绝覆盖。

包内 assets/dependency-rules.json 对应既有 assets/godot-demo。完整项目可用 `python tools/evaluate_boundaries.py --output 新记录.json` 复现五个有限回归：原案例、反向引用、动态加载、普通字符串、未知 UID。它不运行引擎或模型，不证明全工程准确率或技能提效。
