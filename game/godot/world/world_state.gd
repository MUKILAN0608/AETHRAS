class_name WorldState
extends RefCounted

## Canonical world state — mirrors Go authoritative server state.

var world_id: String = ""
var seed: int = 0
var turn: int = 0
var scenario_id: String = ""
var entities: Dictionary = {}  # id -> WorldEntity
var relationships: Array = []  # WorldRelation
var regions: Array = []
var environmental_state: Dictionary = {}
var active_events: Array = []
var semantic_state: Dictionary = {}
var history: Array = []

static func from_dict(data: Dictionary) -> WorldState:
	var ws := WorldState.new()
	ws.world_id = str(data.get("world_id", ""))
	ws.seed = int(data.get("seed", 0))
	ws.turn = int(data.get("turn", 0))
	ws.scenario_id = str(data.get("scenario_id", ""))
	ws.environmental_state = data.get("environmental_state", {})
	ws.semantic_state = data.get("semantic_state", {})
	ws.regions = data.get("regions", [])
	ws.history = data.get("history", [])

	var ents: Dictionary = data.get("entities", {})
	for id in ents:
		ws.entities[id] = WorldEntity.from_dict(ents[id])

	for rel_data in data.get("relationships", []):
		ws.relationships.append(WorldRelation.from_dict(rel_data))

	for ev_data in data.get("active_events", []):
		ws.active_events.append(WorldEvent.from_dict(ev_data))

	return ws

func get_entities_by_type(entity_type: String) -> Array:
	var result: Array = []
	for id in entities:
		var e: WorldEntity = entities[id]
		if e.type == entity_type:
			result.append(e)
	return result

func get_entity(id: String) -> WorldEntity:
	return entities.get(id, null)
