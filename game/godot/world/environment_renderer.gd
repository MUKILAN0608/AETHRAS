extends Node3D
class_name EnvironmentRenderer

## Visualizes environmental state — water, fire, storm, lighting.

var _water_plane: MeshInstance3D
var _fire_particles: GPUParticles3D
var _flood_particles: GPUParticles3D
var _memory_particles: GPUParticles3D
var _directional_light: DirectionalLight3D = null


func setup(lights: DirectionalLight3D, _env: WorldEnvironment = null) -> void:
	_directional_light = lights
	_water_plane = _create_water_plane()
	_fire_particles = _create_fire_particles()
	_flood_particles = _create_flood_particles()
	_memory_particles = _create_memory_particles()
	add_child(_water_plane)
	add_child(_fire_particles)
	add_child(_flood_particles)
	add_child(_memory_particles)


func apply_environment(env_state: Dictionary, visual_hints: Array = []) -> void:
	var water_level := float(env_state.get("water_level", 0))
	var weather: String = str(env_state.get("weather", "clear"))
	var visibility := float(env_state.get("visibility", 1.0))

	_water_plane.visible = water_level > 0.01
	_water_plane.position.y = water_level * 2.0
	var water_mat: StandardMaterial3D = _water_plane.get_surface_override_material(0)
	if water_mat:
		water_mat.albedo_color.a = clampf(0.3 + water_level * 0.4, 0.3, 0.8)

	_flood_particles.emitting = "flood" in visual_hints or water_level > 0.3
	_fire_particles.emitting = "fire" in visual_hints or float(env_state.get("fire_spread", 0)) > 0.1
	_memory_particles.emitting = "memory" in visual_hints

	if _directional_light:
		match weather:
			"storm":
				_directional_light.light_energy = 0.3
				_directional_light.light_color = Color(0.4, 0.45, 0.6)
			"rain", "flood":
				_directional_light.light_energy = 0.45
				_directional_light.light_color = Color(0.5, 0.6, 0.85)
			"clouds":
				_directional_light.light_energy = 0.65
				_directional_light.light_color = Color(0.85, 0.85, 0.9)
			_:
				_directional_light.light_energy = 1.0
				_directional_light.light_color = Color(1.0, 0.95, 0.9)
		_directional_light.light_energy *= visibility


func _create_water_plane() -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(28, 0.15, 28)
	mi.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = Color(0.1, 0.4, 0.9, 0.45)
	mi.set_surface_override_material(0, mat)
	mi.visible = false
	return mi


func _create_fire_particles() -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.amount = 48
	p.lifetime = 1.5
	p.emitting = false
	p.position = Vector3(0, 1, 0)
	return p


func _create_flood_particles() -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.amount = 64
	p.lifetime = 2.0
	p.emitting = false
	return p


func _create_memory_particles() -> GPUParticles3D:
	var p := GPUParticles3D.new()
	p.amount = 32
	p.lifetime = 3.0
	p.emitting = false
	return p
