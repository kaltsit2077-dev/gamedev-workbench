# 一个具体的架构/UI/效果交付案例

状态：2026-11-11 已跑通内置 headless 行为和五尺寸/二十帧 UI/效果检查。源码在 ../skills/gamedev-workbench/assets/godot-demo/；运行步骤见 godot/README.md。

需求：玩家通过按钮增加充能，并获得短时视觉反馈；重置与重复触发应行为明确。

最初风险：如果 Label 文本兼作状态存储，UI 与玩法将难以独立测试；若多个 Timer 各自结束同一效果，重播可能被上一轮收尾打断。

这里的选择：state.gd 作为唯一模型写者，trigger/reset 发快照；demo.gd 只负责装配、命令绑定和显示；pulse.gd 独占 elapsed 与 active，重播重置同一时钟。删除组合场景时子节点自动离树。

信息流：按钮 pressed → model.trigger → changed → Label。按钮同时触发独立 pulse；视觉状态不反向修改模型。这样可以单独验证模型和效果时间，再检查原生控件的实际接线。

smoke.gd 检查充能、重置、重播、结束和按钮到显示的绑定。它不能证明画面正确、焦点无障碍、所有分辨率可用或性能达标。后续按 Godot README 的人工操作、动态取证与预算步骤完成验证。

迁移到其他引擎时保持“模型所有权、装配、视图、效果时钟”的职责，再分别使用 Unity 或 Unreal 的原生事件与生命周期，不逐行翻译节点 API。
