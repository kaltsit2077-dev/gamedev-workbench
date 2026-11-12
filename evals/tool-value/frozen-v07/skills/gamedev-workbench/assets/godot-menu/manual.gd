extends SceneTree
const Menu = preload("res://menu.gd")
var scene
var report_path: String
var finished: bool = false
var mode: String = "operator"

func _initialize() -> void:
	call_deferred("begin")

func begin() -> void:
	var args := OS.get_cmdline_user_args()
	if args.is_empty():
		quit(2)
		return
	report_path = args[0]
	if args.size() > 1:
		mode = args[1]
	auto_accept_quit = false
	root.size = Vector2i(1100,780)
	root.title = "GameDev Workbench — keyboard / mouse check"
	scene = Menu.new()
	root.add_child(scene)
	scene.audit_changed.connect(save_progress)
	scene.completed.connect(complete)
	root.close_requested.connect(cancel)
	save_progress()
	await create_timer(1800.0).timeout
	if not finished:
		cancel()

func save_progress() -> void:
	var result := {"case": "menu input session", "mode": mode, "session_completed": finished,
		"operator_completed": finished and mode == "operator", "automation_completed": finished and mode == "os-automation",
		"keyboard_events": scene.keyboard_events, "mouse_events": scene.mouse_events,
		"settings_opened": scene.settings_opened, "focus_restored": scene.focus_restored,
		"replayed": scene.replayed, "text_size_changed": scene.text_size_changed,
		"steps_complete": scene.input_steps_complete(), "connected_joypads": Input.get_connected_joypads().size(),
		"hardware_attestation": "operator confirmation required; window events alone do not establish device origin",
		"engine_version": Engine.get_version_info().string}
	var file := FileAccess.open(report_path, FileAccess.WRITE)
	if file != null:
		file.store_string(JSON.stringify(result, "\t"))
		file.close()

func complete() -> void:
	finished = true
	save_progress()
	print("WORKBENCH_MANUAL: COMPLETE")
	quit(0)

func cancel() -> void:
	save_progress()
	print("WORKBENCH_MANUAL: INCOMPLETE")
	quit(2)
