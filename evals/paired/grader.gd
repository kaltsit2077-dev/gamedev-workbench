extends SceneTree
var checks: Array[Dictionary] = []

func _initialize() -> void:
	call_deferred("run_checks")

func check(value: bool, name: String) -> void:
	checks.append({"name": name, "passed": value})

func descendants(node: Node) -> int:
	var count := node.get_child_count()
	for child: Node in node.get_children():
		count += descendants(child)
	return count

func run_checks() -> void:
	var Model = load("res://state.gd")
	var UI = load("res://ui.gd")
	var model = Model.new()
	check(model.charge == 0, "model starts at zero")
	model.trigger()
	check(model.charge == 1, "model increments")
	for i in 30:
		model.trigger()
	check(model.charge == 5, "model saturates at five")
	var events: Array[int] = []
	model.changed.connect(func(value: int) -> void: events.append(value))
	model.reset()
	check(model.charge == 0 and events == [0], "reset updates state and notifies")
	model.reset()
	check(events == [0, 0], "zero reset still notifies")
	var scene = UI.new()
	root.add_child(scene)
	await process_frame
	for i in 30:
		scene.trigger_button.pressed.emit()
	check(scene.model.charge == 5, "native button obeys model bound")
	scene.reset_button.pressed.emit()
	check(scene.model.charge == 0 and scene.status.text.contains("0"), "reset button immediately updates view")
	scene.model.trigger()
	check(scene.status.text.contains("1"), "model signal updates view without polling frame")
	var count: int = descendants(scene)
	scene.effect.trigger()
	scene.effect.advance(0.4)
	scene.effect.trigger()
	check(is_zero_approx(scene.effect.elapsed), "active feedback restarts")
	scene.effect.advance(0.69)
	check(scene.effect.active, "feedback stays active before duration")
	scene.effect.advance(0.02)
	check(not scene.effect.active, "feedback stops after duration")
	scene.effect.trigger()
	check(scene.effect.active and is_zero_approx(scene.effect.elapsed), "finished feedback is reusable")
	for i in 30:
		scene.effect.trigger()
		scene.effect.advance(0.8)
	check(descendants(scene) == count, "repeated use does not accumulate nodes")
	scene.effect.trigger()
	var before: float = scene.effect.elapsed
	paused = true
	await process_frame
	await process_frame
	check(is_equal_approx(before, scene.effect.elapsed), "scene pause stops feedback clock")
	paused = false
	scene.queue_free()
	await process_frame
	check(not is_instance_valid(scene), "scene cleanup completes")
	var failed := checks.filter(func(item: Dictionary) -> bool: return not item.passed)
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		var file := FileAccess.open(args[0], FileAccess.WRITE)
		if file != null:
			file.store_string(JSON.stringify({"passed": failed.is_empty(), "checks": checks}, "\t"))
			file.close()
	print("PAIRED_GRADER: ", "PASS" if failed.is_empty() else "FAIL")
	quit(0 if failed.is_empty() else 1)
