extends SceneTree

var _frames := 0


func _initialize() -> void:
	process_frame.connect(func(): _frames += 1)
	_run.call_deferred()


func _failed(message: String) -> void:
	push_error(message)
	quit(1)


func _check(condition: bool, message: String) -> bool:
	if not condition:
		_failed(message)
	return condition


func _run() -> void:
	create_timer(20.0).timeout.connect(func(): _failed("Prompt flow test timed out"))
	var scene: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	var semantic: Node = scene.get_node("SemanticWorld")
	var execute: Button = scene.get_node("UI/Panel/VBox/ExecuteButton")
	var input: LineEdit = scene.get_node("UI/Panel/VBox/PromptInput")
	semantic.error_occurred.connect(_failed)
	scene.call("_on_generate_pressed")
	await semantic.world_generated
	input.text = "The ocean rises and consumes the fortress."
	_frames = 0
	scene.call("_on_submit_pressed")
	var interpretation: Dictionary = await semantic.interpretation_ready
	if OS.get_cmdline_user_args().has("--expect-fallback"):
		var decision: Dictionary = interpretation.get("decision", {})
		if not _check(interpretation.get("status") == "AMBIGUOUS" and decision.get("reason") == "timeout" and execute.disabled, "Timed-out model response did not block execution"):
			return
		if not _check(_frames > 2 and not scene.get("_is_busy"), "Delayed model request froze frames or left UI busy"):
			return
		print("PASS: Godot remained responsive during mocked provider timeout; execution blocked")
		scene.queue_free()
		await process_frame
		quit(0)
		return
	if not _check(interpretation.get("status") == "VALID" and not execute.disabled, "Valid proposal was not reviewable"):
		return
	if not _check(interpretation.get("decision", {}).get("status") == "disabled", "Headless smoke requires disabled provider"):
		return
	scene.call("_on_execute_pressed")
	await semantic.world_updated
	if not _check(execute.disabled and semantic.current_state.environmental_state.get("water_level", 0.0) > 0.0, "Go world result was not applied"):
		return
	scene.call("_on_tick_pressed")
	await semantic.world_updated
	if not _check(not scene.get("_is_busy"), "Environment tick left UI busy"):
		return
	input.text = "The invisible moon destroys the ancient city."
	scene.call("_on_submit_pressed")
	interpretation = await semantic.interpretation_ready
	if not _check(interpretation.get("status") == "INVALID" and execute.disabled, "Critic rejection enabled Execute"):
		return
	# Exercise a real asynchronous HTTP failure without touching provider credentials.
	semantic.error_occurred.disconnect(_failed)
	root.get_node("GameConfig").GAME_SERVER_URL += "/missing-route"
	input.text = "The ocean rises."
	scene.call("_on_submit_pressed")
	await semantic.error_occurred
	if not _check(not scene.get("_is_busy") and execute.disabled, "HTTP error left UI busy or executable"):
		return
	print("PASS: Godot generate, interpret, review, execute, tick, invalid proposal, HTTP error")
	scene.queue_free()
	await process_frame
	quit(0)
