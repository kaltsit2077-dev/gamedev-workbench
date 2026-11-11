# 充能反馈审查

## 问题与变化压力

任务规格为 `REQUIREMENTS.md`。只修现有充能、重置、反馈复用和原生控件接线，保留既有公开字段、信号和方法。

## 现状入口与证据

- `project.godot` 的 `application`：仅项目配置，没有主场景；本组通过测试脚本实例化 `ui.gd` 作为装配入口，不新增主场景。
- `ui.gd` 的 `_ready`：创建 Label、两个 Button 和反馈节点；按钮没有布局，初始文本未同步。
- `ui.gd` 的 `_on_trigger`：直接写 `model.charge`，绕过 `state.gd` 的 `trigger` 与 `changed`。
- `ui.gd` 的 `_process`：每帧读模型刷新标签，导致重置与初始状态都依赖下一帧。
- `state.gd` 的 `trigger`：无上限；`reset`：写零但不发 `changed`。
- `feedback.gd` 的 `trigger`：激活时直接返回，连续触发无法重启时长。

以上为修复前源码锚点；失败断言记录在 `.run/baseline.log`。

## 模块与依赖方向

`Button.pressed → ui.gd → state.gd.trigger/reset → changed → ui.gd.status`

`Charge pressed → ui.gd → feedback.gd.trigger`；`feedback.gd._process → advance(delta)`。

## 状态所有权

| 状态 | 声明者与唯一写者 | 读者 | 生命周期 |
| --- | --- | --- | --- |
| `charge` | `state.gd` 模型的 `trigger/reset` | 标签订阅者、测试 | 每个模型实例 |
| `elapsed/active` | `feedback.gd` 的 `trigger/advance` | 反馈与测试 | 每个反馈实例 |
| `status.text` | `ui.gd` 的初始同步与 `changed` 消费方 | 原生 Label | 每个视图节点 |
| 布局 | 原生 VBoxContainer | Label、Button | 视图子树 |

反馈自动推进唯一入口仍是 `_process → advance(delta)`；不引入 Timer/Tween。节点保持默认继承暂停。测试直接推进时关闭其自动处理，避免测试制造双时钟。视图销毁释放控件和反馈子树，连接到视图方法的信号随对象释放断开。

## 方案与最小决策

1. 保持现状不能满足饱和、即时通知、重触发要求。
2. 采用局部修复：模型统一写充能，重置无条件通知；视图连接 `changed` 并主动同步初值，删除轮询；反馈每次触发重置时间。
3. 不做边界重构、不添加总线、自动加载或新计时器。三个现有脚本足以承担各自责任。
4. 仅用一个 VBoxContainer 分隔标签和按钮，保留原生控件与文字，不增加视觉设计。

## 接口与迁移

保留 `changed(value: int)`、`charge`、`trigger()`、`reset()`、`elapsed`、`active`、`DURATION`、`advance(delta)` 以及现有视图字段。反馈时间从最近一次触发起算；达到时长停止，停止后推进无效。模型饱和时仍发当前值，重置为零时也发通知。

迁移是替换三个脚本的局部实现；回退时还原这些脚本即可，不涉及数据迁移。新增能力仍应从模型方法和信号接入；视图不得直接写充能，外部不得同时手动推进正在自动处理的反馈。

## 验证边界

自编测试覆盖模型行为、按钮信号接线、原生按钮合成键盘输入、即时刷新、时间边界、重复使用、场景节点计数与实际树暂停。几何断言覆盖窄屏及宽屏放大文字；它们不是渲染检查。真实画面、硬件性能与真人操作不在本次验证内。具体命令、轮次、结果见 `RESULT.md`。
