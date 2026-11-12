extends SceneTree
const State = preload("res://settings_state.gd")
const OptionsPanel = preload("res://settings_panel.gd")
const HUD = preload("res://hud.gd")
var checks: Array[Dictionary] = []
var saves: int = 0

func expect(value: bool, name: String) -> void:
	checks.append({"name": name, "passed": value})

func save_ok(_data) -> bool:
	saves += 1
	return true

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var state = State.new()
	state.persist_callback = save_ok
	var hud = HUD.new()
	hud.observe(state)
	var values: Dictionary = state.snapshot()
	expect(values.get("font_size") == 20 and values.get("reduced_motion") == false and values.get("master_volume") == 1.0,
		"both merged defaults survive")
	var ok: bool = state.set_reduced_motion(true) and state.set_master_volume(0.5) and state.set_font_size(24)
	values = state.snapshot()
	expect(ok and values.get("reduced_motion") == true and values.get("master_volume") == 0.5 and values.get("font_size") == 24,
		"all merged setters and unrelated fields")
	var before: Dictionary = state.snapshot().duplicate(true)
	var old_saves: int = saves
	var old_updates: int = hud.updates
	expect(not state.set_font_size(19) and not state.set_master_volume(-0.5) and state.snapshot() == before and saves == old_saves and hud.updates == old_updates,
		"invalid inputs are silent")
	ok = state.set_font_size(24)
	expect(ok and saves == old_saves and hud.updates == old_updates, "unchanged values are silent noops")
	state.persist_callback = func(_data): return false
	ok = state.set_font_size(28)
	expect(not ok and state.snapshot() == before and hud.updates == old_updates, "failed save does not commit or notify")
	state.persist_callback = func(_data): return 1
	ok = state.set_font_size(32)
	expect(not ok and state.snapshot() == before and hud.updates == old_updates, "save success is strictly boolean true")
	state.persist_callback = save_ok
	values = state.snapshot()
	values["font_size"] = 999
	expect(state.snapshot().get("font_size") == 24, "read snapshot cannot mutate state")
	state.persist_callback = func(data):
		data["font_size"] = 999
		return true
	ok = state.set_font_size(28)
	expect(ok and state.snapshot().get("font_size") == 28, "persistence callback cannot mutate committed state")
	state.persist_callback = save_ok
	var panel = OptionsPanel.new()
	panel.open(state)
	var start_updates: int = panel.update_count
	panel.open(state)
	state.set_font_size(32)
	expect(panel.update_count == start_updates + 1 and panel.last_snapshot.get("font_size") == 32, "repeated open keeps one binding")
	panel.close()
	panel.close()
	start_updates = panel.update_count
	old_updates = hud.updates
	state.set_font_size(20)
	expect(panel.update_count == start_updates and hud.updates == old_updates + 1, "close detaches only that panel")
	panel.open(state)
	expect(panel.last_snapshot.get("font_size") == 20, "reopen reads latest state")
	var other = State.new()
	other.persist_callback = save_ok
	panel.open(other)
	start_updates = panel.update_count
	state.set_font_size(24)
	ok = panel.update_count == start_updates
	other.set_font_size(28)
	expect(ok and panel.update_count == start_updates + 1 and panel.last_snapshot.get("font_size") == 28, "switching states removes old binding")
	panel.close()
	for _index: int in range(100):
		panel.open(state)
		panel.close()
	panel.open(state)
	start_updates = panel.update_count
	old_updates = hud.updates
	state.set_font_size(28)
	expect(panel.update_count == start_updates + 1 and hud.updates == old_updates + 1, "100 open-close cycles preserve single updates")
	panel.close()
	var passed: bool = checks.all(func(item): return item.passed)
	var output := {"engine": "godot", "engine_version": Engine.get_version_info().string, "passed": passed, "checks": checks}
	var args := OS.get_cmdline_user_args()
	if not args.is_empty():
		var file := FileAccess.open(args[0], FileAccess.WRITE)
		if file:
			file.store_string(JSON.stringify(output, "  "))
	print("ENGINEERING_GRADE: ", "PASS" if passed else "FAIL")
	quit(0 if passed else 1)
