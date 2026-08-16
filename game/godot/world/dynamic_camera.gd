extends Camera3D
class_name DynamicCamera

## Responds to world events — not permanently fixed.

var _default_position: Vector3
var _default_rotation: Vector3
var _tween: Tween = null


func _ready() -> void:
	_default_position = position
	_default_rotation = rotation


func focus_on_position(target: Vector3, zoom_factor: float = 1.0, duration: float = 1.5) -> void:
	if _tween:
		_tween.kill()
	_tween = create_tween()
	var offset := (global_position - Vector3(0, global_position.y, 0)).normalized() * 8.0 * zoom_factor
	offset.y = 6.0
	var new_pos := target + offset
	_tween.set_parallel(true)
	_tween.tween_property(self, "global_position", new_pos, duration)
	_tween.tween_property(self, "rotation:x", -0.4, duration)


func respond_to_action(action: String, affected_positions: Array) -> void:
	match action:
		"FLOOD":
			if affected_positions.size() > 0:
				focus_on_position(affected_positions[0], 0.8)
		"FIRE":
			if affected_positions.size() > 0:
				focus_on_position(affected_positions[0], 0.9)
		"MEMORY_REMEMBER", "MEMORY_DECAY":
			if affected_positions.size() > 0:
				focus_on_position(affected_positions[0], 0.7)
		"STORM":
			pull_back(1.3)
		_:
			reset_camera()


func pull_back(factor: float = 1.2, duration: float = 2.0) -> void:
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, "global_position", _default_position * factor, duration)


func reset_camera(duration: float = 1.5) -> void:
	if _tween:
		_tween.kill()
	_tween = create_tween()
	_tween.tween_property(self, "position", _default_position, duration)
	_tween.parallel().tween_property(self, "rotation", _default_rotation, duration)
