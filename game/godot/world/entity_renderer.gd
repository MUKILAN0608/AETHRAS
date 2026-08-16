extends Node3D
class_name EntityRenderer

var _entity_nodes: Dictionary = {}
var _container: Node3D


func setup(container: Node3D) -> void:
	_container = container


func render_entities(state, affected_ids: Array = []) -> void:
	for id in state.entities:
		var entity = state.entities[id]
		if id in _entity_nodes:
			_update_entity_node(id, entity, id in affected_ids)
		else:
			_create_entity_node(id, entity)

	for id in _entity_nodes.keys():
		if id not in state.entities:
			_entity_nodes[id].queue_free()
			_entity_nodes.erase(id)


func _create_entity_node(id: String, entity) -> void:
	var mesh_instance := MeshInstance3D.new()
	mesh_instance.name = "entity_%s" % id

	match entity.type:
		"ocean", "river":
			var plane := BoxMesh.new()
			plane.size = WorldRules.mesh_scale_for(entity) * Vector3(1, 0.2, 1)
			mesh_instance.mesh = plane
		"core":
			var sphere := SphereMesh.new()
			sphere.radius = 0.6
			sphere.height = 1.2
			mesh_instance.mesh = sphere
		"mountain":
			var box := BoxMesh.new()
			box.size = WorldRules.mesh_scale_for(entity)
			mesh_instance.mesh = box
		_:
			var box := BoxMesh.new()
			box.size = WorldRules.mesh_scale_for(entity) * Vector3(0.8, 1.2, 0.8)
			mesh_instance.mesh = box

	var mat := StandardMaterial3D.new()
	mat.albedo_color = WorldRules.color_for_type(entity.type)
	if entity.type == "core":
		mat.emission_enabled = true
		mat.emission = Color(0.4, 0.2, 0.8)
		mat.emission_energy_multiplier = 2.0
	if entity.state.get("burning", 0) > 0:
		mat.emission_enabled = true
		mat.emission = Color(1.0, 0.3, 0.0)
		mat.emission_energy_multiplier = 1.5
	if entity.state.get("flooded", 0) > 0:
		mat.albedo_color = mat.albedo_color.lerp(Color(0.1, 0.3, 0.7), 0.5)

	mesh_instance.set_surface_override_material(0, mat)
	mesh_instance.position = entity.position
	_container.add_child(mesh_instance)
	_entity_nodes[id] = mesh_instance


func _update_entity_node(id: String, entity, animate: bool) -> void:
	var node: MeshInstance3D = _entity_nodes[id]
	var target_pos: Vector3 = entity.position
	if entity.state.get("flooded", 0) > 0:
		target_pos.y -= 0.4 * float(entity.state.get("flooded", 0))

	if animate:
		var tween := create_tween()
		tween.tween_property(node, "position", target_pos, 1.5)
		if entity.state.get("burning", 0) > 0:
			var mat: StandardMaterial3D = node.get_surface_override_material(0)
			if mat:
				tween.parallel().tween_property(mat, "emission_energy_multiplier", 2.5, 0.5)
	else:
		node.position = target_pos

	if entity.type == "ruins":
		var mat: StandardMaterial3D = node.get_surface_override_material(0)
		if mat:
			mat.albedo_color = WorldRules.color_for_type("ruins")


func get_entity_node(id: String) -> Node3D:
	return _entity_nodes.get(id, null)
