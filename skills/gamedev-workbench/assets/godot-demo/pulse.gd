extends Node2D
## One clock owns the visible effect and stops after its duration.
var elapsed: float = 0.0
var active: bool = false
const DURATION: float = 0.7

func _ready() -> void:
	visible = active
	set_process(active)

func trigger() -> void:
	elapsed = 0.0
	active = true
	visible = true
	set_process(true)
	queue_redraw()

func advance(delta: float) -> void:
	if not active:
		return
	elapsed = minf(elapsed + delta, DURATION)
	active = elapsed < DURATION
	visible = active
	if not active:
		set_process(false)
	queue_redraw()

func _process(delta: float) -> void:
	advance(delta)

func _draw() -> void:
	if active:
		var t: float = elapsed / DURATION
		draw_arc(Vector2.ZERO, 35.0 + t * 130.0, 0.0, TAU, 64,
			Color(0.3, 0.85, 1.0, 1.0 - t), 7.0 * (1.0 - t), true)
