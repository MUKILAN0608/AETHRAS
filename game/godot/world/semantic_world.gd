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
	_http.timeout = 20.0

	_world_renderer = renderer

	_dynamic_camera = camera

	_entity_container = entity_container

	_http.request_completed.connect(_on_http_completed)

func generate_world(scenario_index: int, seed_value: int) -> void:
	pending_interpretation = {}

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
	if str(pending_interpretation.get("status", "")) != "VALID" or str(pending_interpretation.get("proposal_id", "")).is_empty():
		error_occurred.emit("This proposal requires review or reinterpretation")
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
		"proposal_id": pending_interpretation.get("proposal_id", ""),

	})

func tick_environment() -> void:
	pending_interpretation = {}

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
		_pending_callback = Callable()
		pending_interpretation = {}
		error_occurred.emit("Could not start the request; retry when the server is available")

func _http_get(endpoint: String) -> void:

	var url := GameConfig.GAME_SERVER_URL + endpoint

	var err := _http.request(url)

	if err != OK:
		_pending_callback = Callable()
		pending_interpretation = {}
		error_occurred.emit("Could not start the request; retry when the server is available")

func _on_http_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:

	if result != HTTPRequest.RESULT_SUCCESS or response_code < 200 or response_code >= 300:
		_pending_callback = Callable()
		pending_interpretation = {}
		var message := "Request failed (HTTP %d). Check the server and retry." % response_code
		if result == HTTPRequest.RESULT_TIMEOUT:
			message = "The request timed out. Reinterpret the prompt before trying to execute."
		elif response_code == 409:
			message = "The proposal expired or the world changed. Interpret the prompt again."
		elif response_code == 422:
			message = "Go rejected this proposal under the current game rules. Edit and reinterpret."
		error_occurred.emit(message)
		return

	var json := JSON.new()

	if json.parse(body.get_string_from_utf8()) != OK or not json.data is Dictionary:
		_pending_callback = Callable()
		pending_interpretation = {}

		error_occurred.emit("Invalid JSON from server")

		return

	var callback := _pending_callback
	_pending_callback = Callable()
	if callback.is_valid():
		callback.call(json.data)

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
	world_updated.emit(current_state, {})
