extends RefCounted
var updates: int = 0
var last_snapshot: Dictionary = {}
func observe(state) -> void:
	state.changed.connect(_changed)
func _changed(values: Dictionary) -> void:
	updates += 1
	last_snapshot = values.duplicate(true)
