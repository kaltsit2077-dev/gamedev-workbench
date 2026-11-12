---
name: gamedev-workbench
description: "Assist AI-driven game development in existing or new projects: project and code architecture, integrated features, team Git collaboration, debugging, native UI/VFX, and game design. Use for small and medium game-project work; follow the project's own contracts and workflow."
license: Apache-2.0
---

# 游戏开发辅助

目标是帮助 AI 连贯地完成游戏开发：理解项目、作出设计选择、实现完整功能、定位问题、协作集成并验证结果。适用于个人和小团队的小型/中型项目；可视化与资料检索按任务需要使用。

## 开始与工作尺度

先读项目 AGENTS.md、代码导航、相关决策、当前任务与回归入口，核对分支/工作树与已有改动。已有规范、授权和设计优先；技能不额外授予提交、推送、安装或外传权限。避免覆盖他人改动。

局部修正沿现有契约直接实现并验证。影响多个系统、存档/资源/生命周期或多人分工时，先明确受影响契约与可运行的拆分步骤。按变化影响选择流程深度，不强制每个任务先写整套设计文档。

## 实现时保持整体一致

- 从一个真实入口追到状态所有者、消费者与销毁，先找现有接缝，再增加代码。目录名、同名属性和扫描线索不能代替运行关系证据。
- 明确本次新增状态、唯一声明/写入者、失败/取消/重入与资源生命周期；避免平行管理器、重复真值源和绕过现有装配的局部特判。抽象和框架需要具体变化压力。
- 交付完整的代码、数据/资源、场景接线与用户反馈。涉及持久化、输入、跨场景状态或异步时，检查相关消费者和失败路径。
- 在实际修改/合并后的树上运行受影响的回归，核对 diff 中确实落盘的内容。分别记录行为、引擎画面、输入、性能和人工试玩；未执行保留未验证。
- 交接更新项目已有记录，保留决定、契约、当前提交/改动归属、失败基线与下一步；恢复任务时用真实工作树复核，避免复制维护多个状态清单。

## 按需加载

- 跨迭代计划、接手项目、多人分工：[项目规划](references/workflows/project-planning.md)。
- 模块、状态归属、依赖与迁移：[架构评审](references/workflows/architecture-review.md)。
- 功能与场景接线：[功能交付](references/workflows/feature-delivery.md)。
- 复现、诊断、回归修复：[Bug 修复](references/workflows/bug-fixing.md)。
- 分支、改动归属、冲突、提交与交接：[Git 协作](references/workflows/git-collaboration.md)。
- 原生菜单/HUD：[游戏 UI](references/workflows/game-ui-delivery.md)。Shader/粒子/反馈：[效果](references/workflows/effects-delivery.md)。
- 创意、机制、类型、受众与关卡：[游戏设计](references/workflows/game-design-lab.md)。剧情：[叙事](references/workflows/narrative-lab.md)。风格/建模/材质/声音：[资产](references/workflows/art-and-assets.md)。
- 试玩、性能与证据：[验证](references/workflows/game-validation.md)。资源研究：[来源核验](references/workflows/resource-research.md)。不确定路径：[导航](references/workflows/gamedev-guide.md)。

只读当前任务需要的引擎说明：[Godot](references/adapters/godot.md)、[Unity](references/adapters/unity.md)、[Unreal](references/adapters/unreal.md)、[Web](references/adapters/web.md)、[Blender](references/adapters/blender.md)。现有项目引擎版本优先于样例默认版本。

## 创意和风格

方向不明时，给出少量实质不同的方案，差异落实到玩家动作、信息组织、交互、视觉语法和反馈，并说明制作/维护取舍。用户已有方向时沿用项目风格；借鉴参考需说明来源和借鉴内容。交付可编辑的目标引擎实现，不把网页草图或概念图当作游戏内结果。

## 可选工具

从技能根执行 `python scripts/workbench.py --help`。按需选择，不为用工具而增加步骤：

- `brief` 整理当前任务入口；`analyze-project` / `report-analysis` / `compare-analysis` 提供有范围与未知项的 Godot 文本线索。
- `review-git` 读取本地 Git 状态、冲突与变更关联线索，不 fetch 或修改仓库。
- `project-tests` 默认预览项目声明的命令，显式 --execute 才运行；遵守项目副作用、并发编辑器及缓存约定。它不会自动隔离项目。
- `check-ui-effects` / `run-adapter-case` 运行包内原创案例，不自动验收用户游戏；`gallery` 只是查看已有画面。
- `check-narrative` / `simulate-economy` / `audit-assets` 覆盖其有限输入模型，不证明写作、平衡或实际导入质量。
- `create-workspace` / `check-workspace` / `workspace-page` 是可选草案组织工具，不强制用于已有工程，也不表示游戏已实现。

详细命令与输入边界见 [工具配方](references/tool-recipes.md)。模板只在项目缺少合适载体且任务确需记录时取用。来源目录是元数据快照，第三方技能/MCP 的存在与其已验证状态分开；不自动安装。输出默认拒绝覆盖。
