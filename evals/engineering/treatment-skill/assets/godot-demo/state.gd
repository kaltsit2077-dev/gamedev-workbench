extends RefCounted
## The model is the only owner of charge. UI receives snapshots.
signal changed(value: int)
var charge: int = 0

func trigger() -> void:
	charge = (charge + 1) % 6
	changed.emit(charge)

func reset() -> void:
	charge = 0
	changed.emit(charge)
