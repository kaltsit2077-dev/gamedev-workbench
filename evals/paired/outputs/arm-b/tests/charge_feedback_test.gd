extends SceneTree

const Model = preload("res://state.gd")
const Feedback = preload("res://feedback.gd")
const View = preload("res://ui.gd")

var checks: int = 0
var failures: Array[String] = []

func _initialize() -> void:
	_run.call_deferred()

func _expect(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		print("FAIL: ", message)

func _test_model() -> void:
	var model = Model.new()
	var values: Array[int] = []
	model.changed.connect(func(value: int): values.append(value))
	_expect(model.charge == 0, "model starts at zero")
	model.trigger()
	_expect(model.charge == 1 and values == [1], "trigger increases by one and notifies")
	for i in range(20):
		model.trigger()
	_expect(model.charge == 5, "trigger saturates at five")
	_expect(values.all(func(value: int): return value <= 5), "notifications never exceed five")
	var before_reset := values.size()
	model.reset()
	_expect(model.charge == 0, "reset restores zero")
	_expect(values.size() == before_reset + 1 and values.back() == 0, "reset notifies immediately")
	model.reset()
	_expect(values.size() == before_reset + 2 and values.back() == 0, "reset at zero still notifies")
	model.trigger()
	_expect(model.charge == 1, "trigger works after reset")
	_expect(Model.new().charge == 0, "model instances do not share charge")

func _test_feedback() -> void:
	var effect = Feedback.new()
	_expect(not effect.active and is_zero_approx(effect.elapsed), "feedback starts inactive")
	effect.advance(1.0)
	_expect(not effect.active and is_zero_approx(effect.elapsed), "inactive advance is inert")
	effect.trigger()
	_expect(effect.active and is_zero_approx(effect.elapsed), "trigger starts feedback")
	effect.advance(0.4)
	effect.trigger()
	_expect(effect.active and is_zero_approx(effect.elapsed), "active trigger restarts elapsed")
	effect.advance(0.4)
	_expect(effect.active, "restarted feedback survives old expiry")
	effect.advance(0.29)
	_expect(effect.active, "restarted feedback is active before 0.7 seconds")
	effect.advance(0.011)
	_expect(not effect.active, "restarted feedback stops after 0.7 seconds")
	effect.trigger()
	effect.advance(Feedback.DURATION)
	_expect(not effect.active, "exact duration stops feedback")
	effect.trigger()
	effect.advance(1.0)
	_expect(not effect.active, "large frame delta stops feedback")
	var stopped_elapsed: float = effect.elapsed
	effect.advance(0.3)
	_expect(effect.elapsed == stopped_elapsed, "finished feedback stays stopped")
	var children := effect.get_child_count()
	for i in range(1000):
		effect.trigger()
		effect.advance(0.01)
	_expect(effect.active and effect.get_child_count() == children, "repeated trigger does not add nodes")
	effect.free()

func _test_view() -> void:
	var view = View.new()
	view.size = Vector2(320, 240)
	root.add_child(view)
	view.set_process(false)
	view.effect.set_process(false)
	_expect(view.status.text == "0", "view initializes without waiting for a frame")
	var values: Array[int] = []
	view.model.changed.connect(func(value: int): values.append(value))
	view.trigger_button.pressed.emit()
	_expect(view.model.charge == 1 and values == [1], "Charge button uses model trigger notifications")
	_expect(view.status.text == "1", "Charge button updates label immediately")
	_expect(view.effect.active, "Charge button starts feedback")
	view.effect.advance(0.4)
	view.trigger_button.pressed.emit()
	_expect(is_zero_approx(view.effect.elapsed), "Charge button restarts feedback")
	for i in range(20):
		view.trigger_button.pressed.emit()
	_expect(view.model.charge == 5 and view.status.text == "5", "Charge button respects saturation")
	view.reset_button.pressed.emit()
	_expect(view.model.charge == 0 and view.status.text == "0", "Reset button updates label without processing")
	var before_reset := values.size()
	view.reset_button.pressed.emit()
	_expect(values.size() == before_reset + 1 and values.back() == 0, "Reset button at zero still notifies")
	view.model.trigger()
	_expect(view.status.text == "1", "external model trigger updates subscribed view immediately")
	view.model.reset()
	_expect(view.status.text == "0", "external model reset updates subscribed view immediately")
	await _test_native_button_input(view)
	await process_frame
	await process_frame
	_expect_controls_separate(view, "320x240")
	view.size = Vector2(1280, 720)
	var enlarged_theme := Theme.new()
	enlarged_theme.default_font_size = 32
	view.theme = enlarged_theme
	await process_frame
	await process_frame
	_expect_controls_separate(view, "1280x720, 32px font")
	var nodes_before := view.get_tree().get_node_count()
	for i in range(1000):
		view.trigger_button.pressed.emit()
	_expect(view.get_tree().get_node_count() == nodes_before, "repeated UI trigger preserves scene node count")
	view.free()

func _test_native_button_input(view: Control) -> void:
	view.trigger_button.grab_focus()
	await process_frame
	await _press_space()
	_expect(view.model.charge == 1 and view.status.text == "1", "native focused Charge handles synthetic keyboard press")
	view.reset_button.grab_focus()
	await process_frame
	await _press_space()
	_expect(view.model.charge == 0 and view.status.text == "0", "native focused Reset handles synthetic keyboard press")

func _press_space() -> void:
	var event := InputEventKey.new()
	event.keycode = KEY_SPACE
	event.physical_keycode = KEY_SPACE
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame
	var release := InputEventKey.new()
	release.keycode = KEY_SPACE
	release.physical_keycode = KEY_SPACE
	release.pressed = false
	Input.parse_input_event(release)
	await process_frame

func _expect_controls_separate(view: Control, context: String) -> void:
	var label_rect: Rect2 = view.status.get_global_rect()
	var trigger_rect: Rect2 = view.trigger_button.get_global_rect()
	var reset_rect: Rect2 = view.reset_button.get_global_rect()
	_expect(not label_rect.intersects(trigger_rect) and not label_rect.intersects(reset_rect) and not trigger_rect.intersects(reset_rect), "controls do not overlap at " + context)
	var bounds := Rect2(Vector2.ZERO, view.size)
	_expect(bounds.encloses(label_rect) and bounds.encloses(trigger_rect) and bounds.encloses(reset_rect), "controls fit at " + context)

func _test_inherited_pause() -> void:
	var parent := Node.new()
	root.add_child(parent)
	var effect = Feedback.new()
	parent.add_child(effect)
	paused = true
	effect.trigger()
	for i in range(3):
		await process_frame
	_expect(not effect.can_process() and is_zero_approx(effect.elapsed), "inherited scene pause freezes feedback clock")
	paused = false
	await process_frame
	await process_frame
	_expect(effect.can_process() and effect.elapsed > 0.0, "feedback clock resumes after unpause")
	parent.free()

func _run() -> void:
	_test_model()
	_test_feedback()
	await _test_view()
	await _test_inherited_pause()
	print("RESULT: ", checks, " checks; ", failures.size(), " failures")
	quit(0 if failures.is_empty() else 1)
