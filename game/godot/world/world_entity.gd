class_name WorldEntity
extends RefCounted

## Generic world entity data parsed from authoritative Go server state.

var id: String = ""
var type: String = ""
var name: String = ""
var position: Vector3 = Vector3.ZERO
var scale: Vector3 = Vector3.ONE
var properties: Dictionary = {}
var state: Dictionary = {}
var semantic_tags: Array = []
var health: float = 100.0
var importance: float = 0.5

static func from_dict(data: Dictionary) -> WorldEntity:
	var e := WorldEntity.new()
	e.id = str(data.get("id", ""))
	e.type = str(data.get("type", ""))
	e.name = str(data.get("name", ""))
	var pos: Dictionary = data.get("position", {})
	e.position = Vector3(float(pos.get("x", 0)), float(pos.get("y", 0)), float(pos.get("z", 0)))
	var scl: Dictionary = data.get("scale", {})
	e.scale = Vector3(float(scl.get("x", 1)), float(scl.get("y", 1)), float(scl.get("z", 1)))
	e.properties = data.get("properties", {})
	e.state = data.get("state", {})
	e.semantic_tags = data.get("semantic_tags", [])
	e.health = float(data.get("health", 100))
	e.importance = float(data.get("importance", 0.5))
	return e
