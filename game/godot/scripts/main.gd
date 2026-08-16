extends Node3D



## Main scene — Prompt Intelligence Engine (Phase 3).



const _SemanticWorldScript = preload("res://world/semantic_world.gd")

const _WorldTransformerScript = preload("res://world/world_transformer.gd")



@onready var _camera = $DynamicCamera

@onready var _light: DirectionalLight3D = $DirectionalLight3D

@onready var _entity_container: Node3D = $EntityContainer

@onready var _world_renderer = $WorldRenderer

@onready var _semantic_world = $SemanticWorld

@onready var _http: HTTPRequest = $HTTPRequest



@onready var _scenario_option: OptionButton = $UI/Panel/VBox/ScenarioOption

@onready var _seed_input: SpinBox = $UI/Panel/VBox/SeedInput

@onready var _generate_button: Button = $UI/Panel/VBox/GenerateButton

@onready var _prompt_input: LineEdit = $UI/Panel/VBox/PromptInput

@onready var _submit_button: Button = $UI/Panel/VBox/SubmitButton

@onready var _interpretation_label: Label = $UI/Panel/VBox/InterpretationLabel

@onready var _execute_button: Button = $UI/Panel/VBox/ExecuteButton

@onready var _tick_button: Button = $UI/Panel/VBox/TickButton

@onready var _status_label: Label = $UI/Panel/VBox/StatusLabel

@onready var _result_label: Label = $UI/Panel/VBox/ResultLabel

@onready var _world_state_label: Label = $UI/Panel/VBox/WorldStateLabel

@onready var _entity_count_label: Label = $UI/Panel/VBox/EntityCountLabel



var _is_busy := false

var _last_prompt := ""

var _pending_action: Dictionary = {}





func _ready() -> void:

	_world_renderer.setup(_entity_container, _light)

	_semantic_world.setup(_http, _world_renderer, _camera, _entity_container)

	_semantic_world.world_generated.connect(_on_world_generated)

	_semantic_world.world_updated.connect(_on_world_updated)

	_semantic_world.interpretation_ready.connect(_on_interpretation_ready)

	_semantic_world.error_occurred.connect(_on_error)



	_generate_button.pressed.connect(_on_generate_pressed)

	_submit_button.pressed.connect(_on_submit_pressed)

	_execute_button.pressed.connect(_on_execute_pressed)

	_tick_button.pressed.connect(_on_tick_pressed)



	_scenario_option.clear()

	for i in range(_SemanticWorldScript.SCENARIOS.size()):

		_scenario_option.add_item("Scenario %d" % (i + 1), i)

	_scenario_option.select(0)

	_seed_input.value = 42

	_prompt_input.text = "The ocean rises and consumes the fortress."

	_status_label.text = "Select scenario + seed, then Generate World."

	_update_ui_state(false)





func _on_generate_pressed() -> void:

	if _is_busy:

		return

	_is_busy = true

	_update_ui_state(true)

	_status_label.text = "Generating procedural world..."

	_interpretation_label.text = ""

	_execute_button.disabled = true

	_clear_entity_container()

	_semantic_world.generate_world(_scenario_option.selected, int(_seed_input.value))





func _on_submit_pressed() -> void:

	if _is_busy or _semantic_world.current_state == null:

		return

	var prompt_text := _prompt_input.text.strip_edges()

	if prompt_text.is_empty():

		_status_label.text = "Error: prompt cannot be empty."

		return

	_is_busy = true

	_last_prompt = prompt_text

	_update_ui_state(true)

	_status_label.text = "Interpreting prompt..."

	_execute_button.disabled = true

	_semantic_world.interpret_prompt(prompt_text)





func _on_execute_pressed() -> void:

	if _is_busy or _semantic_world.pending_interpretation.is_empty():

		return

	_is_busy = true

	_update_ui_state(true)

	_status_label.text = "Executing action..."

	_semantic_world.execute_pending_action(_last_prompt)





func _on_tick_pressed() -> void:

	if _is_busy or _semantic_world.current_state == null:

		return

	_is_busy = true

	_semantic_world.tick_environment()





func _on_world_generated(state) -> void:

	_is_busy = false

	_update_ui_state(true)

	_status_label.text = "WORLD GENERATED — seed %d, turn %d" % [state.seed, state.turn]

	_world_state_label.text = "WORLD STATE: %d entities, scenario %s" % [state.entities.size(), state.scenario_id]

	_entity_count_label.text = "Entities: %s" % ", ".join(_entity_type_summary(state))

	_result_label.text = ""

	_interpretation_label.text = ""





func _on_interpretation_ready(data: Dictionary) -> void:

	_is_busy = false

	_update_ui_state(true)

	var status: String = str(data.get("status", "UNKNOWN"))

	var interp: Dictionary = data.get("interpretation", {})

	var action: Dictionary = data.get("action", {})

	var conf: Dictionary = data.get("confidence", {})

	var novelty: float = float(data.get("novelty", 0.0))



	var entity_names: PackedStringArray = []

	for e in interp.get("entities", []):

		entity_names.append(str(e.get("name", "")))



	var strategy: Dictionary = interp.get("strategy", {})

	var intent: String = str(interp.get("intent", "")).replace("_", " ").capitalize()



	_interpretation_label.text = (

		"PROMPT\n\"%s\"\n\nINTERPRETATION\n\nIntent:\n%s\n\nEntities:\n%s\n\nStrategy:\n%s\n\nAction:\n%s\n\nConfidence:\n%d%%\n\nNovelty:\n%d%%\n\nStatus:\n%s"

		% [

			interp.get("original_prompt", _last_prompt),

			intent,

			"\n".join(entity_names) if entity_names.size() > 0 else "—",

			strategy.get("strategy_type", "—"),

			action.get("action_type", "—"),

			int(conf.get("overall_confidence", 0.0) * 100),

			int(novelty * 100),

			status,

		]

	)

	_status_label.text = "INTERPRETATION READY — %s" % status

	_pending_action = action

	_execute_button.disabled = status == "INVALID" or action.is_empty()





func _on_world_updated(state, transform: Dictionary) -> void:

	_is_busy = false

	_update_ui_state(true)

	var action_proposal: Dictionary = _pending_action

	var parsed: Dictionary = transform.get("action", {})

	_status_label.text = "ACTION EXECUTED"

	_result_label.text = (

		"ACTION: %s → %s\nTARGET: %s\n\n%s"

		% [

			action_proposal.get("action_type", ""),

			parsed.get("action", ""),

			parsed.get("target", ""),

			_WorldTransformerScript.describe_transform(transform),

		]

	)

	_world_state_label.text = "WORLD STATE CHANGED — turn %d" % state.turn

	_entity_count_label.text = "Causal: %s" % str(transform.get("causal_chain", []))

	_execute_button.disabled = true





func _on_error(message: String) -> void:

	_is_busy = false

	_update_ui_state(_semantic_world.current_state != null)

	_status_label.text = "Error: %s" % message





func _entity_type_summary(state) -> PackedStringArray:

	var counts: Dictionary = {}

	for id in state.entities:

		var e = state.entities[id]

		counts[e.type] = counts.get(e.type, 0) + 1

	var parts: PackedStringArray = []

	for t in counts:

		parts.append("%s x%d" % [t, counts[t]])

	return parts





func _clear_entity_container() -> void:

	for child in _entity_container.get_children():

		child.queue_free()





func _update_ui_state(world_ready: bool) -> void:

	_submit_button.disabled = _is_busy or not world_ready

	_tick_button.disabled = _is_busy or not world_ready

	_generate_button.disabled = _is_busy

