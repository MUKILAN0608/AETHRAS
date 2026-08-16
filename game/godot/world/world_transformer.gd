class_name WorldTransformer
extends RefCounted

## Client-side read-only helper — actual transformation runs on Go server.
## Used for local display calculations only.

static func describe_transform(transform: Dictionary) -> String:
	var lines: PackedStringArray = []
	var action: Dictionary = transform.get("action", {})
	lines.append("ACTION: %s" % action.get("action", "NONE"))
	lines.append("TARGET: %s" % action.get("target", "NONE"))
	for step in transform.get("causal_chain", []):
		lines.append("  → %s" % step)
	return "\n".join(lines)
