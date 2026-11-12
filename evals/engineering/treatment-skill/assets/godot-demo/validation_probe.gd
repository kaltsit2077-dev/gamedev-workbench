extends RefCounted
## Reusable original test helper. Call on explicitly selected controls in your own fixture.

static func control_bounds(controls: Array[Control], dimensions: Vector2) -> Array[Dictionary]:
	var results: Array[Dictionary] = []
	for control: Control in controls:
		var bounds := control.get_global_rect()
		results.append({"node": String(control.name), "class": control.get_class(),
			"x": bounds.position.x, "y": bounds.position.y, "width": bounds.size.x, "height": bounds.size.y,
			"within_viewport": bounds.position.x >= 0 and bounds.position.y >= 0 and bounds.end.x <= dimensions.x + 1 and bounds.end.y <= dimensions.y + 1})
	return results

static func focus_chain(start: Control, expected: Array[Control]) -> Dictionary:
	var visited: Array[Control] = []
	var current := start
	for i in range(expected.size() + 1):
		if current == null or current in visited:
			break
		visited.append(current)
		current = current.find_next_valid_focus()
	var complete: bool = visited.size() == expected.size()
	for control: Control in expected:
		complete = complete and control in visited
	var names: Array[String] = []
	for control: Control in visited:
		names.append(String(control.name))
	return {"visited": names, "complete": complete, "scope": "engine focus links, not physical device input"}

static func send_action(viewport: Viewport, action: StringName) -> void:
	for down: bool in [true, false]:
		var event := InputEventAction.new()
		event.action = action
		event.pressed = down
		viewport.push_input(event)
		await viewport.get_tree().process_frame
