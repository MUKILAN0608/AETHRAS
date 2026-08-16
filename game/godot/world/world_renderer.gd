extends Node3D
class_name WorldRenderer

var _entity_renderer: EntityRenderer = EntityRenderer.new()
var _environment_renderer: EnvironmentRenderer = EnvironmentRenderer.new()
var _relation_lines: Node3D = Node3D.new()
var _terrain: TerrainGenerator = TerrainGenerator.new()

var _entity_container: Node3D
var _directional_light: DirectionalLight3D


func setup(entity_container: Node3D, directional_light: DirectionalLight3D) -> void:
	_entity_container = entity_container
	_directional_light = directional_light
	add_child(_terrain)
	add_child(_entity_renderer)
	add_child(_environment_renderer)
	add_child(_relation_lines)
	_entity_renderer.setup(entity_container)
	_environment_renderer.setup(directional_light)


func render_world(state, affected_ids: Array = [], visual_hints: Array = []) -> void:
	_terrain.generate(state.seed, state.regions)
	_entity_renderer.render_entities(state, affected_ids)
	_environment_renderer.apply_environment(state.environmental_state, visual_hints)
	_render_relationships(state)


func _render_relationships(state) -> void:
	for child in _relation_lines.get_children():
		child.queue_free()

	for rel_data in state.relationships:
		var rel = rel_data
		if not rel.active:
			continue
		var from_node = _entity_renderer.get_entity_node(rel.from_id)
		var to_node = _entity_renderer.get_entity_node(rel.to_id)
		if from_node and to_node:
			_draw_connection(from_node.global_position, to_node.global_position, rel.strength)


func _draw_connection(from: Vector3, to: Vector3, strength: float) -> void:
	var mesh_instance := MeshInstance3D.new()
	var mesh := ImmediateMesh.new()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.3, 0.7, 1.0, clampf(strength, 0.2, 0.8))
	mat.emission_enabled = true
	mat.emission = Color(0.2, 0.5, 0.9)
	mat.emission_energy_multiplier = strength
	mesh.surface_begin(Mesh.PRIMITIVE_LINES, mat)
	mesh.surface_add_vertex(from + Vector3(0, 1, 0))
	mesh.surface_add_vertex(to + Vector3(0, 1, 0))
	mesh.surface_end()
	mesh_instance.mesh = mesh
	_relation_lines.add_child(mesh_instance)
