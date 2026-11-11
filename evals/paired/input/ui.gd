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
 trigger_button.pressed.connect(_on_trigger)
 reset_button.pressed.connect(model.reset)
func _on_trigger() -> void:
 model.charge += 1
 effect.trigger()
func _process(_delta: float) -> void:
 status.text = str(model.charge)
