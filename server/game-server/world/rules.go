package world

// Rules defines validation and transformation constraints.
type Rules struct {
	AllowedActions []string
	MaxIntensity   float64
}

func NewRules() *Rules {
	return &Rules{
		AllowedActions: []string{
			"FLOOD", "FIRE", "MEMORY_DECAY", "MEMORY_REMEMBER",
			"CREATE", "DESTROY", "TRANSFORM", "STORM", "NONE",
		},
		MaxIntensity: 1.0,
	}
}

// ValidateAction checks if a structured action is permitted.
func (r *Rules) ValidateAction(action StructuredAction) (bool, string) {
	if action.Action == "NONE" {
		return false, "action is NONE"
	}
	for _, a := range r.AllowedActions {
		if a == action.Action {
			if action.Intensity > r.MaxIntensity {
				return false, "intensity exceeds maximum"
			}
			if action.Confidence < 0.1 {
				return false, "confidence too low"
			}
			return true, ""
		}
	}
	return false, "action not in allowed set"
}

// CanSpreadFire returns whether fire can spread from source to target entity types.
func (r *Rules) CanSpreadFire(sourceType, targetType string) bool {
	return sourceType == "forest" && (targetType == "forest" || targetType == "city")
}

// CanFlood returns whether water can flood target from source.
func (r *Rules) CanFlood(sourceType, targetType string) bool {
	water := sourceType == "ocean" || sourceType == "river"
	target := targetType == "fortress" || targetType == "city" || targetType == "plain"
	return water && target
}
