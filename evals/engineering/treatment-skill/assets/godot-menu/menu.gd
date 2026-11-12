extends Control
signal audit_changed
signal completed
const Model = preload("res://state.gd")
const Impact = preload("res://impact.gd")
var model = Model.new()
var impact = Impact.new()
var screen_host := Control.new()
var main_scroll := ScrollContainer.new()
var settings_scroll := ScrollContainer.new()
var main_panel := VBoxContainer.new()
var settings_panel := VBoxContainer.new()
var confirm_panel := VBoxContainer.new()
var stack: Array[Dictionary] = []
var begin_button := Button.new()
var options_button := Button.new()
var replay_button := Button.new()
var finish_button := Button.new()
var back_button := Button.new()
var reset_button := Button.new()
var cancel_button := Button.new()
var apply_button := Button.new()
var font_slider := HSlider.new()
var motion_toggle := CheckButton.new()
var long_text: Label
var effect_area := PanelContainer.new()
var status := Label.new()
var keyboard_events: int = 0
var mouse_events: int = 0
var joypad_events: int = 0
var settings_opened: int = 0
var focus_restored: int = 0
var replayed: int = 0
var text_size_changed: int = 0
var _last_font: int = 20

func label(text: String, parent: Node, font: int = 0) -> Label:
	var item := Label.new()
	item.text = text
	item.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if font > 0:
		item.add_theme_font_size_override("font_size", font)
	parent.add_child(item)
	return item

func button(item: Button, text: String, parent: Node, action: Callable) -> void:
	item.text = text
	item.custom_minimum_size.y = 48
	parent.add_child(item)
	item.pressed.connect(action)

