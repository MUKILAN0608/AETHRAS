package world

import (
	"fmt"
	"math/rand"
)

// StructuredAction is a validated action from the AI parser.
type StructuredAction struct {
	Intent     string  `json:"intent"`
	Action     string  `json:"action"`
	Target     string  `json:"target"`
	Source     string  `json:"source"`
	Intensity  float64 `json:"intensity"`
	Magnitude  float64 `json:"magnitude"`
	Confidence float64 `json:"confidence"`
	Demo       bool    `json:"demo"`
}

// TransformResult contains world changes from an action.
type TransformResult struct {
	Action      StructuredAction `json:"action"`
	AffectedIDs []string         `json:"affected_ids"`
	Events      []WorldEvent     `json:"events"`
	CausalChain []string         `json:"causal_chain"`
	WorldState  *WorldState      `json:"world_state"`
	VisualHints []string         `json:"visual_hints"`
}

// Transformer applies structured actions to world state deterministically.
type Transformer struct {
	rules *Rules
}

func NewTransformer() *Transformer {
	return &Transformer{rules: NewRules()}
}

func (t *Transformer) Apply(ws *WorldState, action StructuredAction, actor string, prompt string) TransformResult {
	ws.Turn++
	result := TransformResult{
		Action:      action,
		AffectedIDs: []string{},
		Events:      []WorldEvent{},
		CausalChain: []string{},
		VisualHints: []string{},
	}

	if action.Intensity <= 0 {
		action.Intensity = 0.8
	}
	if action.Magnitude <= 0 {
		action.Magnitude = action.Intensity
	}

	switch action.Action {
	case "FLOOD":
		result = t.applyFlood(ws, action, result)
	case "FIRE":
		result = t.applyFire(ws, action, result)
	case "MEMORY_DECAY", "MEMORY_REMEMBER":
		result = t.applyMemoryEvent(ws, action, result)
	case "CREATE":
		result = t.applyCreate(ws, action, result)
	case "DESTROY":
		result = t.applyDestroy(ws, action, result)
	case "TRANSFORM":
		result = t.applyTransform(ws, action, result)
	case "STORM":
		result = t.applyStorm(ws, action, result)
	default:
		result.CausalChain = append(result.CausalChain, "NO_OP: unknown action")
	}

	processor := NewEventProcessor()
	result.Events = append(result.Events, processor.ProcessQueue(ws, result.Events)...)

	newStates := make(map[string]interface{})
	for _, id := range result.AffectedIDs {
		if e, ok := ws.Entities[id]; ok {
			newStates[id] = CloneEntityState(e)
		}
	}
	ws.History = append(ws.History, HistoryEntry{
		Turn:        ws.Turn,
		Actor:       actor,
		Prompt:      prompt,
		Action:      action.Action,
		AffectedIDs: result.AffectedIDs,
		NewState:    newStates,
		CausalChain: result.CausalChain,
	})

	ws.CausalHistory = append(ws.CausalHistory, CausalEvent{
		ID: fmtID("causal", ws.Turn), Turn: ws.Turn, Actor: actor,
		Prompt: prompt, Action: action.Action, TargetIDs: result.AffectedIDs, Chain: result.CausalChain,
	})

	result.WorldState = ws
	return result
}

func (t *Transformer) applyFlood(ws *WorldState, action StructuredAction, result TransformResult) TransformResult {
	result.CausalChain = append(result.CausalChain, "FLOOD_STARTED")
	ws.EnvironmentalState.WaterLevel += action.Intensity * 0.8
	ws.EnvironmentalState.Weather = "rain"
	ws.EnvironmentalState.Visibility -= 0.1 * action.Intensity
	result.VisualHints = append(result.VisualHints, "water", "flood")

	targets := t.resolveTargets(ws, action.Target, "fortress", "city", "ocean")
	for _, id := range targets {
		e := ws.Entities[id]
		prevIntegrity := e.Properties["structural_integrity"]
		if prevIntegrity == 0 {
			prevIntegrity = e.Properties["integrity"]
		}
		if prevIntegrity == 0 {
			prevIntegrity = 1.0
		}
		e.Properties["structural_integrity"] = prevIntegrity - 0.25*action.Intensity
		e.Properties["defense"] = e.Properties["defense"] - 22*action.Intensity
		e.State["flooded"] = 1.0
		e.State["movement_speed"] = 0.65
		e.Health -= 15 * action.Intensity
		e.LastModifiedTurn = ws.Turn
		ws.Entities[id] = e
		result.AffectedIDs = append(result.AffectedIDs, id)
		result.CausalChain = append(result.CausalChain, fmt.Sprintf("%s flooded", e.Name))
	}

	for i := range ws.Regions {
		if ws.Regions[i].Type == "plain" || ws.Regions[i].Type == "valley" {
			ws.Regions[i].Properties["accessibility"] = 0.3
			result.CausalChain = append(result.CausalChain, "roads become inaccessible")
		}
	}

	result.Events = append(result.Events, WorldEvent{
		ID: fmtID("event", ws.Turn), Type: "FLOOD", Intensity: action.Intensity, Turn: ws.Turn,
	})
	return result
}

