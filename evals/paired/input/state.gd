extends RefCounted
signal changed(value: int)
var charge: int = 0
func trigger() -> void:
 charge += 1
 changed.emit(charge)
func reset() -> void:
 charge = 0
