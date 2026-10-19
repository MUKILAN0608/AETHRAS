package world

import "math"

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
	if math.IsNaN(action.Intensity) || math.IsInf(action.Intensity, 0) || action.Intensity < 0 ||
		math.IsNaN(action.Magnitude) || math.IsInf(action.Magnitude, 0) || action.Magnitude < 0 || action.Magnitude > r.MaxIntensity ||
		math.IsNaN(action.Confidence) || math.IsInf(action.Confidence, 0) || action.Confidence > 1 {
		return false, "invalid numeric action limits"
	}
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