func (t *Transformer) applyFire(ws *WorldState, action StructuredAction, result TransformResult) TransformResult {
	result.CausalChain = append(result.CausalChain, "FIRE_STARTED")
	ws.EnvironmentalState.FireSpread = action.Intensity * 0.6
	ws.EnvironmentalState.Visibility -= 0.2 * action.Intensity
	ws.EnvironmentalState.AtmosphericFX = "smoke"
	result.VisualHints = append(result.VisualHints, "fire", "smoke")

	targets := t.resolveTargets(ws, action.Target, "forest")
	for _, id := range targets {
		e := ws.Entities[id]
		e.Properties["vegetation"] -= 0.4 * action.Intensity
		e.Properties["density"] -= 0.3 * action.Intensity
		e.State["burning"] = 1.0
		e.Health -= 30 * action.Intensity
		e.LastModifiedTurn = ws.Turn
		if e.Properties["vegetation"] < 0.2 {
			e.Type = "ruins"
			e.SemanticTags = append(e.SemanticTags, "burned")
			result.CausalChain = append(result.CausalChain, "FOREST → RUINS")
		}
		ws.Entities[id] = e
		result.AffectedIDs = append(result.AffectedIDs, id)
	}

	for id, e := range ws.Entities {
		if e.Type == "forest" && !contains(result.AffectedIDs, id) {
			for _, affected := range result.AffectedIDs {
				if Distance(e.Position, ws.Entities[affected].Position) < 8 {
					e.State["burning"] = 0.5
					e.Properties["vegetation"] -= 0.2
					ws.Entities[id] = e
					result.AffectedIDs = append(result.AffectedIDs, id)
					result.CausalChain = append(result.CausalChain, "NEARBY REGION IGNITES")
					break
				}
			}
		}
	}

	result.Events = append(result.Events, WorldEvent{
		ID: fmtID("event", ws.Turn), Type: "FIRE", Intensity: action.Intensity, Turn: ws.Turn,
	})
	return result
}

func (t *Transformer) applyMemoryEvent(ws *WorldState, action StructuredAction, result TransformResult) TransformResult {
	result.VisualHints = append(result.VisualHints, "memory", "semantic")
	targets := t.resolveTargets(ws, action.Target, "mountain", "city")

	if action.Action == "MEMORY_DECAY" {
		result.CausalChain = append(result.CausalChain, "MEMORY_DECAY")
		for _, id := range targets {
			e := ws.Entities[id]
			e.Properties["memory"] -= action.Magnitude
			e.State["memory_weakened"] = 1.0
			e.LastModifiedTurn = ws.Turn
			ws.Entities[id] = e
			result.AffectedIDs = append(result.AffectedIDs, id)
		}
		for i := range ws.Relationships {
			ws.Relationships[i].Strength -= action.Magnitude * 0.2
			if ws.Relationships[i].Strength < 0.2 {
				ws.Relationships[i].Active = false
				result.CausalChain = append(result.CausalChain, "relationship decayed")
			}
		}
	} else {
		result.CausalChain = append(result.CausalChain, "MEMORY_REMEMBER")
		for _, id := range targets {
			e := ws.Entities[id]
			e.Properties["shape_shift"] = action.Magnitude
			e.Properties["memory"] = 1.0
			e.State["lie_detected"] = 1.0
			e.Position.Y += 2 * action.Magnitude
			e.LastModifiedTurn = ws.Turn
			ws.Entities[id] = e
			result.AffectedIDs = append(result.AffectedIDs, id)
			ws.Relationships = append(ws.Relationships, Relation{
				ID: fmtID("rel", ws.Turn), FromID: id, ToID: id,
				Type: "remembers_lie", Strength: action.Magnitude, Active: true,
			})
		}
	}

	result.Events = append(result.Events, WorldEvent{
		ID: fmtID("event", ws.Turn), Type: action.Action, Intensity: action.Magnitude, Turn: ws.Turn,
	})
	return result
}

