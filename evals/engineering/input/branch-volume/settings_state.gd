extends RefCounted
signal changed(snapshot: Dictionary)
const DEFAULTS := {"font_size": 20, "master_volume": 1.0}
var _data: Dictionary = DEFAULTS.duplicate(true)
var persist_callback: Callable

func snapshot() -> Dictionary:
	return _data

func set_font_size(value: int) -> bool:
	if value not in [20, 24, 28, 32]:
		return false
	return _apply({"font_size": value})

func _apply(patch: Dictionary) -> bool:
	_data.merge(patch, true)
	changed.emit(_data)
	if persist_callback.is_valid():
		return bool(persist_callback.call(_data))
	return true

func set_master_volume(value: float) -> bool:
	if value < 0.0 or value > 1.0:
		return false
	return _apply({"master_volume": value})
