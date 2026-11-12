extends RefCounted
var source
var opened: bool = false
var update_count: int = 0
var last_snapshot: Dictionary = {}

func open(next_source) -> void:
	if not _is_valid_source(next_source):
		return
	if opened and source == next_source:
		return
	var values = next_source.snapshot()
	if not (values is Dictionary):
		return
	close()
	source = next_source
	opened = true
	source.changed.connect(_on_changed)
	_on_changed(values)

func close() -> void:
	if _is_valid_source(source) and source.changed.is_connected(_on_changed):
		source.changed.disconnect(_on_changed)
	opened = false
	source = null

func _is_valid_source(candidate) -> bool:
	return typeof(candidate) == TYPE_OBJECT and is_instance_valid(candidate) \
		and candidate.has_signal("changed") and candidate.has_method("snapshot")

func _on_changed(values: Dictionary) -> void:
	if not opened:
		return
	last_snapshot = values.duplicate(true)
	update_count += 1
