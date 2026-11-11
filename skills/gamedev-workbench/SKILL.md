---
name: gamedev-workbench
description: Support independent game development architecture, native game UI, gameplay features, shaders and VFX, design, narrative, assets and validation across Godot, Unity and Unreal. Use for game-project tasks or game-development resource discovery.
license: Apache-2.0
---

# 游戏开发工作台

环境：可读文件的代理；可选离线工具需要 Python 3.11+，运行引擎需要匹配的本地编辑器。阅读方法不需要 MCP 或账号。

先读项目自身 AGENTS.md、代码导航和任务相关决策，再选择工作流。遵守现有接口与用户授权；本技能不授予远端发布、云端上传或额外安装权限。

边界明确的小改动可直接沿现有契约实现与验证；跨模块或状态归属不清时再展开架构材料。只加载会改变当前决策的资源。

## 按任务加载

- 不确定路径：[导航](references/workflows/gamedev-guide.md)。
- 代码工程架构：[架构评审](references/workflows/architecture-review.md)。
- 功能实现：[交付流程](references/workflows/feature-delivery.md)。
- 游戏 HUD、菜单与绘制：[原生 UI](references/workflows/game-ui-delivery.md)。
- Shader、粒子、动效：[效果实现](references/workflows/effects-delivery.md)。
- 调试、回归、性能与试玩：[验证](references/workflows/game-validation.md)。
- 创意、机制、受众与关卡：[设计实验室](references/workflows/game-design-lab.md)。
- 剧情与选择：[叙事实验室](references/workflows/narrative-lab.md)。
- 美术、建模、材质、声音：[美术资产](references/workflows/art-and-assets.md)。
- 技能、工具与资料：[资源研究](references/workflows/resource-research.md)。

按需读 [Godot](references/adapters/godot.md)、[Unity](references/adapters/unity.md)、[Unreal](references/adapters/unreal.md)、[Web](references/adapters/web.md)、[Blender](references/adapters/blender.md)。更广的学习方向见 [开发导引](references/learning-path.md)。模板位于 templates/，只读取当前任务需要的文件。

## 可选本地工具

从本技能目录执行 `python scripts/workbench.py --help`。search/inspect/route/brief/doctor/validate 离线可用。catalog/resources.json 是来源元数据快照，外部能力均未在此包验证。

需要把任务整理成工作资料包时，运行 `python scripts/workbench.py brief "任务" --engine godot`；可加 `--project "项目路径"` 列出已有规则与引擎标记。它只整理入口，不分析完整源码、不自动修改项目、不声称执行完任务。模式与来源映射的声明面为 catalog/modes.json。

需要复现内置样例时，使用 `python scripts/workbench.py verify-godot --engine "引擎路径"`；先核验期望的官方版本，再在临时副本运行 assets/godot-demo/smoke.gd。可用 --scratch 指定引擎可写的临时目录、--output 保存 JSON。它只验证这个自有样例，不运行用户工程；真实渲染、真人输入和性能仍分别取证。

每次交付区分设计、代码、解析、行为、渲染、性能、真人试玩等证据。没有执行的部分保留未验证状态。参考网页和工具声明不是本项目测试结果。

## 工程只读分析与样例验收

- `python scripts/workbench.py analyze-project "Godot 项目目录" --output "报告.json"`：不运行引擎，输出入口、autoload、引用边、循环及状态赋值线索；只读范围与不确定性随报告返回。不是完整语义图，也不生成/改写游戏文档。
- `python scripts/workbench.py check-ui-effects --engine "官方引擎" --scratch "可写缓存" --output-dir "新证据目录" --graphical`：在临时样例副本中检查布局、焦点、注入动作、效果生命周期并捕获时间序列。省略 --graphical 使用 headless，不产画面；输出目录必须为空或不存在。
- `assets/godot-demo/validation_probe.gd` 是可复用的原创测试助手，供授权的场景夹具显式选择控件和注入动作。不会自动接管用户工程。
- `python scripts/workbench.py report-analysis "分析.json" --output "新的阅读稿.md"`：把原始线索整理为有行数上限的 Markdown；保留未知项，不自动下架构结论。
- `python scripts/workbench.py compare-analysis "改动前.json" "改动后.json" --output "新的对比.json"`：比较文件 hash、引用、autoload、循环和写入线索，忽略单纯行号变化。先确认是同一项目；扫描范围不同或不完整时不得把增删直接认定为回归。
- `python scripts/workbench.py gallery "UI证据目录" --output "新的画面浏览.html"`：把 report.json 与原始 PNG 打包为离线双画面浏览器，可筛选视口、逐帧对照、筛选失败项及下载报告。不运行引擎，不产生新的测试证据。

工具通过只背书其报告明确覆盖的维度；其他引擎、真实硬件输入、性能和玩法仍须各自验证。

## 创作工作区与项目执行

- `create-workspace assets/design/brief.json --output "新工作区"`：从明确目标创建体验、机制、剧情、风格、UI、资产、实现交接和验收的可编辑草案，关联需求与任务依赖；不是已经实现的游戏。
- `check-workspace "工作区"` 与 `workspace-page "工作区" --output "新的工作页.html"`：检查连接及有限模型，浏览草案并下载当前任务包。页面是只读快照；由当前宿主助手结合真实项目规则继续执行，没有独立 AI 后台。
- `capabilities`：区分五类后端的具体入口与真实运行要求。`run-adapter-case` 返回共同执行报告；Godot/Unity/Unreal/Web/Blender 各自保留原生证据，缺少环境为 blocked。
- `freeze-project-tests` 对项目明确声明的源文件做快照；`project-tests` 默认只预览结构化命令，`--execute` 才运行。必须先读配置中的副作用、工作目录与验收项；不把用户项目代码当作隔离进程。本技能不扩大宿主授权。

以上省略公共前缀 `python scripts/workbench.py`，完整命令和格式见 [配方](references/tool-recipes.md)。优先按当前任务加载设计产物；不要一次将整个工作区或全部知识库塞入模型。

## 专项执行入口

按需读 [工具配方与输入格式](references/tool-recipes.md)：包括 UID/有限常量解析、`check-ui-effects --case menu`、`manual-input`、`check-narrative`、`simulate-economy`、`audit-assets`、`summarize-evals` 与 `verify-editor-case`。这些工具随技能自包含分发；Unity/Unreal 的源码案例存在不代表已运行，没有编辑器时返回 blocked。
