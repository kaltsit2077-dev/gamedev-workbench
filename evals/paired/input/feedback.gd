extends Node2D
var elapsed: float = 0.0
var active: bool = false
const DURATION: float = 0.7
func trigger() -> void:
 if active:
  return
 elapsed = 0.0
 active = true
func advance(delta: float) -> void:
 if not active:
  return
 elapsed += delta
 if elapsed >= DURATION:
  active = false
func _process(delta: float) -> void:
 advance(delta)
