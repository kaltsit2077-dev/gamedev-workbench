# 上游做法：采纳与取舍

按当前开发问题选择参考；高星只帮助发现候选。这里链接到本轮实际读过的固定提交，全文与许可仍属于上游；没有安装、运行或复制其代码/提示词。工作流正文是本项目原创的适配。

| 固定来源 | 借鉴点 | 保留的边界 |
|---|---|---|
| [github/spec-kit](https://github.com/github/spec-kit/blob/979b0a3c1277283371c9901ad0eed04b64a99997/templates/tasks-template.md) | 借鉴按用户可用切片组织任务和独立验收。 | 不照搬全量规格目录或每项必经阶段；上游模板中的测试可选不覆盖本项目回归约定。 |
| [obra/superpowers](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/SKILL.md) | 借鉴正常实现对照、跨边界取证与单假设验证。 | 不整体复制提示词、强制门或宿主钩子；本项目已有同类步骤，主要补具体取证顺序。 |
| [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core/blob/4226711512fb4035fcbb7d17ae64ac5419d8396a/README.md) | 借鉴可落盘的决定、计划和未完成验收，恢复时回读实际产物。 | 不照搬新目录、自动多代理或上下文容量承诺；复用项目现有载体。 |
| [htdt/godogen](https://github.com/htdt/godogen/blob/40542b6c8efbdc40112c2b004fbaa6d67141846d/README.md) | 借鉴按引擎薄适配，以及运行产物而非仅编译的验证原则。 | 未安装其工具、资产服务或 API；不采用清空目标目录的发布方式。 |
| [abmarnie/godot-architecture-organization-advice](https://github.com/abmarnie/godot-architecture-organization-advice/blob/7afa7b12049beb5adb68d61136191721730545a3/README.md) | 借鉴外部依赖显式注入、资源归属和按项目规模取舍。 | 不强推 src 目录、继承层数、静态状态或自动清理缓存。 |
| [Anuken/Mindustry](https://github.com/Anuken/Mindustry/blob/1a22b880576d2f8f97550280f76bfdd0d0069543/CONTRIBUTING.md) | 借鉴范围明确、行为改变后在游戏中验证、避免无价值大清理。 | GPL-3.0 源码未复制；其上游禁止 AI 生成贡献，本轮不向其提交或发消息。 |
| [yairm210/Unciv](https://github.com/yairm210/Unciv/blob/6ace04816af9f577db2e493f14947404210ad034/README.md) | 借鉴游戏状态、规则定义、UI 与派生缓存的区分；恢复时重建运行关联。 | 文档不等于源码全审或在本地运行；不复制其类图、代码或游戏规则。 |
| [derkork/godot-statecharts](https://github.com/derkork/godot-statecharts/blob/76d226a3efac66a72aea825382b320c94808f409/README.md) | 借鉴离开状态取消待执行切换的针对性回归。 | 未安装或验证该插件；具体测试仅作参考，不默认给项目换状态机框架。 |
| [godot-gdunit-labs/gdUnit4](https://github.com/godot-gdunit-labs/gdUnit4/blob/674a5a0e0065e641d289fffa4e4350a47be57705/README.md) | 将原生场景行为、清理与参数化测试作为需要时可选工具。 | 维护组织已变化；README 未逐项确认项目所用补丁版本，兼容性与真实运行仍须验证。 |

旧 gsd-build/get-shit-done 已归档，其固定 README 指向新的 open-gsd/gsd-core；后续研究先核对维护来源。静态文档可能过时，测试框架兼容和宿主能力须在选定版本上另验。

本项目将依赖需明确归属与方向的设计原则，原创实现为 check-boundaries；上游没有为本项目验证该检查器。它只对选定快照中的显式 Godot 资源引用取证，不测游戏状态所有权或运行时调用。详细输入边界见 [工具配方](tool-recipes.md)。

更新方式：从真实失败或下一次改动出发，找原始来源 → 固定读取版本与范围 → 核对许可/维护和已有覆盖 → 实现最小有用变化 → 用反例与回归验证。框架/安装只在存在实际缺口且符合项目授权时采用；已有项目规则和决策始终优先。
