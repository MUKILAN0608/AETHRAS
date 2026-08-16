extends Node
class_name SemanticWorld

signal world_generated(state)
signal world_updated(state, transform: Dictionary)
signal interpretation_ready(data: Dictionary)
signal error_occurred(message: String)

const SCENARIOS := [
	{
		"id": "scenario_1",
		"description": "A fortress stands between a living forest and a restless ocean."
	},
	{
		"id": "scenario_2",
		"description": "A ruined city floats above a world of endless storms."
	},
	{
		"id": "scenario_3",
		"description": "A civilization survives around a mountain that changes shape whenever someone lies."
	},
]

var current_state = null
var pending_interpretation: Dictionary = {}
var _http: HTTPRequest
var _pending_callback: Callable = Callable()
var _world_renderer = null
var _dynamic_camera = null
var _entity_container: Node3D


func setup(http: HTTPRequest, renderer, camera, entity_container: Node3D) -> void:
	_http = http
	_world_renderer = renderer
	_dynamic_camera = camera
	_entity_container = entity_container
	_http.request_completed.connect(_on_http_completed)


func generate_world(scenario_index: int, seed_value: int) -> void:
	var scenario: Dictionary = SCENARIOS[scenario_index]
	var body := {
		"scenario_id": scenario["id"],
		"scenario": scenario["description"],
		"seed": seed_value,
		"difficulty": 0.5,
		"world_size": 32.0,
	}
	_pending_callback = _on_world_generated
	_post("/api/world/generate", body)


func interpret_prompt(prompt: String) -> void:
	pending_interpretation = {}
	var ctx := _build_world_context()
	_pending_callback = _on_interpret_result
	_post("/api/prompt/interpret", {
		"prompt": prompt,
		"player_id": "human",
		"turn": current_state.turn if current_state else 1,
		"world_id": current_state.world_id if current_state else "world_001",
		"world_context": ctx,
		"history": [],
	})


func execute_pending_action(prompt: String) -> void:
	if pending_interpretation.is_empty():
		error_occurred.emit("No interpretation to execute")
		return
	var action = pending_interpretation.get("action", {})
	if action.is_empty():
		error_occurred.emit("No valid action in interpretation")
		return
	_pending_callback = _on_execute_result
	_post("/api/prompt/execute", {
		"prompt": prompt,
		"actor": "human",
		"action": action,
	})


func tick_environment() -> void:
	_pending_callback = _on_tick_result
	_http_get("/api/world/tick")


func _build_world_context() -> Dictionary:
	if current_state == null:
		return {}
	var entities: Dictionary = {}
	var nearby: Array = []
	for id in current_state.entities:
		var e = current_state.entities[id]
		var entry := {
			"id": id,
			"type": e.type,
			"name": e.name,
			"health": e.health,
		}
		entities[id] = entry
		nearby.append(entry)
	return {
		"entities": entities,
		"nearby_entities": nearby,
		"turn": current_state.turn,
	}


func _post(endpoint: String, body: Dictionary) -> void:
	var url := GameConfig.GAME_SERVER_URL + endpoint
	var headers := ["Content-Type: application/json"]
	var err := _http.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	if err != OK:
		error_occurred.emit("HTTP request failed")


func _http_get(endpoint: String) -> void:
	var url := GameConfig.GAME_SERVER_URL + endpoint
	var err := _http.request(url)
	if err != OK:
		error_occurred.emit("HTTP request failed")


func _on_http_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300:
		error_occurred.emit("Server error HTTP %d" % response_code)
		return

	var json := JSON.new()
	if json.parse(body.get_string_from_utf8()) != OK:
		error_occurred.emit("Invalid JSON from server")
		return

	if _pending_callback.is_valid():
		_pending_callback.call(json.data)
	_pending_callback = Callable()


func _on_world_generated(data: Dictionary) -> void:
	current_state = load("res://world/world_state.gd").from_dict(data)
	_world_renderer.render_world(current_state)
	world_generated.emit(current_state)


func _on_interpret_result(data: Dictionary) -> void:
	pending_interpretation = data
	interpretation_ready.emit(data)


func _on_execute_result(data: Dictionary) -> void:
	var transform: Dictionary = data.get("transform", {})
	var world_data: Dictionary = transform.get("world_state", {})
	if world_data.is_empty():
		error_occurred.emit("No world state in response")
		return

	current_state = load("res://world/world_state.gd").from_dict(world_data)
	var affected: Array = transform.get("affected_ids", [])
	var hints: Array = transform.get("visual_hints", [])
	var action_proposal: Dictionary = data.get("action_proposal", {})
	var action_type: String = str(action_proposal.get("action_type", ""))

	_world_renderer.render_world(current_state, affected, hints)

	var positions: Array = []
	for id in affected:
		var e = current_state.get_entity(str(id))
		if e:
			positions.append(e.position)
	_dynamic_camera.respond_to_action(action_type, positions)

	world_updated.emit(current_state, transform)
	pending_interpretation = {}


func _on_tick_result(data: Dictionary) -> void:
	current_state = load("res://world/world_state.gd").from_dict(data)
	_world_renderer.render_world(current_state)
