# GameDev Workbench

辅助 AI 开发小型和中型游戏的技能与离线工具。用于理解项目架构、完整实现功能、修复 Bug、多人 Git 集成，以及原生 UI、效果和游戏内容设计。

[下载预览版](https://github.com/kaltsit2077-dev/gamedev-workbench/releases/tag/v0.10.0-preview) · [使用指南](docs/QUICKSTART.md) · [实操案例](docs/CASE-STUDIES.md) · [能力边界](docs/CAPABILITIES.md) · [English](README.en.md)

[![Toolbox checks](https://github.com/kaltsit2077-dev/gamedev-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/kaltsit2077-dev/gamedev-workbench/actions/workflows/ci.yml)

## 能做什么

| 工作 | AI 使用技能完成的内容 | 可运行工具 |
|---|---|---|
| 项目与代码架构 | 读项目约定，追踪入口、职责、状态归属、生命周期和迁移影响 | Godot 只读分析、UID/命名继承线索、快照对比、模块依赖规则检查 |
| 功能实现与 Bug 修复 | 从复现和契约到代码、资源/场景接线、失败/取消/清理，再运行相关回归 | 引擎核验、项目测试预览与显式执行、原生案例 |
| 多人 Git 协作 | 保护已有改动，核对双方意图，解冲突后在集成树上验证 | 本地状态/冲突索引、大小写与 UID/.meta 关联检查 |
| 原生 UI、HUD 和效果 | 布局、主题、长文本、焦点、状态绑定；Shader/VFX 触发、暂停、复用与清理 | 原创 Godot 菜单/效果验证、画面证据浏览器 |
| 玩法、剧情、风格与资产 | 比较机制/交互/视觉方案，形成可编辑规格；沿项目风格制作和接入 | 有限剧情分支检查、整数经济模拟、资产依赖预检 |
| 规划与交接 | 按改动影响拆成可运行步骤，复用已有决策/票据，恢复时核对真实工作树 | 可选任务草案与文件导出 |

技能指导由 AI 执行；Python 工具负责有限范围的检查与证据。它们不会自动接管编辑器、合并分支或制作完整游戏。可视化界面按需使用。

## 实操中确实改变了什么

| 案例 | 原来的情况 | 验证后的结果 |
|---|---|---|
| 现有游戏的架构分析 | 在同一份 497 文件快照中，33 条已核对的命名类继承均未进入旧报告 | 33 条均进入新报告；游戏源码与索引保持不变 |
| 可复现的架构修复 | 游戏状态误继承界面类；旧工具未检出，代码可编译，同一原生验收仅 3/4 | 新工具指出 1 条违规；去掉不当继承后，模块检查无该违规，原生验收 4/4 |
| 原生菜单与效果 | 需要检查长文本、窄屏、返回焦点和重复使用 | 已有五视口、两字号、40 帧和 121 项图形检查记录，含菜单/效果清理 |

[查看代码、命令与原始记录](docs/CASE-STUDIES.md)。第一个结果是已标注正例的识别覆盖；第二个是预设问题的原创演示；第三个是包内案例的既有原生记录。它们不代表全工程准确率、审美评分或已证明节省开发时间/费用。已有模型对照中两组均通过，尚无普遍提效结论。

<details>
<summary>查看已有原生菜单与效果画面</summary>

![原生菜单的大字号与长文本滚动](docs/quality-v05/menu_960x540_text30_reading.png)

![原生分层命中效果](docs/quality-v05/impact_1280x720_060.png)

这些是已有原创案例的原始 OpenGL 截图，不是本次新增画面或同一游戏的审美对照。

</details>

## 怎么使用

本机已安装时，直接描述实际任务：

```text
$gamedev-workbench 审查当前项目架构，核对职责、状态归属和依赖；给出有源码依据的改进，并验证实际修改。
$gamedev-workbench 修复这个 Bug：先复现与验证根因，再最小修改，检查相关消费者和失败路径。
$gamedev-workbench 集成这两个分支，保留双方功能，核对场景与资源，在最终树上回归；遵守本项目的提交和推送约定。
```

完整项目需要 Python 3.11+，Python 工具只用标准库，无 API key。克隆后可先只读检查：

```text
python tools/gdw.py validate
python tools/gdw.py analyze-project "你的Godot工程" --output analysis.json
python tools/gdw.py report-analysis analysis.json --output analysis.md
python tools/gdw.py review-git "仓库根目录" --output git-review.json
```

项目已约定模块方向时，可再运行 `check-boundaries analysis.json --rules "本项目规则.json" --output boundaries.json`。动态引用、歧义与未覆盖部分保留待核对；输出拒绝覆盖，完整格式见 [工具配方](skills/gamedev-workbench/references/tool-recipes.md)。

运行原生架构案例需要官方 Godot 4.7.2，完整项目中执行：

```text
python tools/run_architecture_case.py --engine "Godot可执行文件" --scratch "新的引擎可写副本目录" --output-dir "新的引擎可写证据目录"
```

运行器复制包内 before/after 案例，使用同一套验收；before 的失败是预期证据。它不修改用户游戏。菜单/效果、安装和其他专项工具用法见 [使用指南](docs/QUICKSTART.md)。

## 支持范围

- Godot 有 Windows / 官方 4.7.2 的实际原生案例与画面记录；架构文本工具的跨平台状态见 Actions。
- Unity / Unreal 有工作流、原创案例和运行入口，本机缺少编辑器，实际执行未验证。Web 状态案例跑过 Node，浏览器渲染未验证。
- 完整实体键鼠流程、手柄、真人试玩与性能尚未通过验收；引擎注入和 OS 自动化分别记录。
- 静态扫描不证明运行时依赖或状态单写者；资产预检不代替编辑器导入，剧情/经济检查不证明好玩或平衡。

## 安装与许可

```text
python tools/gdw.py install-plan --dest "客户端技能目录"
python tools/gdw.py install --dest "客户端技能目录"
```

安装复制自包含技能，拒绝覆盖已有安装；发行页同时提供独立技能 ZIP、完整项目 ZIP、可选离线 HTML 与校验值。已有项目规则和权限优先，不自动安装第三方服务。

[验证范围](docs/VALIDATION.md) · [贡献指南](CONTRIBUTING.md) · [变更记录](CHANGELOG.md) · [第三方声明](THIRD_PARTY_NOTICES.md)

原创代码与文档采用 [Apache-2.0](LICENSE)。少量官方 demo 评估源码保留其 MIT 许可；其他外部资料主要保存链接和元数据。公开包不含私有游戏源码或私有完整分析报告。
