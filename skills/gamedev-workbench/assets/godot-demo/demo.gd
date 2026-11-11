extends Control
const State = preload("res://state.gd")
const Pulse = preload("res://pulse.gd")
var model = State.new()
var pulse = Pulse.new()
var status = Label.new()
var trigger_button = Button.new()
var reset_button = Button.new()
var panel = VBoxContainer.new()
var effect_area = Control.new()

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	process_mode = Node.PROCESS_MODE_PAUSABLE
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 24)
	add_child(margin)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 24)
	margin.add_child(row)
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.size_flags_stretch_ratio = 2.0
	panel.add_theme_constant_override("separation", 18)
	row.add_child(panel)
	var title := Label.new()
	title.text = "GAMEDEV WORKBENCH / ISOLATED EXAMPLE"
	title.add_theme_font_size_override("font_size", 25)
	title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	panel.add_child(title)
	panel.add_child(status)
	trigger_button.text = "Charge [Enter / Space]"
	trigger_button.custom_minimum_size = Vector2(0, 54)
	panel.add_child(trigger_button)
	reset_button.text = "Reset model"
	reset_button.custom_minimum_size = Vector2(0, 54)
	panel.add_child(reset_button)
	trigger_button.pressed.connect(_trigger)
	reset_button.pressed.connect(model.reset)
	model.changed.connect(_update_status)
	effect_area.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	effect_area.custom_minimum_size = Vector2(100, 0)
	effect_area.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(effect_area)
	effect_area.add_child(pulse)
	effect_area.resized.connect(_layout_effect)
	trigger_button.focus_next = trigger_button.get_path_to(reset_button)
	trigger_button.focus_previous = trigger_button.get_path_to(reset_button)
	reset_button.focus_next = reset_button.get_path_to(trigger_button)
	reset_button.focus_previous = reset_button.get_path_to(trigger_button)
	_update_status(model.charge)
	trigger_button.grab_focus()
	_layout_effect.call_deferred()

func _layout_effect() -> void:
	pulse.position = effect_area.size * 0.5
	var fit: float = maxf(0.01, minf(effect_area.size.x, effect_area.size.y) * 0.42 / 165.0)
	pulse.scale = Vector2.ONE * fit

func _trigger() -> void:
	model.trigger()
	pulse.trigger()

func _update_status(value: int) -> void:
	status.text = "Model charge: %d / 5" % value
