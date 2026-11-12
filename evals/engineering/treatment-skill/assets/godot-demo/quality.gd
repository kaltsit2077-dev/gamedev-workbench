extends SceneTree
const Demo = preload("res://demo.gd")
const Probe = preload("res://validation_probe.gd")
var checks: Array[Dictionary] = []
var frames: Array[Dictionary] = []

func _initialize() -> void:
	call_deferred("run_checks")

func expect(value: bool, name: String) -> void:
	checks.append({"name": name, "passed": value})

func action(name: String) -> void:
	await Probe.send_action(root, name)

func run_checks() -> void:
	var arguments := OS.get_cmdline_user_args()
	if arguments.is_empty():
		quit(2)
		return
	var report_path: String = arguments[0]
	var capture: bool = arguments.size() > 1 and arguments[1] == "capture"
	root.size = Vector2i(960, 540)
	var scene = Demo.new()
	root.add_child(scene)
	await process_frame
	await process_frame
	expect(scene.trigger_button.has_focus(), "initial trigger focus")
	expect(Probe.focus_chain(scene.trigger_button, [scene.trigger_button, scene.reset_button]).complete, "declared focus chain covers both buttons")
	await action("ui_focus_next")
	expect(scene.reset_button.has_focus(), "Tab reaches reset")
	await action("ui_focus_prev")
	expect(scene.trigger_button.has_focus(), "reverse Tab reaches trigger")
	await action("ui_accept")
	expect(scene.model.charge == 1, "injected accept action activates native button")
	expect(scene.status.text.contains("1 / 5"), "native button updates bound label")
	var child_count: int = scene.effect_area.get_child_count()
	scene.pulse.trigger()
	scene.pulse.advance(0.3)
	scene.pulse.trigger()
	expect(is_zero_approx(scene.pulse.elapsed), "retrigger resets clock")
	expect(scene.effect_area.get_child_count() == child_count, "retrigger does not add nodes")
	var paused_at: float = scene.pulse.elapsed
	paused = true
	await process_frame
	await process_frame
	expect(is_equal_approx(scene.pulse.elapsed, paused_at), "scene pause stops inherited effect clock")
	paused = false
	scene.pulse.advance(1.0)
	expect(not scene.pulse.active and not scene.pulse.visible and not scene.pulse.is_processing(), "effect ends hidden and idle")
	for dimensions: Vector2i in [Vector2i(640, 360), Vector2i(960, 540), Vector2i(1280, 720), Vector2i(800, 600), Vector2i(360, 640)]:
		root.size = dimensions
		await process_frame
		await process_frame
		for bounds: Dictionary in Probe.control_bounds([scene.panel, scene.status, scene.trigger_button, scene.reset_button, scene.effect_area], Vector2(dimensions)):
			expect(bounds.within_viewport, "bounds %s %s" % [str(dimensions), bounds["class"]])
		expect(not scene.trigger_button.get_global_rect().intersects(scene.reset_button.get_global_rect()), "buttons separated %s" % str(dimensions))
		for moment: float in [0.0, 0.2, 0.5, 0.8]:
			scene.pulse.trigger()
			scene.pulse.set_process(false)
			scene.pulse.advance(moment)
			var item := {"width": dimensions.x, "height": dimensions.y, "effect_seconds": moment, "effect_active": scene.pulse.active}
			if capture:
				await RenderingServer.frame_post_draw
				var frame := root.get_texture().get_image()
				var filename := "frame_%dx%d_%03d.png" % [dimensions.x, dimensions.y, int(moment * 100)]
				var result := frame.save_png(report_path.get_base_dir().path_join(filename))
				expect(result == OK and frame.get_width() == dimensions.x and frame.get_height() == dimensions.y, "rendered frame " + filename)
				item["image"] = filename
			frames.append(item)
	scene.queue_free()
	await process_frame
	var report := {"checks": checks, "frames": frames, "rendering": "captured" if capture else "not-run", "input": "injected engine actions; no physical device", "performance": "not-measured"}
	var failures := checks.filter(func(check: Dictionary) -> bool: return not check.passed)
	report["passed"] = failures.is_empty()
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	if file == null:
		quit(3)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print("WORKBENCH_QUALITY: ", "PASS" if failures.is_empty() else "FAIL")
	quit(0 if failures.is_empty() else 1)
