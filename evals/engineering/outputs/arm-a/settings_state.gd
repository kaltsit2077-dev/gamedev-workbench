extends RefCounted
signal changed(snapshot: Dictionary)
const DEFAULTS := {"font_size": 20, "reduced_motion": false, "master_volume": 1.0}
var _data: Dictionary = DEFAULTS.duplicate(true)
var persist_callback: Callable

func snapshot() -> Dictionary:
	return _data.duplicate(true)

func set_font_size(value: int) -> bool:
	if value not in [20, 24, 28, 32]:
		return false
	return _apply({"font_size": value})

func _apply(patch: Dictionary) -> bool:
	var candidate := _data.duplicate(true)
	candidate.merge(patch, true)
	if candidate == _data:
		return true
	if persist_callback.is_valid():
		var saved = persist_callback.call(candidate.duplicate(true))
		if not (saved is bool and saved == true):
			return false
	_data = candidate
	changed.emit(snapshot())
	return true

func set_reduced_motion(value: bool) -> bool:
	return _apply({"reduced_motion": value})

func set_master_volume(value: float) -> bool:
	if not is_finite(value) or value < 0.0 or value > 1.0:
		return false
	return _apply({"master_volume": value})
