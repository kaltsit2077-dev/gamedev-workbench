# 执行工具的使用与边界

## 只读工程分析

```text
python tools/gdw.py analyze-project "Godot项目目录" --output "分析.json"
```

读取 project.godot、GDScript 与文本场景/资源，收集入口、autoload、资源引用、可检测循环、成员声明和状态赋值线索。默认排除隐藏目录、缓存、测试、插件、符号链接和越出项目根的解析路径。可用 --include-tests / --include-addons 扩大范围，--max-files 限制扫描。

报告包含快照时间、源文件 hash、实际扫描范围、跳过原因及动态引用。赋值线索保留文件/方法/目标，并标注未解析接收者或局部遮蔽；不能把同名 position 判断成同一变量，也不能从未发现引用推导“没有依赖”。没有调用引擎、执行脚本、写游戏文件或生成游戏文档。

已用于当前私有工程的只读扫描，完整报告留在发布项目之外。公开示例仅为 [自有样例分析](sample-analysis.json)。不要未经脱敏公开自己的工程报告。

## 阅读稿与架构变化

```text
python tools/gdw.py report-analysis "分析.json" --output "新的阅读稿.md" --max-rows 40
python tools/gdw.py compare-analysis "之前.json" "之后.json" --output "新的变化.json"
```

只读已有分析 JSON，不执行引擎，也不修改原报告。输出采用独占创建，拒绝覆盖。阅读稿限制每张表的行数，转义不可信名称；完整线索仍在 JSON。对比按文件 hash、资源边、autoload、循环和写入的文件/方法/目标/操作匹配，单纯移动行号不算新增。

调用者确认两个快照属于同一工程。scope_comparable 为 false 时增删只是暂定差异；即使为 true 也不是语义回归证明，循环基于扫描器发现的线索，属性同名或新增写入不能证明状态冲突。

## UI 与效果验证

```text
python tools/gdw.py check-ui-effects --engine "官方Godot路径" --scratch "可写缓存" --output-dir "新的证据目录"
python tools/gdw.py check-ui-effects --engine "官方Godot路径" --scratch "可写缓存" --output-dir "另一个新证据目录" --graphical
```

先核验 Godot 4.7.2 官方版；在临时副本运行本工作台的自有样例，用户数据和日志隔离。默认 headless：检查边界、焦点链、注入的 Tab/反向 Tab/Accept，以及重播、暂停、结束隐藏和停止处理。graphical 使用真实 OpenGL 后端，短暂显示窗口，额外捕获五种视口、四个时刻的 PNG。输出目录不覆盖已有证据。

自有样例通过不等于用户游戏通过。将 `skills/gamedev-workbench/assets/godot-demo/validation_probe.gd` 复制到授权的测试夹具后，可以复用：

- control_bounds：对明确选中的控件检查可见范围，不擅自把装饰或滚动内容越界当缺陷。
- focus_chain：检查预期焦点控件集合是否可达。
- send_action：向 Viewport 注入引擎动作。它不证明物理键盘、手柄、触摸或系统窗口焦点行为。

将 quality.gd 的场景实例换成自己的夹具，并显式绑定效果触发/推进/清理接口，才可用于具体界面或效果。本版没有自动扫描并运行任意用户场景，避免误启动写档和自动加载副作用。

## 0.5 专项工具与新案例

完整输入格式与命令见 [工具配方](../skills/gamedev-workbench/references/tool-recipes.md)。新增 --case menu、manual-input、check-narrative、simulate-economy、audit-assets、summarize-evals、verify-editor-case。新菜单证据为 [121 项/40 帧](quality-v05/report.json)，人工输入单列 [当前状态](manual-input-v05.json)。Unity/Unreal 的 [运行状态](unity-case-v05.json) 为 [blocked](unreal-case-v05.json)，符合本机未安装事实。

[20 项分析标注回归](analysis-labels-v05.json)相对于公开 0.4 源码快照从 12/20 到 20/20；该集合随实现建立，不是独立留出集。新工具折叠的是有限静态表达式，不会执行任意动态代码；源 UID 也不等同于引擎缓存结果。

## 0.6 离线画面浏览

```text
python tools/gdw.py gallery docs/quality-v05 --output "新的画面浏览.html"
```

将 report.json 与原始 PNG 变成自包含 HTML，可按视口筛选、双画面选帧、查看失败项和下载原报告。使用已经存在的记录，不产生新的引擎测试。限额与预检边界见 [配方](../skills/gamedev-workbench/references/tool-recipes.md) 的「离线画面浏览」。完整使用路径见 [快速上手](QUICKSTART.md)。发行附件另提供可直接双击的样例 HTML。

## MCP 接入条件

本轮只读分析、场景副本运行、截图和合成输入均可由文件与 CLI 完成，没有出现必须连接编辑器 MCP 的缺口，因此没有自动安装或连接。

需要读取正在运行的远程场景树、在编辑器中选择/修改对象并撤回、检查运行时 Inspector 或持续交互调参时，再对目录内 Godot 桥做同一任务比较。比较必须覆盖读取、编辑、撤回、运行、停止和权限/版本，不能只看工具数量。

Unity/Unreal 已提供原创案例与显式运行入口；本机未安装，尚无真实运行证据。取得环境后逐项运行，不借 Godot 或模拟单测结果背书。

Windows 窗口 OS 自动交互记录见 os-input-v05.json：已走 Tab/Enter/Right/Escape 和鼠标路径，operator_completed=false；它不替代实体输入验收。
