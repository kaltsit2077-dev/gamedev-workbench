# GameDev Workbench

面向个人与小团队的游戏开发工作台：可安装技能 + 离线工具 + 知识导引。优先支持工程架构、原生游戏 UI、功能与视觉效果实现，同时覆盖创意、受众、机制、剧情、美术资产和验证。

**当前版本：0.5.0-preview。** 新增源 UID/有限常量路径解析、可操作的嵌套菜单与分层命中特效、叙事检查、整数经济模拟、资产依赖预检及重复评估汇总。新菜单案例完成五种视口、两种字号、四十帧真实 OpenGL 捕获和一百二十一项检查。新增两轮对照四组均通过，仍未证明技能提效。Unity/Unreal 原创案例和运行入口已准备，本机未安装引擎；实体输入、第三方 MCP 与性能保持单独验收状态。见 [能力矩阵](docs/CAPABILITIES.md)、[验证报告](docs/VALIDATION.md) 与 [对照结果](docs/PAIRED-EVALUATION.md)。

[GitHub](https://github.com/kaltsit2077-dev/gamedev-workbench) · [预览版下载](https://github.com/kaltsit2077-dev/gamedev-workbench/releases) · [后续路线](docs/ROADMAP.md) · [English](README.en.md)

## 立即使用

需要 Python 3.11+，不需要第三方 Python 包或 API key。在项目根目录：

```text
git clone https://github.com/kaltsit2077-dev/gamedev-workbench.git
cd gamedev-workbench
python tools/gdw.py search "架构"
python tools/gdw.py search "粒子"
python tools/gdw.py search --category mcp
python tools/gdw.py inspect T09
python tools/gdw.py route "制作游戏菜单和焦点导航"
python tools/gdw.py brief "制作游戏菜单和焦点导航" --engine godot --project "你的项目目录"
python tools/gdw.py analyze-project "你的Godot项目目录" --output "工程分析.json"
python tools/gdw.py report-analysis "工程分析.json" --output "工程阅读稿.md"
python tools/gdw.py doctor
python tools/gdw.py validate
python -m unittest discover -s tests -v
```

工具输出 JSON；search 是本地快照全文检索，route 是关键词建议，不是完整语义推理。资源来源、许可限制和未验证状态随记录返回。brief 整理工作流、模板、来源和项目规则指针，不自动编写代码。doctor 不扫描磁盘、不导入游戏、不写编辑器缓存；指定 --engine 后只执行该文件的 --version：

```text
python tools/gdw.py doctor --engine "完整引擎可执行文件路径" --expect 4.7.2
```

## 安装技能

一个自包含技能，内部提供十个按需工作模式。完整技能目录为 skills/gamedev-workbench；可单独复制到支持 Agent Skills 的客户端技能目录，或先预览再安装：

```text
python tools/gdw.py install-plan --dest "你的客户端技能目录"
python tools/gdw.py install --dest "你的客户端技能目录"
```

安装只复制此技能，不安装任何上游包、不注册 MCP、不覆盖同名技能。更新时先保留旧版，再自行选择新目标；卸载时移除安装计划中指明的 gamedev-workbench 目录。客户端需要重新发现技能后才可调用；具体刷新方式以客户端为准。

Codex 示例：将 --dest 指向自己的技能目录，之后可用 `$gamedev-workbench` 发起任务。安装前可用 install-plan 检查目标目录。

## 工作方式

| 请求 | 使用模式 | 产物 |
|---|---|---|
| 整体架构怎样安排 | architecture | 状态归属、依赖、契约和迁移 |
| 把功能接入游戏 | feature | 代码/资源/场景与回归 |
| 做 HUD 或菜单 | ui | 原生控件、主题、绑定、导航与画面 |
| 实现 Shader/粒子/反馈 | effects | 源资源、触发、生命周期与预算 |
| 错误/性能/试玩 | validation | 复现、证据与复测 |
| 创意/机制/类型/受众/关卡 | design | 体验目标、原型与验证问题 |
| 剧情/选择/演出 | narrative | 分支、变量与恢复契约 |
| 美术/模型/材质/声音 | art | 风格、资产规格、导入与致谢 |
| 查技能、MCP、开发资料 | research | 来源、许可、版本与试验计划 |
| 不知道从哪开始 | guide | 最小任务路径 |

读取 [技能入口](skills/gamedev-workbench/SKILL.md) 或 [学习导引](skills/gamedev-workbench/references/learning-path.md)。Godot、Unity、Unreal 的适配步骤分别提供；可执行验证按引擎单独登记，不把通用方法可用写成所有引擎已测。

## 实际执行内置样例

```text
python tools/gdw.py verify-godot --engine "你的 Godot 官方版路径" --scratch "引擎可写的临时目录" --output "本次验证.json"
```

默认要求 4.7.2 官方版。先检查版本，再复制自有样例到临时目录执行并清理；不会运行你的游戏。无匹配引擎则报告 blocked。验证通过仅证明样例的 headless 行为，真实输入、画面和性能分别验证。

进一步检查布局、焦点、注入动作、重播/暂停/清理和时间序列画面：

```text
python tools/gdw.py check-ui-effects --engine "你的Godot官方版路径" --scratch "引擎可写临时目录" --output-dir "新的证据目录" --graphical
```

这条命令运行本包自有样例；将测试助手接入自己的场景夹具后，才能验证具体游戏。分析报告是文本线索，不是完整依赖图或自动架构结论。详见 [执行工具与边界](docs/EXECUTION-TOOLS.md)。

改动前后各保存一份分析，可检查结构线索的变化：

```text
python tools/gdw.py compare-analysis "改动前.json" "改动后.json" --output "架构变化.json"
```

它比较文件、引用、autoload、循环和状态写入线索，忽略纯行号变化。扫描范围或完整性不同会标明不可直接比较；新写入线索不是“多个写者冲突”的自动证明。[阅读稿示例](docs/sample-analysis.md)可直接查看输出形式。

完整项目另含 [配对任务与统一验收工具](evals/paired/README.md)，可准备相同任务、保留两组修改、运行共同验收；它不自动调用模型或读取账单。首轮使用 0.2；新增两轮设置事务任务使用 0.4。完整验收在新两轮派发前冻结，仍没有测量新增 0.5 工具的提效幅度。

## 专项工具与新菜单

```text
python tools/gdw.py check-ui-effects --case menu --engine "官方Godot路径" --scratch "可写缓存" --output-dir "新的证据目录" --graphical
python tools/gdw.py check-narrative skills/gamedev-workbench/assets/design/narrative.json
python tools/gdw.py simulate-economy skills/gamedev-workbench/assets/design/economy.json
python tools/gdw.py audit-assets skills/gamedev-workbench/assets/design --manifest skills/gamedev-workbench/assets/design/assets.json
python tools/gdw.py summarize-evals docs/transactions-results.json
```

[输入格式、人工输入窗口与跨引擎案例](skills/gamedev-workbench/references/tool-recipes.md)。[新菜单证据](docs/quality-v05/report.json)覆盖长文本、20/30 字号、嵌套返回焦点、合成键鼠/数字手柄、100 次菜单循环和 1000 次效果复用。实体硬件与合成事件分别登记，预检通过不等于引擎导入或玩法品质通过。

## 示例与当前项目接入

[Godot 小样例](examples/godot/README.md)将模型、原生 UI 和短时效果分离。先在隔离样例运行，之后在你的项目中读取 AGENTS、ADR 与现有回归入口，选一个边界清楚的任务使用。不要把本例脚本直接覆盖项目的正式类型。

本包没有包含私有游戏源码、未公开剧情、账号或第三方美术/书籍正文。第三方工具都只是来源索引，见 [第三方说明](THIRD_PARTY_NOTICES.md)。

## 发布与维护

自有代码、技能、模板和样例采用 Apache-2.0，完整条款见 LICENSE 和 NOTICE。外部网页、工具和素材保留其原有权利。公开发行使用 preview 标识，源码与附件以 GitHub 仓库和 Releases 为准。见 [贡献规则](CONTRIBUTING.md)、[发布流程](docs/RELEASING.md)、[设计](DESIGN.md) 与 [使用与价值评估](docs/USAGE-AND-VALUE.md)。

CI 对 Windows、Linux、macOS 的 Python 3.11/3.14 运行工具测试与发布检查；CI 不运行 Godot、第三方 MCP 或玩家试玩。维护者可用 `python tools/package.py --output-dir dist` 重建完整项目包、单独技能包和 SHA256 校验和。
