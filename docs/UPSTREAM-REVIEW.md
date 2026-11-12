# GitHub 上游研究与本轮落地

日期：2026-11-12。检索实际维护源，选择与当前开发问题相关的 AI 工程方法、Godot 架构/测试和已发布游戏。不是全网完整排名。Stars、许可元数据、归档状态、固定 commit、实际读取文件/范围见 [原始记录](upstream-review-v09.json)。Stars 只帮助发现，不能证明适用性或收益。

| 固定来源 | 目录 ID | 借鉴 | 没有直接照搬的部分 |
|---|---|---|---|
| [github/spec-kit](https://github.com/github/spec-kit/tree/979b0a3c1277283371c9901ad0eed04b64a99997) | S10 | 借鉴按用户可用切片组织任务和独立验收。 | 不照搬全量规格目录或每项必经阶段；上游模板中的测试可选不覆盖本项目回归约定。 |
| [obra/superpowers](https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7) | S11 | 借鉴正常实现对照、跨边界取证与单假设验证。 | 不整体复制提示词、强制门或宿主钩子；本项目已有同类步骤，主要补具体取证顺序。 |
| [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done/tree/bdcaab2c752d9a33a1a1ca9acf3a3c81fb991815) | 归档迁移记录 | 旧高星仓库 README 明确迁至 open-gsd/gsd-core。 | 归档项目保留迁移证据，不作为当前安装目标。 |
| [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core/tree/4226711512fb4035fcbb7d17ae64ac5419d8396a) | S12 | 借鉴可落盘的决定、计划和未完成验收，恢复时回读实际产物。 | 不照搬新目录、自动多代理或上下文容量承诺；复用项目现有载体。 |
| [htdt/godogen](https://github.com/htdt/godogen/tree/40542b6c8efbdc40112c2b004fbaa6d67141846d) | S13 | 借鉴按引擎薄适配，以及运行产物而非仅编译的验证原则。 | 未安装其工具、资产服务或 API；不采用清空目标目录的发布方式。 |
| [abmarnie/godot-architecture-organization-advice](https://github.com/abmarnie/godot-architecture-organization-advice/tree/7afa7b12049beb5adb68d61136191721730545a3) | K16 | 借鉴外部依赖显式注入、资源归属和按项目规模取舍。 | 不强推 src 目录、继承层数、静态状态或自动清理缓存。 |
| [Anuken/Mindustry](https://github.com/Anuken/Mindustry/tree/1a22b880576d2f8f97550280f76bfdd0d0069543) | K17 | 借鉴范围明确、行为改变后在游戏中验证、避免无价值大清理。 | GPL-3.0 源码未复制；其上游禁止 AI 生成贡献，本轮不向其提交或发消息。 |
| [yairm210/Unciv](https://github.com/yairm210/Unciv/tree/6ace04816af9f577db2e493f14947404210ad034) | K18 | 借鉴游戏状态、规则定义、UI 与派生缓存的区分；恢复时重建运行关联。 | 文档不等于源码全审或在本地运行；不复制其类图、代码或游戏规则。 |
| [derkork/godot-statecharts](https://github.com/derkork/godot-statecharts/tree/76d226a3efac66a72aea825382b320c94808f409) | T11 | 借鉴离开状态取消待执行切换的针对性回归。 | 未安装或验证该插件；具体测试仅作参考，不默认给项目换状态机框架。 |
| [godot-gdunit-labs/gdUnit4](https://github.com/godot-gdunit-labs/gdUnit4/tree/674a5a0e0065e641d289fffa4e4350a47be57705) | T12 | 将原生场景行为、清理与参数化测试作为需要时可选工具。 | 维护组织已变化；README 未逐项确认项目所用补丁版本，兼容性与真实运行仍须验证。 |

## 本轮落地

- planning、bugfix、architecture、feature、validation 和 research 工作流补充独立可玩切片、正常路径对照、存档事实/派生数据分离、退出后旧异步结果的取消/拒收。既有项目规则优先，不增加每次任务的固定文档门。
- 原创 check-boundaries 将项目选定的依赖方向变为可执行复查，消费既有 Godot 分析快照。它是本项目对原则的具体实现，不是上游提供或背书的同名工具。
- 新增可独立安装的目录来源；全部上游维持 not-run，未安装框架、调用付费资产 API、复制上游提示词/源码或提交上游贡献。

## 直接验证结果

[五个有限工具回归](boundaries-v09.json)：既有原创样例符合所选规则；新增 state → presentation 反向引用产生一项违规；动态 load、普通路径字符串、未知 UID 分别保留 partial，字符串不会被当作确定违规。执行未修改样例源文件；没有运行引擎或模型。

这不是留出准确率、真实中型项目评估或新的 AI 生产力实验。现有 0.8 两组模型任务结论不变：都通过，尚未证明技能提效。模块检查不覆盖 runtime、信号/注入依赖、状态单写者、入口/autoload 注册或当前树新鲜度。用法和输入限制见 [配方](../skills/gamedev-workbench/references/tool-recipes.md)。

## 后续怎样继续研究

由真实缺陷或下一项工程变化提出问题，优先查项目已有实现，再选少量原始来源。每项候选都记录现有覆盖、采纳或搁置原因、许可与版本、预期失败反例；能落地的改成工具/短流程，跑反例和相关回归。没有具体缺口时保持候选，不为了增加集成数量安装。真实编辑器与宿主适配、长期团队收益分别取得证据。

原始记录保留范围与固定链接；元数据是查阅时快照，并非持续在线状态。没有创建定时任务或后台自动升级。
