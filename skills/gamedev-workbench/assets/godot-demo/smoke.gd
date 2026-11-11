extends SceneTree
const State = preload("res://state.gd")
const Pulse = preload("res://pulse.gd")
const Demo = preload("res://demo.gd")
var errors: Array[String] = []

func expect(condition: bool, message: String) -> void:
	if not condition:
		errors.append(message)

func _initialize() -> void:
	call_deferred("run_checks")

func run_checks() -> void:
	var model = State.new()
	model.trigger()
	expect(model.charge == 1, "model trigger")
	model.reset()
	expect(model.charge == 0, "model reset")
	var effect = Pulse.new()
	effect.trigger()
	effect.advance(0.35)
	expect(effect.active, "effect halfway")
	effect.trigger()
	expect(is_zero_approx(effect.elapsed), "retrigger restarts clock")
	effect.advance(0.8)
	expect(not effect.active, "effect terminates")
	effect.free()
	var scene = Demo.new()
	root.add_child(scene)
	await process_frame
	scene.trigger_button.pressed.emit()
	expect(scene.model.charge == 1, "UI command reaches model")
	expect(scene.status.text.contains("1 / 5"), "model reaches UI")
	scene.queue_free()
	await process_frame
	for message in errors:
		push_error(message)
	print("WORKBENCH_SMOKE: ", "PASS" if errors.is_empty() else "FAIL")
	quit(0 if errors.is_empty() else 1)
