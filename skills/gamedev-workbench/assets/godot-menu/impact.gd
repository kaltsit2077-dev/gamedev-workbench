extends Control
const DURATION: float = 1.2
var elapsed: float = 0.0
var active: bool = false
var reduced_motion: bool = false
var light := ColorRect.new()
var material_instance := ShaderMaterial.new()

func _ready() -> void:
	clip_contents = true
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	material_instance.shader = preload("res://impact.gdshader")
	light.material = material_instance
	light.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(light)
	light.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	set_process(false)
	resized.connect(_parameters)

func _parameters() -> void:
	material_instance.set_shader_parameter("progress", clampf(elapsed / DURATION, 0.0, 1.0))
	material_instance.set_shader_parameter("aspect", size.x / maxf(size.y, 1.0))
	material_instance.set_shader_parameter("strength", 0.18 if reduced_motion else 1.0)
	queue_redraw()

func trigger() -> void:
	elapsed = 0.0
	active = true
	visible = true
	set_process(true)
	_parameters()

func _process(delta: float) -> void:
	advance(delta)

func advance(delta: float) -> void:
	if not active:
		return
	elapsed = minf(DURATION, elapsed + maxf(0.0, delta))
	if elapsed >= DURATION:
		active = false
		visible = false
		set_process(false)
	_parameters()

func _draw() -> void:
	if not active:
		return
	var t: float = elapsed / DURATION
	var center: Vector2 = size * 0.5
	var radius: float = minf(size.x, size.y) * 0.42
	var fade: float = 1.0 - t
	if reduced_motion:
		draw_arc(center, radius * 0.35, 0, TAU, 64, Color(0.3, 0.9, 0.95, fade * 0.4), 2.0, true)
		return
	for index: int in range(28):
		var angle: float = float(index) * 2.399963
		var direction := Vector2(cos(angle), sin(angle))
		var travel: float = radius * (0.12 + t * (0.5 + float(index % 5) * 0.08))
		var tail: float = radius * 0.11 * fade
		draw_line(center + direction * maxf(0.0, travel - tail), center + direction * travel,
			Color(1.0, 0.68, 0.28, fade), 1.5 + float(index % 2), true)
	draw_arc(center, radius * t, -0.2 + t, 2.4 + t, 48, Color(0.35, 0.95, 1.0, fade), 2.0, true)
