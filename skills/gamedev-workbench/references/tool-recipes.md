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
