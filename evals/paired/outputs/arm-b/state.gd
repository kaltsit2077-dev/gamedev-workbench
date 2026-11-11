extends RefCounted
signal changed(value: int)
var charge: int = 0
func trigger() -> void:
 charge = mini(charge + 1, 5)
 changed.emit(charge)
func reset() -> void:
 charge = 0
 changed.emit(charge)
