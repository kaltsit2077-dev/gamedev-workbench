class_name CaseWidgetState
extends RefCounted
var source

func bind_state(next_source) -> void:
	source = next_source

func caption() -> String:
	return str(source.coins) if source != null else "unbound"
