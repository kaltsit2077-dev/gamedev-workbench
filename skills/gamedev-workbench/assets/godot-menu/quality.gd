extends SceneTree
const Menu = preload("res://menu.gd")
var checks: Array[Dictionary] = []
var frames: Array[Dictionary] = []

func _initialize() -> void:
	call_deferred("run_checks")

func expect(condition: bool, name: String) -> void:
	checks.append({"name": name, "passed": condition})

func key(code: Key) -> void:
	for down: bool in [true, false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.physical_keycode = code
		event.pressed = down
		root.push_input(event)
		await process_frame

func click(control: Control) -> void:
	for down: bool in [true, false]:
		var event := InputEventMouseButton.new()
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = down
		event.position = control.get_global_rect().get_center()
		event.global_position = event.position
		root.push_input(event)
		await process_frame

func joy(button: JoyButton) -> void:
	for down: bool in [true, false]:
		var event := InputEventJoypadButton.new()
		event.button_index = button
		event.pressed = down
		event.pressure = 1.0 if down else 0.0
		root.push_input(event)
		await process_frame

func capture_frame(path: String, filename: String, enabled: bool) -> void:
	if not enabled:
		return
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	expect(image.save_png(path.get_base_dir().path_join(filename)) == OK, "capture " + filename)
	frames.append({"image": filename, "width": image.get_width(), "height": image.get_height()})

func run_checks() -> void:
	var args := OS.get_cmdline_user_args()
	if args.is_empty():
		quit(2)
		return
	var path: String = args[0]
	var graphical: bool = args.size() > 1 and args[1] == "capture"
	root.size = Vector2i(1100, 780)
	var scene = Menu.new()
	root.add_child(scene)
	await process_frame
	await process_frame
	expect(scene.begin_button.has_focus(), "main initial focus")
	await key(KEY_TAB)
	expect(scene.options_button.has_focus(), "typed Tab reaches options")
	await key(KEY_ENTER)
	expect(scene.stack.size() == 2 and scene.font_slider.has_focus(), "typed Enter opens options and focuses slider")
	await click(scene.reset_button)
	expect(scene.stack.size() == 3 and scene.cancel_button.has_focus(), "typed mouse opens nested confirmation")
	await key(KEY_ESCAPE)
	expect(scene.stack.size() == 2 and scene.reset_button.has_focus(), "cancel restores settings focus")
	await key(KEY_ESCAPE)
	expect(scene.stack.size() == 1 and scene.options_button.has_focus(), "back restores original main focus")
	scene.begin_button.grab_focus()
	await joy(JOY_BUTTON_DPAD_DOWN)
	expect(scene.options_button.has_focus(), "synthetic gamepad down navigates")
	await joy(JOY_BUTTON_A)
	expect(scene.stack.size() == 2, "synthetic gamepad accept opens options")
	await joy(JOY_BUTTON_B)
	expect(scene.stack.size() == 1 and scene.options_button.has_focus(), "synthetic gamepad cancel restores focus")
	var nodes_before: int = scene.get_child_count()
	for iteration: int in range(100):
		scene.open_settings()
		scene.open_confirmation()
		scene.pop_screen()
		scene.pop_screen()
	expect(scene.stack.size() == 1 and scene.get_child_count() == nodes_before, "100 nested menu cycles preserve stack and nodes")
	scene.impact.trigger()
	scene.impact.advance(0.4)
	scene.impact.trigger()
	expect(is_zero_approx(scene.impact.elapsed), "layered impact restarts single clock")
	var clock: float = scene.impact.elapsed
	paused = true
	await process_frame
	await process_frame
	expect(is_equal_approx(clock, scene.impact.elapsed), "pause freezes all shader and spark progress")
	paused = false
	scene.impact.advance(2.0)
	expect(not scene.impact.active and not scene.impact.visible and not scene.impact.is_processing(), "impact ends hidden and idle")
	var effect_nodes: int = scene.impact.get_child_count()
	for iteration: int in range(1000):
		scene.impact.trigger()
		scene.impact.advance(2.0)
	expect(scene.impact.get_child_count() == effect_nodes, "1000 impact cycles do not allocate persistent nodes")
	for dimensions: Vector2i in [Vector2i(640,360),Vector2i(960,540),Vector2i(1280,720),Vector2i(800,600),Vector2i(360,640)]:
		root.size = dimensions
		scene.open_settings()
		for font: int in [20,30]:
			scene.model.set_font_size(font)
			await process_frame
			await process_frame
			scene.settings_scroll.scroll_vertical = 0
			var bounds: Rect2 = scene.settings_scroll.get_global_rect()
			expect(bounds.position.x >= 0 and bounds.position.y >= 0 and bounds.end.x <= dimensions.x + 1 and bounds.end.y <= dimensions.y + 1, "scroll viewport fits %s text %d" % [str(dimensions), font])
			expect(scene.long_text.size.x <= scene.settings_scroll.size.x + 1, "long text wraps within width %s text %d" % [str(dimensions), font])
			expect(scene.long_text.size.y > scene.settings_scroll.size.y, "long text is scrollable %s text %d" % [str(dimensions), font])
			var back: Rect2 = scene.back_button.get_global_rect()
			expect(back.end.y <= dimensions.y + 1 and back.end.x <= dimensions.x + 1, "return stays on screen %s text %d" % [str(dimensions), font])
			await capture_frame(path, "menu_%dx%d_text%d.png" % [dimensions.x, dimensions.y, font], graphical)
			scene.settings_scroll.scroll_vertical = roundi(scene.long_text.position.y)
			await process_frame
			await process_frame
			expect(scene.settings_scroll.scroll_vertical > 0, "content scrolls to reading position %s text %d" % [str(dimensions), font])
			expect(scene.long_text.get_global_rect().intersects(scene.settings_scroll.get_global_rect()), "long paragraph visible after scrolling %s text %d" % [str(dimensions), font])
			await capture_frame(path, "menu_%dx%d_text%d_reading.png" % [dimensions.x, dimensions.y, font], graphical)
		scene.model.reset()
		scene.pop_screen()
		scene.main_scroll.ensure_control_visible(scene.effect_area)
		await process_frame
		await process_frame
		expect(scene.main_scroll.get_global_rect().has_point(scene.effect_area.get_global_rect().get_center()), "effect center visible %s" % str(dimensions))
		for moment: float in [0.05,0.25,0.6,1.3]:
			scene.impact.trigger()
			scene.impact.set_process(false)
			scene.impact.advance(moment)
			await capture_frame(path, "impact_%dx%d_%03d.png" % [dimensions.x, dimensions.y, int(moment * 100)], graphical)
	scene.model.set_reduced_motion(true)
	scene.impact.trigger()
	expect(scene.impact.reduced_motion, "reduced-motion preference reaches effect")
	scene.queue_free()
	await process_frame
	await process_frame
	expect(not is_instance_valid(scene), "scene cleanup releases menu and effect")
	var failures := checks.filter(func(item: Dictionary) -> bool: return not item.passed)
	var report := {"passed": failures.is_empty(), "checks": checks, "frames": frames,
		"case": "menu and layered impact", "input": "typed synthetic key/mouse/gamepad events, not hardware verification",
		"rendering": "captured" if graphical else "not-run", "performance": "not-measured"}
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		quit(3)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print("WORKBENCH_QUALITY: ", "PASS" if failures.is_empty() else "FAIL")
	quit(0 if failures.is_empty() else 1)
