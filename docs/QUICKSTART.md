# 从查看证据到用于自己的项目

需要 Python 3.11+。以下在完整项目根目录执行，无第三方 Python 包、API key 或 MCP 依赖。单独技能包将 `python tools/gdw.py` 替换为 `python scripts/workbench.py`，并按技能目录调整 assets 路径。

## 先在现有工程使用技能

安装后直接描述当前任务，不必创建网页或工作区：

```text
$gamedev-workbench 接手这个游戏，先读已有规则和决策，再检查整体模块、状态归属和近期功能的实现顺序。
$gamedev-workbench 修复这个问题：给出可重复的复现，验证根因，最小修复并运行相关回归。
$gamedev-workbench 集成这两个分支，保留双方功能和资源元数据，解决冲突后在集成树上验证；遵守本项目的提交/推送约定。
```

新项目先做整体规划和最近可运行切片；已有项目优先沿用既有模块、票据和测试。局部修改无需完整设计文档。规划、修复、协作方法由 AI 执行，不是输入一句命令就自动合并或修好所有问题。

只读检查多人协作现场，需要本机 Git：

```text
python tools/gdw.py review-git "仓库根目录" --base "本地基准提交或分支" --output git-review.json
```

--base 可省略。报告包含本地分支/跟踪引用、已有操作、未解决索引、变更和有限资源线索；不 fetch、不暂存、不改文件。远端引用可能旧，未发现列出的问题不表示语义合并正确。完整边界见 [工具配方](../skills/gamedev-workbench/references/tool-recipes.md)。

## 先看已有真实证据

发行页的 `gamedev-workbench-gallery-0.10.0-preview.html` 可直接下载后双击。也可从克隆生成：

```text
python tools/gdw.py validate
python tools/gdw.py gallery docs/quality-v05 --output menu-gallery.html
```

页面可筛选五种视口，在 A/B 两侧独立选择截图，比较字号/滚动位置/效果时间点，查看失败项并下载原报告。无截图的 headless 报告仍可查看检查。浏览器不联网、不运行引擎，不新增测试记录。请用新输出文件名，避免覆盖现有证据。

## 给代理安装方法和工具

```text
python tools/gdw.py install-plan --dest "客户端的skills目录"
python tools/gdw.py install --dest "客户端的skills目录"
```

先核对计划中的目标目录；安装只复制 `gamedev-workbench`，拒绝覆盖已有安装。更新前备份旧目录或换新目标；卸载时删除该目标目录。客户端重新发现技能后，明确提出任务，例如：

```text
$gamedev-workbench 审查当前项目整体代码架构。先读约束，确认状态归属与接口，再列出最小迁移步骤和验证方法。
$gamedev-workbench 实现原生设置菜单，覆盖大字号、窄屏、键盘导航和返回焦点。
```

技能让代理按需读取工作流与模板；不会给代理额外授权，不自动安装其他工具。`brief` 可以整理当前任务的资料入口：

```text
python tools/gdw.py brief "制作设置菜单和命中反馈" --engine godot --project "你的游戏目录"
python tools/gdw.py search "架构"
python tools/gdw.py search --category mcp
```

search 检索随包的来源快照，不是实时网页搜索；上游资源仍需复核版本、许可与兼容性。

## 对自己的 Godot 工程做一次只读审查

```text
python tools/gdw.py analyze-project "你的Godot项目目录" --output before.json
python tools/gdw.py report-analysis before.json --output before.md
```

先阅读报告的范围、warnings、动态引用与未知 UID，再核对关心的源码。分析器不启动引擎，不写源码或 .godot 缓存；默认排除隐藏目录、插件和测试。它是有界文本扫描，不是 AST、完整语义依赖图或状态单写者证明。

已有模块方向约定时，按 [规则配方](../skills/gamedev-workbench/references/tool-recipes.md) 映射本项目路径，再运行：

```text
python tools/gdw.py check-boundaries before.json --rules "本项目模块规则.json" --output boundary-check.json
```

工具复查保存快照的显式引用，不重读当前项目。partial 表示动态、UID、字符串或未覆盖路径仍需核对；旧快照通过不等于当前工程通过。包内规则只适用于包内 demo。

完成项目授权的修改和相关回归后，再取快照：