func (t *Transformer) applyCreate(ws *WorldState, action StructuredAction, result TransformResult) TransformResult {
	gen := NewGenerator()
	rng := rand.New(rand.NewSource(ws.Seed + int64(ws.Turn)))
	entity := gen.createEntity(ws, action.Target, rng, Vector3{0, 0, 0}, "player")
	entity.CreatedAtTurn = ws.Turn
	ws.Entities[entity.ID] = entity
	result.AffectedIDs = append(result.AffectedIDs, entity.ID)
	result.CausalChain = append(result.CausalChain, "ENTITY_CREATED:"+entity.Type)
	result.VisualHints = append(result.VisualHints, "creation")
	return result
}

func (t *Transformer) applyDestroy(ws *WorldState, action StructuredAction, result TransformResult) TransformResult {
	targets := t.resolveTargets(ws, action.Target, action.Target)
	for _, id := range targets {
		e := ws.Entities[id]
		e.Health = 0
		e.Type = "ruins"
		e.Properties["integrity"] = 0.1
		e.LastModifiedTurn = ws.Turn
		ws.Entities[id] = e
		result.AffectedIDs = append(result.AffectedIDs, id)
		result.CausalChain = append(result.CausalChain, e.Name+" destroyed → RUINS")
	}
	result.VisualHints = append(result.VisualHints, "destruction")
	return result
}

func (t *Transformer) applyTransform(ws *WorldState, action StructuredAction, result TransformResult) TransformResult {
	targets := t.resolveTargets(ws, action.Target, action.Target)
	for _, id := range targets {
		e := ws.Entities[id]
		for k, v := range e.Properties {
			e.Properties[k] = v * (1 + action.Intensity*0.2)
		}
		e.LastModifiedTurn = ws.Turn
		ws.Entities[id] = e
		result.AffectedIDs = append(result.AffectedIDs, id)
	}
	result.CausalChain = append(result.CausalChain, "TRANSFORM applied")
	result.VisualHints = append(result.VisualHints, "transform")
	return result
}

func (t *Transformer) applyStorm(ws *WorldState, action StructuredAction, result TransformResult) TransformResult {
	ws.EnvironmentalState.Weather = "storm"
	ws.EnvironmentalState.WindSpeed = action.Intensity
	ws.EnvironmentalState.AtmosphericFX = "storm"
	ws.EnvironmentalState.Visibility -= 0.3
	result.CausalChain = append(result.CausalChain, "STORM intensifies")
	result.VisualHints = append(result.VisualHints, "storm")
	return result
}

func (t *Transformer) resolveTargets(ws *WorldState, target string, types ...string) []string {
	if _, exists := ws.Entities[target]; exists {
		return []string{target}
	}
	var ids []string
	target = normalizeType(target)
	for id, e := range ws.Entities {
		if normalizeType(e.Type) == target {
			ids = append(ids, id)
		}
	}
	if len(ids) == 0 {
		for _, tp := range types {
			for id, e := range ws.Entities {
				if normalizeType(e.Type) == normalizeType(tp) {
					ids = append(ids, id)
				}
			}
			if len(ids) > 0 {
				break
			}
		}
	}
	return ids
}

func normalizeType(s string) string {
	s = stringsToLower(s)
	switch s {
	case "fortress", "castle", "citadel", "keep":
		return "fortress"
	case "forest", "woods", "grove":
		return "forest"
	case "ocean", "sea", "water", "lake", "river":
		return "ocean"
	case "mountain", "peak":
		return "mountain"
	case "city", "civilization":
		return "city"
	default:
		return s
	}
}

func stringsToLower(s string) string {
	b := []byte(s)
	for i, c := range b {
		if c >= 'A' && c <= 'Z' {
			b[i] = c + 32
		}
	}
	return string(b)
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func fmtID(prefix string, turn int) string {
	return fmt.Sprintf("%s_%d", prefix, turn)
}