func focus_order(controls: Array[Control]) -> void:
	for index: int in range(controls.size()):
		var current: Control = controls[index]
		var next: Control = controls[(index + 1) % controls.size()]
		var previous: Control = controls[(index + controls.size() - 1) % controls.size()]
		current.focus_next = current.get_path_to(next)
		current.focus_previous = current.get_path_to(previous)
		current.focus_neighbor_bottom = current.focus_next
		current.focus_neighbor_top = current.focus_previous

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# The sample declares its own controller actions instead of assuming engine defaults.
	var gamepad_bindings := {&"ui_accept": JOY_BUTTON_A, &"ui_cancel": JOY_BUTTON_B,
		&"ui_up": JOY_BUTTON_DPAD_UP, &"ui_down": JOY_BUTTON_DPAD_DOWN}
	for action: StringName in gamepad_bindings:
		var binding := InputEventJoypadButton.new()
		binding.device = -1
		binding.button_index = gamepad_bindings[action]
		if not InputMap.action_has_event(action, binding):
			InputMap.action_add_event(action, binding)
	var style := StyleBoxFlat.new()
	style.bg_color = Color("122333")
	style.border_color = Color("35536a")
	style.set_border_width_all(1)
	style.set_corner_radius_all(7)
	style.content_margin_left = 18
	style.content_margin_right = 18
	var focus_style: StyleBoxFlat = style.duplicate()
	focus_style.bg_color = Color("254258")
	focus_style.border_color = Color("e7b766")
	focus_style.set_border_width_all(2)
	theme = Theme.new()
	theme.default_font_size = model.font_size
	theme.set_stylebox("normal", "Button", style)
	theme.set_stylebox("focus", "Button", focus_style)
	theme.set_stylebox("hover", "Button", focus_style)
	var margin := MarginContainer.new()
	add_child(margin)
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 20)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 12)
	margin.add_child(column)
	label("DEEP SIGNAL  /  TRANSIT TERMINAL", column, 28)
	label("Navigate with Tab / arrows. Enter selects. Escape returns.", column, 16)
	screen_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	column.add_child(screen_host)
	for panel: Control in [main_scroll, settings_panel, confirm_panel]:
		screen_host.add_child(panel)
		panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		panel.visible = false
	main_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	main_scroll.follow_focus = true
	main_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main_panel.add_theme_constant_override("separation", 12)
	main_scroll.add_child(main_panel)
	button(begin_button, "Begin calibration", main_panel, replay)
	button(options_button, "Options", main_panel, open_settings)
	button(replay_button, "Replay impact", main_panel, replay)
	button(finish_button, "Finish input check", main_panel, finish)
	finish_button.disabled = true
	effect_area.custom_minimum_size.y = 180
	main_panel.add_child(effect_area)
	effect_area.add_child(impact)
	settings_panel.add_theme_constant_override("separation", 12)
	label("OPTIONS / LONG TEXT", settings_panel, 24)
	settings_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	settings_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	settings_scroll.follow_focus = true
	settings_panel.add_child(settings_scroll)
	var body := VBoxContainer.new()
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 16)
	settings_scroll.add_child(body)
	label("Text size — move the slider", body)
	font_slider.min_value = 20
	font_slider.max_value = 30
	font_slider.step = 2
	font_slider.value = 20
	font_slider.custom_minimum_size.y = 42
	body.add_child(font_slider)
	font_slider.value_changed.connect(model.set_font_size)
	motion_toggle.text = "Reduce motion"
	body.add_child(motion_toggle)
	motion_toggle.toggled.connect(model.set_reduced_motion)
	label("Reduce the flash intensity and replace moving sparks with a quiet fading ring.", body)
	long_text = label(("The survey vessel is waiting beyond the relay. Every saved route remembers a different sky. " +
		"This deliberately extended description must wrap inside the panel, remain readable when text grows, and scroll without moving the return button outside the screen.\n\n").repeat(7), body)
	button(reset_button, "Reset preferences", settings_panel, open_confirmation)
	button(back_button, "Back to terminal", settings_panel, pop_screen)
	confirm_panel.add_theme_constant_override("separation", 12)
	label("Reset preferences?", confirm_panel, 24)
	label("Text size and reduced motion will return to defaults. The menu remembers which control opened this page.", confirm_panel)
	button(apply_button, "Apply reset", confirm_panel, apply_reset)
	button(cancel_button, "Cancel", confirm_panel, pop_screen)
	column.add_child(status)
	status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	status.add_theme_font_size_override("font_size", 15)
	focus_order([begin_button, options_button, replay_button, finish_button])
	focus_order([font_slider, motion_toggle, reset_button, back_button])
	focus_order([apply_button, cancel_button])
	model.changed.connect(update_preferences)
	stack.append({"panel": main_scroll, "return_focus": null})
	main_scroll.visible = true
	begin_button.grab_focus()
	update_audit()

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode in [KEY_TAB, KEY_ENTER, KEY_SPACE, KEY_ESCAPE, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
			keyboard_events += 1
	elif event is InputEventMouseButton and event.pressed:
		mouse_events += 1
	elif event is InputEventJoypadButton and event.pressed:
		joypad_events += 1
	update_audit()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and stack.size() > 1:
		pop_screen()
		get_viewport().set_input_as_handled()

func push_screen(panel: Control, initial_focus: Control) -> void:
	if stack[-1].panel == panel:
		return
	var previous_focus: Control = get_viewport().gui_get_focus_owner()
	stack[-1].panel.visible = false
	panel.visible = true
	stack.append({"panel": panel, "return_focus": previous_focus})
	initial_focus.grab_focus()
	update_audit()

func open_settings() -> void:
	settings_opened += 1
	push_screen(settings_panel, font_slider)

func open_confirmation() -> void:
	push_screen(confirm_panel, cancel_button)

func pop_screen() -> void:
	if stack.size() <= 1:
		return
	var removed: Dictionary = stack.pop_back()
	removed.panel.visible = false
	stack[-1].panel.visible = true
	if is_instance_valid(removed.return_focus):
		removed.return_focus.grab_focus()
		if removed.return_focus.has_focus():
			focus_restored += 1
	update_audit()

func apply_reset() -> void:
	model.reset()
	pop_screen()

func update_preferences() -> void:
	theme.default_font_size = model.font_size
	font_slider.set_value_no_signal(model.font_size)
	motion_toggle.set_pressed_no_signal(model.reduced_motion)
	impact.reduced_motion = model.reduced_motion
	if model.font_size != _last_font:
		text_size_changed += 1
	_last_font = model.font_size
	update_audit()

func replay() -> void:
	replayed += 1
	impact.trigger()
	update_audit()

func input_steps_complete() -> bool:
	return keyboard_events >= 1 and mouse_events >= 2 and settings_opened >= 1 and focus_restored >= 1 and replayed >= 1 and text_size_changed >= 1

func update_audit() -> void:
	if not is_instance_valid(status) or not status.is_inside_tree():
		return
	finish_button.disabled = not input_steps_complete()
	if text_size_changed == 0:
		status.text = "Next: open Options, click the text-size slider, then press Right."
	elif keyboard_events == 0:
		status.text = "Next: use Tab or an arrow key in this window."
	elif focus_restored == 0 or stack.size() > 1:
		status.text = "Next: press Escape to return and check that focus is restored."
	elif replayed == 0 or mouse_events < 2:
		status.text = "Next: click Replay impact twice."
	else:
		status.text = "Ready: choose Finish input check to save this session."
	audit_changed.emit()

func finish() -> void:
	if input_steps_complete():
		completed.emit()
