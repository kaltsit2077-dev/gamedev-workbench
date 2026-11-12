extends RefCounted
signal changed
var font_size: int = 20
var reduced_motion: bool = false

func set_font_size(value: float) -> void:
	font_size = clampi(roundi(value), 20, 30)
	changed.emit()

func set_reduced_motion(value: bool) -> void:
	reduced_motion = value
	changed.emit()

func reset() -> void:
	font_size = 20
	reduced_motion = false
	changed.emit()
