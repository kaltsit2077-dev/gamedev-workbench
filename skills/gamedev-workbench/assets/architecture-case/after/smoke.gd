extends SceneTree
const RunScript = preload("res://domain/run_state.gd")
const WidgetScript = preload("res://presentation/widget_state.gd")

func _initialize() -> void:
	var state = RunScript.new()
	var widget = WidgetScript.new()
	var checks: Array = []
	checks.append({"name": "domain initial state", "passed": state.coins == 3})
	widget.bind_state(state)
	checks.append({"name": "view reads injected state", "passed": widget.caption() == "3"})
	state.add_coins(7)
	checks.append({"name": "view reflects current state", "passed": widget.caption() == "10"})
	checks.append({"name": "domain exposes no view API", "passed": not state.has_method("caption")})
	var passed := true
	for check in checks:
		passed = passed and check["passed"]
	var report := {"engine_version": Engine.get_version_info()["string"], "passed": passed, "checks": checks}
	var target := FileAccess.open(OS.get_cmdline_user_args()[0], FileAccess.WRITE)
	if target == null:
		push_error("Could not write case report")
		quit(2)
		return
	target.store_string(JSON.stringify(report))
	target.close()
	widget = null
	state = null
	print("ARCHITECTURE_CASE: ", JSON.stringify(report))
	quit(0 if passed else 1)
