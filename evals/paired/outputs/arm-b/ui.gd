extends Control
const Model = preload("res://state.gd")
const Feedback = preload("res://feedback.gd")
var model = Model.new()
var effect = Feedback.new()
var status = Label.new()
var trigger_button = Button.new()
var reset_button = Button.new()
func _ready() -> void:
 var layout = VBoxContainer.new()
 layout.position = Vector2(16, 16)
 add_child(layout)
 layout.add_child(status)
 layout.add_child(trigger_button)
 layout.add_child(reset_button)
 add_child(effect)
 trigger_button.text = "Charge"
 reset_button.text = "Reset"
 trigger_button.pressed.connect(_on_trigger)
 reset_button.pressed.connect(model.reset)
 model.changed.connect(_on_charge_changed)
 _on_charge_changed(model.charge)
func _on_trigger() -> void:
 model.trigger()
 effect.trigger()
func _on_charge_changed(value: int) -> void:
 status.text = str(value)
