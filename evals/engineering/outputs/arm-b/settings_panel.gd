extends RefCounted
var source
var opened: bool = false
var update_count: int = 0
var last_snapshot: Dictionary = {}

func open(next_source) -> void:
	if typeof(next_source) != TYPE_OBJECT or not is_instance_valid(next_source):
		return
	if not next_source.has_signal("changed") or not next_source.has_method("snapshot"):
		return
	if opened and source == next_source:
		return
	var values = next_source.snapshot()
	if not values is Dictionary:
		return
	close()
	source = next_source
	opened = true
	source.changed.connect(_on_changed)
	last_snapshot = values.duplicate(true)
	update_count += 1

func close() -> void:
	opened = false
	if is_instance_valid(source) and source.changed.is_connected(_on_changed):
		source.changed.disconnect(_on_changed)
	source = null

func _on_changed(values: Dictionary) -> void:
	if not opened:
		return
	last_snapshot = values.duplicate(true)
	update_count += 1
