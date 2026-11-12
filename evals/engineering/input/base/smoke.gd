extends SceneTree
const State = preload("res://settings_state.gd")
const OptionsPanel = preload("res://settings_panel.gd")
func _initialize() -> void:
	var state = State.new()
	var panel = OptionsPanel.new()
	state.persist_callback = func(_values): return true
	panel.open(state)
	var ok: bool = state.set_font_size(24) and panel.last_snapshot.get("font_size") == 24
	panel.close()
	print("PUBLIC_SMOKE: ", "PASS" if ok else "FAIL")
	quit(0 if ok else 1)
