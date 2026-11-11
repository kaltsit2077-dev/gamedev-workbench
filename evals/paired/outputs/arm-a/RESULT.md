# 修复结果

修改限于本组 `state.gd`、`feedback.gd`、`ui.gd`：模型饱和到 5；reset 每次同步发通知；按钮通过模型入口工作；标签通过信号同步并初始化；反馈每次触发重新计时；仅调整控件位置防止重叠。审计及最小决定见 `AUDIT.md`。

自编测试为 `tests/charge_feedback_test.gd`。覆盖初始状态、饱和、同步信号、零值重置、反馈重触发及精确时长边界、原生按钮 pressed 信号连接、外部模型更新、无 UI 帧轮询、控件非零尺寸与几何不重叠、1000 次触发节点数量不增长，以及真实 SceneTree 暂停/恢复。保留原 `advance(delta)` 与唯一 `_process` 推进路径，没有 Timer/Tween。

## 实际运行与限制

共运行 **3 轮 Godot 测试**，没有修改前运行，也没有进行故障注入。生产修复在首轮前完成，此后没有改变生产逻辑。第三轮仅给测试补充一帧布局等待和标签非零尺寸断言。

| 轮次 | 断言与退出码 | 环境结果与证据 |
|---|---|---|
| 1 | `CHECKS: 43; FAILURES: 0`，退出 0 | 引擎不能在 `.codex` 路径创建 userdata 和写日志；仅本次工具输出保存了结果，预期原生日志没有成功写入。 |
| 2 | `CHECKS: 43; FAILURES: 0`，退出 0 | 完整预建 userdata 后目录错误消失，原生日志仍写入失败；控制台已另存 `.run/regression-2.stdout.txt`。 |
| 3 | `CHECKS: 44; FAILURES: 0`，退出 0 | 按协调者统一补充授权，将 APPDATA、LOCALAPPDATA、原生日志改到真实仓库的本组专用忽略缓存 `.cache/gdw-paired-arm-a/`；没有写正式游戏文件。原生日志成功生成并复制到 `.run/regression-3.log`，控制台在 `.run/regression-3.stdout.txt`。 |

三轮均确认引擎为 `4.7.2.stable.official.ed1daf0bf`，且均输出 `Failed to read the root certificate store`。这是运行环境错误；本任务没有联网，测试全部完成，未把整轮运行声称为无错误日志。

未测试：渲染截图/视觉质量、人工或硬件输入、硬件性能、正式游戏集成、真实存档。按钮测试是对原生 Button 的 `pressed` 信号进行程序化发射；布局检查是 headless 几何断言。暂停检查只验证继承暂停时不推进、恢复后推进，不声称测量了真实墙钟精度。节点数量断言也不等于硬件性能测量。

## 实际命令

以下各轮均在本组目录运行，Godot 以 `require_escalated` 正常本机启动。命令中的退出码均来自 `$LASTEXITCODE`。

第一轮：

```powershell
New-Item -ItemType Directory -Force -Path '.run/data' | Out-Null
$env:APPDATA = (Resolve-Path -LiteralPath '.run/data').Path
$env:LOCALAPPDATA = $env:APPDATA
& '<GODOT_4_7_2>' --headless --path '<ARM_WORKSPACE>' --log-file '<ARM_WORKSPACE>/.run/regression-1.log' --script res://tests/charge_feedback_test.gd
exit $LASTEXITCODE
```

第二轮（此前已用 Python 预建同一个 userdata 目录）：

```powershell
New-Item -ItemType Directory -Force -Path '.run/data/Godot/app_userdata/Paired charge feedback task' | Out-Null
New-Item -ItemType File -Force -Path '.run/regression-2.log' | Out-Null
$env:APPDATA = (Resolve-Path -LiteralPath '.run/data').Path
$env:LOCALAPPDATA = $env:APPDATA
& '<GODOT_4_7_2>' --headless --path '<ARM_WORKSPACE>' --log-file '<ARM_WORKSPACE>/.run/regression-2.log' --script res://tests/charge_feedback_test.gd 2>&1 | Tee-Object -FilePath '.run/regression-2.stdout.txt'
exit $LASTEXITCODE
```

第三轮（最终版本复现命令）：

```powershell
New-Item -ItemType Directory -Force -Path '<ARM_SCRATCH>/data' | Out-Null
$env:APPDATA = '<ARM_SCRATCH>/data'
$env:LOCALAPPDATA = $env:APPDATA
& '<GODOT_4_7_2>' --headless --path '<ARM_WORKSPACE>' --log-file '<ARM_SCRATCH>/regression-3.log' --script res://tests/charge_feedback_test.gd 2>&1 | Tee-Object -FilePath '.run/regression-3.stdout.txt'
$testExit = $LASTEXITCODE
Copy-Item -LiteralPath '<ARM_SCRATCH>/regression-3.log' -Destination '.run/regression-3.log'
exit $testExit
```

## 用时

开始 Unix 时间：1794375416.981659；结束 Unix 时间：1794375678.827819；总耗时：261.846 秒。开始与结束均使用 Python time.time 记录，原始记录在 .run/timing-start.json 与 .run/timing-end.json。
