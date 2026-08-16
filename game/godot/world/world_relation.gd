class_name WorldRelation
extends RefCounted

var id: String = ""
var from_id: String = ""
var to_id: String = ""
var type: String = ""
var strength: float = 0.5
var active: bool = true

static func from_dict(data: Dictionary) -> WorldRelation:
	var r := WorldRelation.new()
	r.id = str(data.get("id", ""))
	r.from_id = str(data.get("from_id", ""))
	r.to_id = str(data.get("to_id", ""))
	r.type = str(data.get("type", ""))
	r.strength = float(data.get("strength", 0.5))
	r.active = bool(data.get("active", true))
	return r
