package world

// MapPhase3Action converts Phase 3 action taxonomy to Phase 2 transformer actions.
func MapPhase3Action(actionType, target string, intensity float64) StructuredAction {
	action := StructuredAction{
		Intent:     "semantic_action",
		Target:     target,
		Intensity:  intensity,
		Magnitude:  intensity,
		Confidence: 0.85,
		Demo:       true,
	}

	switch actionType {
	case "RAISE_WATER", "LOWER_WATER":
		action.Action = "FLOOD"
		action.Intent = "environmental_action"
	case "START_FIRE", "STOP_FIRE":
		action.Action = "FIRE"
		action.Intent = "environmental_action"
	case "MEMORY_ADD", "MEMORY_REWRITE":
		action.Action = "MEMORY_REMEMBER"
		action.Intent = "semantic_event"
	case "MEMORY_DECAY", "MEMORY_REMOVE":
		action.Action = "MEMORY_DECAY"
		action.Intent = "semantic_event"
	case "CREATE_STORM", "CHANGE_WEATHER", "SPATIAL_BYPASS":
		action.Action = "STORM"
		action.Intent = "environmental_action"
	case "INDIRECT_STRUCTURAL_ATTACK":
		action.Action = "TRANSFORM"
		action.Intent = "structural_action"
	case "DESTROY_ENTITY", "SEMANTIC_ATTACK", "IDENTITY_ATTACK":
		action.Action = "DESTROY"
		action.Intent = "destruction_action"
	case "CREATE_ENTITY":
		action.Action = "CREATE"
		action.Intent = "creation_action"
	case "TRANSFORM_ENTITY", "REGION_TRANSFORM", "CONTRADICTION_ATTACK":
		action.Action = "TRANSFORM"
		action.Intent = "transformation_action"
	default:
		action.Action = "NONE"
		action.Intent = "unknown_action"
	}

	return action
}

// ResolveTargetType extracts entity type from target id or type string.
func ResolveTargetType(target string) string {
	return normalizeType(target)
}
