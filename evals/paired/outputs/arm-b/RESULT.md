# 修复结果

## 范围与环境

工作仅位于本组 `arm-b`。正式代码只改 `state.gd`、`feedback.gd`、`ui.gd`，另有自编测试和审查文档。没有改宿主游戏正式文件、安装依赖、网络访问、提交或发布。

引擎版本实际输出：`4.7.2.stable.official.ed1daf0bf`，版本核验命令退出 0。通过 Windows 本机授权启动。

协调方在首次引擎运行前告知：Godot 能读取 `.codex` 中工程，但用户数据/日志应改写到获准的本组宿主缓存。由此所有引擎调用都将 `APPDATA`、`LOCALAPPDATA` 指向 `<ARM_SCRATCH>/data`，日志也写该缓存后复制回本组 `.run`。两处数据目录均已预建。**本组因该环境问题失败或重跑 0 次**；没有先尝试原来的 `.codex` 用户数据路径。除获准缓存外未写宿主游戏。

两次行为运行均输出 `ERROR: Failed to read the root certificate store.`。命令继续完成并给出断言结果；该环境项未修复，也未被算作功能通过证据。

## 最小修改

- `state.gd` 的 `trigger` 统一限幅到 5；`reset` 无条件发 `changed(0)`。
- `ui.gd` 的 Charge 入口调用模型 `trigger`；视图订阅 `changed` 并在装配时同步初值，移除每帧轮询。
- `feedback.gd` 的每次 `trigger` 都重置 `elapsed` 并激活，继续只用现有 `_process → advance(delta)` 推进，保持继承暂停。
- 一个 VBoxContainer 分隔既有标签与两个原生按钮，未引入其他视觉内容。

## 实际轮次与结果

自编测试：`tests/charge_feedback_test.gd`。

| 调用 | 实际结果 | 退出码 | 日志 |
| --- | --- | --- | --- |
| 版本核验 | 官方 4.7.2 | 0 | 本轮命令输出 |
| 第 1 轮，修复前 | 37 checks; 18 failures | 1 | `.run/baseline.log` |
| 第 2 轮，修复后 | 39 checks; 0 failures | 0 | `.run/final.log` |

总计 **2 轮行为测试、1 次版本核验**。第 2 轮在原 37 项断言基础上补充两项原生按钮合成 Space 键输入断言；没有测试脚本解析失败或中间隐藏测试轮次。

覆盖：初值、加一、饱和、通知值上界、重置及零值重复重置通知、模型实例独立；反馈不活动推进、活跃重触发、旧截止点、0.7 秒边界、大步长停止、停止后惰性、1000 次复用；UI 即时初值、模型事件与两按钮接线、外部模型变更、合成键盘输入；320×240 几何、1280×720 加 32px 字体几何；1000 次按钮触发节点数稳定；真实 SceneTree 暂停冻结和恢复自动推进。

## 实际执行命令

工作目录均为：

```text
<ARM_WORKSPACE>
```

版本核验：

```powershell
New-Item -ItemType Directory -Force -Path '.run/data','<ARM_SCRATCH>/data' | Out-Null
$env:APPDATA = '<ARM_SCRATCH>/data'
$env:LOCALAPPDATA = $env:APPDATA
& '<GODOT_4_7_2>' --version
```

第 1 轮（对应修复前代码）：

```powershell
$env:APPDATA = '<ARM_SCRATCH>/data'
$env:LOCALAPPDATA = $env:APPDATA
& '<GODOT_4_7_2>' --headless --path '<ARM_WORKSPACE>' --log-file '<ARM_SCRATCH>/baseline.log' --script 'res://tests/charge_feedback_test.gd'
$test_exit = $LASTEXITCODE
Copy-Item -LiteralPath '<ARM_SCRATCH>/baseline.log' -Destination '.run/baseline.log'
exit $test_exit
```

第 2 轮（当前代码，可复测）：

```powershell
$env:APPDATA = '<ARM_SCRATCH>/data'
$env:LOCALAPPDATA = $env:APPDATA
& '<GODOT_4_7_2>' --headless --path '<ARM_WORKSPACE>' --log-file '<ARM_SCRATCH>/final.log' --script 'res://tests/charge_feedback_test.gd'
$test_exit = $LASTEXITCODE
Copy-Item -LiteralPath '<ARM_SCRATCH>/final.log' -Destination '.run/final.log'
exit $test_exit
```

## 证据边界与未测项

解析和选定行为已通过。几何测试和合成输入在 headless 原生控件中运行，不能证明视觉效果或真人体验。未验证实际渲染、动态画面、GPU/CPU/硬件性能、鼠标点击、触屏、手柄、真人输入、打包导出和主场景启动（原工程没有主场景）。没有新增可视效果或承诺反馈画面；本任务提供的反馈节点仅有时序状态。

## 耗时

起点由第一步 Python `time.time()` 写入 `.run/timing-start.json`，终点由收尾 Python `time.time()` 写入 `.run/timing-end.json`。起止 epoch 与总秒数如下：

- 开始 epoch：`1794375430.256680`
- 结束 epoch：`1794375774.037297`
- 墙钟耗时：**343.781 秒**（约 5.73 分钟，含审查、文档与工具等待）。
