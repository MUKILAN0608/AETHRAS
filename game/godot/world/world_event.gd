class_name WorldEvent
extends RefCounted

var id: String = ""
var type: String = ""
var intensity: float = 0.0
var turn: int = 0
var processed: bool = false

static func from_dict(data: Dictionary) -> WorldEvent:
	var e := WorldEvent.new()
	e.id = str(data.get("id", ""))
	e.type = str(data.get("type", ""))
	e.intensity = float(data.get("intensity", 0))
	e.turn = int(data.get("turn", 0))
	e.processed = bool(data.get("processed", false))
	return e
