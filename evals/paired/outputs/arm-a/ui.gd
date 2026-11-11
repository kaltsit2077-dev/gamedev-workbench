extends Control
const Model = preload("res://state.gd")
const Feedback = preload("res://feedback.gd")
var model = Model.new()
var effect = Feedback.new()
var status = Label.new()
var trigger_button = Button.new()
var reset_button = Button.new()
func _ready() -> void:
 add_child(status)
 add_child(trigger_button)
 add_child(reset_button)
 add_child(effect)
 trigger_button.text = "Charge"
 reset_button.text = "Reset"
 status.position = Vector2(16, 16)
 trigger_button.position = Vector2(16, 48)
 reset_button.position = Vector2(120, 48)
 trigger_button.size = Vector2(88, 32)
 reset_button.size = Vector2(88, 32)
 model.changed.connect(_on_model_changed)
 _on_model_changed(model.charge)
 trigger_button.pressed.connect(_on_trigger)
 reset_button.pressed.connect(model.reset)
func _on_trigger() -> void:
 model.trigger()
 effect.trigger()
func _on_model_changed(value: int) -> void:
 status.text = str(value)
