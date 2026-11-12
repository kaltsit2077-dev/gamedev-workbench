extends RefCounted
var source
var opened: bool = false
var update_count: int = 0
var last_snapshot: Dictionary = {}

func open(next_source) -> void:
	source = next_source
	opened = true
	var callback := func(values: Dictionary):
		update_count += 1
		last_snapshot = values
	source.changed.connect(callback)
	last_snapshot = source.snapshot()
	update_count += 1

func close() -> void:
	opened = false
