extends SceneTree
const Demo = preload("res://demo.gd")

func _initialize() -> void:
	call_deferred("capture")

func capture() -> void:
	var arguments := OS.get_cmdline_user_args()
	if arguments.is_empty():
		push_error("Pass an output PNG path after --")
		quit(2)
		return
	root.size = Vector2i(960, 540)
	var scene = Demo.new()
	root.add_child(scene)
	await process_frame
	scene._trigger()
	scene.pulse.set_process(false)
	scene.pulse.advance(0.25)
	await RenderingServer.frame_post_draw
	var frame := root.get_texture().get_image()
	var result := frame.save_png(arguments[0])
	scene.queue_free()
	await process_frame
	print("WORKBENCH_CAPTURE: ", "PASS" if result == OK else "FAIL")
	quit(0 if result == OK else 1)