```text
python tools/gdw.py analyze-project "同一Godot项目目录" --output after.json
python tools/gdw.py compare-analysis before.json after.json --output changes.json
```

比较文件 hash、引用、autoload、循环、赋值和 UID 线索，忽略单纯行号移动；项目或扫描范围不同、不完整时不能直接断定新增问题。报告不替代真实项目测试。

## 重新运行原创 UI / 效果案例

需要官方 Godot 4.7.2；路径填写可执行文件，不是安装目录。

```text
python tools/gdw.py doctor --engine "Godot官方可执行文件路径" --expect 4.7.2 --official
python tools/gdw.py check-ui-effects --case menu --engine "同一路径" --scratch "引擎可写缓存目录" --output-dir "本次新的证据目录" --graphical
python tools/gdw.py gallery "本次新的证据目录" --output "本次新的画面.html"
```

运行器复制包内原创案例到临时目录，不启动用户游戏。输出目录须为空或不存在；scratch 需允许引擎写日志。省略 --graphical 只测 headless。真实项目需要显式接入自己的测试场景；当前没有自动接管或自动通过项目验收的能力。

实体键鼠入口：

```text
python tools/gdw.py manual-input --engine "Godot官方可执行文件路径" --scratch "引擎可写缓存目录" --output-dir "新的人工输入目录"
```

在窗口中打开 Options、改变字号、按 Escape 返回、用鼠标重播两次效果，再点 Finish。记录结合操作者确认才能验收实体来源；OS 自动化须另用 `--mode os-automation`，不能冒充真人通过。当前仓内人工流程仍未通过。

## 无引擎的专项工具

```text
python tools/gdw.py check-narrative skills/gamedev-workbench/assets/design/narrative.json
python tools/gdw.py simulate-economy skills/gamedev-workbench/assets/design/economy.json
python tools/gdw.py audit-assets skills/gamedev-workbench/assets/design --manifest skills/gamedev-workbench/assets/design/assets.json
python tools/gdw.py summarize-evals docs/transactions-results.json
```

分别得到有限布尔剧情状态、固定购买策略的整数经济、资产清单依赖预检与配对汇总；不证明故事好看、数值平衡、资产可成功导入或必然提效。完整输入格式和上限见 [工具配方](../skills/gamedev-workbench/references/tool-recipes.md)。

Unity / Unreal 的独立案例同样由 `verify-editor-case` 显式指定本地编辑器，在副本中运行；未安装时 blocked。先准备环境，不自动下载安装或激活许可。

## 怎么判断是否值得继续用

选一个边界明确的真实任务，固定输入、验收、模型与环境；分别记录有无工具的产物、失败、共同验收后返工、墙钟和可追溯实际用量。`tools/repeated_eval.py` 可准备和验收已冻结的设置事务任务，`summarize-evals` 可汇总记录，但不会自动派发模型或取得账单。费用缺失保留 null；既有小样本没有证明技能提效。

当前证据与使用边界见 [实操案例](CASE-STUDIES.md) 和 [已验证与未验证项](VALIDATION.md)。


## 0.7：从创作工作区继续开发

在 brief 示例里填写自己的目标，然后创建一个新工作区：

```text
python tools/gdw.py create-workspace skills/gamedev-workbench/assets/design/brief.json --output workspaces/my-game
python tools/gdw.py check-workspace workspaces/my-game --output workspaces/my-game-check.json
python tools/gdw.py workspace-page workspaces/my-game --output workspaces/my-game.html
```

双击 HTML，选择阶段和产物。下载当前任务包后可交给当前 AI 助手；它仍需先读真实项目规则，再制作代码/场景/资源。工作区是初始草案，源文件可编辑；页面只读，编辑后重新导出。不要把模板结构检查通过当作游戏实现完成。

接入已有项目回归时，先按 [项目测试配方](../skills/gamedev-workbench/references/tool-recipes.md) 明确命令、源文件、检查名与副作用，再 freeze-project-tests、预览 project-tests，确认范围后显式 --execute。执行不自动复制项目，需临时副本时先建立副本，避免引擎并发写同一缓存。

适配入口可用 capabilities 查看；run-adapter-case 使用明确的编辑器和版本。五个入口的验证深度不相同；无环境保留 blocked。长期产品形态与下一阶段见 [平台设计](PLATFORM.md)。
