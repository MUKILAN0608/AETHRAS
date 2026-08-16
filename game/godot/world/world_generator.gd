extends Node3D
class_name TerrainGenerator

## Procedural terrain mesh from world seed — deterministic, lightweight arena.

@export var arena_size: float = 32.0
@export var resolution: int = 32

var _mesh_instance: MeshInstance3D


func _ready() -> void:
	_mesh_instance = MeshInstance3D.new()
	add_child(_mesh_instance)


func generate(seed_value: int, regions: Array) -> void:
	var mesh := ArrayMesh.new()
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()

	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value

	var step := arena_size / float(resolution)
	var half := arena_size * 0.5

	for z in range(resolution):
		for x in range(resolution):
			var wx := -half + x * step
			var wz := -half + z * step
			var h := _height_at(wx, wz, rng, regions)
			vertices.append(Vector3(wx, h, wz))
			normals.append(Vector3.UP)
			uvs.append(Vector2(float(x) / resolution, float(z) / resolution))

	for z in range(resolution - 1):
		for x in range(resolution - 1):
			var i := z * resolution + x
			indices.append(i)
			indices.append(i + resolution)
			indices.append(i + 1)
			indices.append(i + 1)
			indices.append(i + resolution)
			indices.append(i + resolution + 1)

	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)

	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.22, 0.32, 0.18)
	mat.roughness = 0.9
	_mesh_instance.mesh = mesh
	_mesh_instance.set_surface_override_material(0, mat)


func _height_at(x: float, z: float, rng: RandomNumberGenerator, regions: Array) -> float:
	var h := sin(x * 0.15) * cos(z * 0.12) * 0.5
	h += rng.randf_range(-0.1, 0.1)
	for region in regions:
		if region is Dictionary:
			var center: Dictionary = region.get("center", {})
			var cx := float(center.get("x", 0))
			var cz := float(center.get("z", 0))
			var radius := float(region.get("radius", 4))
			var dist := Vector2(x - cx, z - cz).length()
			if dist < radius:
				var props: Dictionary = region.get("properties", {})
				h += float(props.get("height", 0)) * (1.0 - dist / radius)
	return h
