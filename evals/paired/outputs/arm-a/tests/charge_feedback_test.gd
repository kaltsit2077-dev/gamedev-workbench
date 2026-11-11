extends SceneTree

const Model = preload("res://state.gd")
const Feedback = preload("res://feedback.gd")
const UI = preload("res://ui.gd")

var failures: Array[String] = []
var checks: int = 0
var observed: Array[int] = []

func _initialize() -> void:
 call_deferred("_run")

func _expect(condition: bool, message: String) -> void:
 checks += 1
 if not condition:
  failures.append(message)
  printerr("FAIL: ", message)

func _observe(value: int) -> void:
 observed.append(value)

func _run() -> void:
 var model = Model.new()
 model.changed.connect(_observe)
 _expect(model.charge == 0, "model starts at zero")
 model.reset()
 _expect(observed == [0], "reset at zero immediately emits zero")
 for value in range(1, 11):
  model.trigger()
  _expect(model.charge == mini(value, 5), "trigger saturates at five: %d" % value)
  _expect(observed.back() == model.charge, "trigger synchronously notifies views")
 model.reset()
 _expect(model.charge == 0 and observed.back() == 0, "reset clears nonzero state and notifies")

 var feedback = Feedback.new()
 _expect(not feedback.active and feedback.elapsed == 0.0, "feedback starts idle")
 feedback.advance(1.0)
 _expect(feedback.elapsed == 0.0, "idle feedback does not advance")
 feedback.trigger()
 feedback.advance(0.5)
 _expect(feedback.active, "feedback remains active before duration")
 feedback.trigger()
 _expect(feedback.elapsed == 0.0 and feedback.active, "active retrigger restarts duration")
 feedback.advance(0.69)
 _expect(feedback.active, "retrigger grants a full duration")
 feedback.advance(0.02)
 _expect(not feedback.active, "feedback stops after duration")
 feedback.trigger()
 feedback.advance(Feedback.DURATION)
 _expect(not feedback.active, "feedback stops exactly at duration")
 feedback.free()

 var ui = UI.new()
 root.add_child(ui)
 _expect(ui.status.text == "0", "label initializes immediately")
 _expect(not ui.is_processing(), "UI has no per-frame polling")
 await process_frame
 _expect(ui.status.size.x > 0.0 and ui.status.size.y > 0.0, "label geometry is resolved before overlap checks")
 _expect(not ui.trigger_button.get_rect().intersects(ui.reset_button.get_rect()), "buttons do not overlap geometrically")
 _expect(not ui.status.get_rect().intersects(ui.trigger_button.get_rect()), "label and Charge do not overlap geometrically")
 for index in range(9):
  ui.trigger_button.pressed.emit()
 _expect(ui.model.charge == 5 and ui.status.text == "5", "native Charge signal uses saturated model and synchronous view")
 ui.model.reset()
 _expect(ui.status.text == "0", "external model reset immediately updates label")
 ui.trigger_button.pressed.emit()
 ui.reset_button.pressed.emit()
 _expect(ui.model.charge == 0 and ui.status.text == "0", "native Reset signal immediately updates label")
 ui.model.trigger()
 _expect(ui.status.text == "1", "external model trigger immediately updates label")

 var initial_nodes = get_node_count()
 for index in range(1000):
  ui.trigger_button.pressed.emit()
  ui.effect.advance(0.1)
 _expect(get_node_count() == initial_nodes and ui.effect.get_child_count() == 0, "1000 retriggers do not grow the scene tree")
 _expect(ui.effect.active and is_equal_approx(ui.effect.elapsed, 0.1), "each repeated trigger restarts the same feedback instance")
 ui.effect.trigger()
 _expect(ui.effect.process_mode == Node.PROCESS_MODE_INHERIT, "feedback inherits scene processing mode")
 paused = true
 var paused_elapsed: float = ui.effect.elapsed
 for index in range(5):
  await process_frame
 _expect(ui.effect.elapsed == paused_elapsed and ui.effect.active, "paused tree does not advance feedback")
 paused = false
 for index in range(5):
  await process_frame
 _expect(ui.effect.elapsed > paused_elapsed, "unpaused tree resumes its existing process clock")
 ui.free()

 print("CHECKS: %d; FAILURES: %d" % [checks, failures.size()])
 quit(0 if failures.is_empty() else 1)
