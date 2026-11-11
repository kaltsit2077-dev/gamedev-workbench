# 独立架构、UI、效果样例

唯一源码位于 ../../skills/gamedev-workbench/assets/godot-demo/，随技能安装。使用项目根目录的 verify-godot 命令在临时副本验证，避免写入发布包本身。

2026-11-11：官方基准下 smoke 实际通过；quality 完成五尺寸、二十帧 OpenGL 捕获和六十项检查，见 ../../docs/quality-v03/report.json。完整支持范围见 ../../docs/VALIDATION.md。

本例 state.gd 独占模型状态，demo.gd 组合原生控件与事件，pulse.gd 独占效果时钟。它是最小架构/接线/生命周期样例，不代表最终视觉质量或生产力提升。

要单独打开样例，在上述源码目录使用匹配的 Godot 编辑器。smoke.gd 可 headless 运行；capture.gd 需要真实图形环境，用 `--script res://capture.gd -- <输出PNG路径>` 捕获一帧。没有图形环境时不要运行 capture。

quality.gd 与 validation_probe.gd 验证明确选中控件的边界、焦点链、注入的 Tab/反向 Tab/Accept、重播、暂停及结束隐藏/停止处理。通过 check-ui-effects --graphical 运行时捕获 640×360、960×540、1280×720、800×600、360×640，在效果 0/0.2/0.5/0.8 秒采样。可复用助手的接入方式见 ../../docs/EXECUTION-TOOLS.md。

物理鼠标/键盘/手柄、系统窗口缩放操作、文字扩展、复杂菜单焦点恢复、退出及代表性负载下性能仍需另测；引擎动作注入不能替代真人设备验收。
