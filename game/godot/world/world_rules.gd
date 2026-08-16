class_name WorldRules
extends RefCounted

## Client-side display rules — validation happens on Go server.

const ALLOWED_ACTIONS := [
	"FLOOD", "FIRE", "MEMORY_DECAY", "MEMORY_REMEMBER",
	"CREATE", "DESTROY", "TRANSFORM", "STORM"
]

static func color_for_type(entity_type: String) -> Color:
	match entity_type:
		"ocean", "river":
			return Color(0.1, 0.4, 0.9, 0.8)
		"forest":
			return Color(0.15, 0.55, 0.2)
		"fortress":
			return Color(0.5, 0.5, 0.55)
		"mountain":
			return Color(0.45, 0.42, 0.38)
		"city", "ruins":
			return Color(0.6, 0.55, 0.5)
		"storm":
			return Color(0.3, 0.35, 0.5)
		"core":
			return Color(0.6, 0.3, 0.9)
		"human_player":
			return Color(0.2, 0.6, 1.0)
		"ai_agent":
			return Color(1.0, 0.3, 0.3)
		"bridge":
			return Color(0.55, 0.4, 0.25)
		_:
			return Color(0.4, 0.4, 0.4)

static func mesh_scale_for(entity: WorldEntity) -> Vector3:
	return entity.scale if entity.scale.length() > 0.1 else Vector3.ONE
