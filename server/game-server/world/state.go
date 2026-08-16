package world

import "math"

// Vector3 represents a 3D position or scale in world space.
type Vector3 struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
	Z float64 `json:"z"`
}

// Entity is a generic world object with semantic meaning.
type Entity struct {
	ID               string             `json:"id"`
	Type             string             `json:"type"`
	Name             string             `json:"name"`
	Position         Vector3            `json:"position"`
	Scale            Vector3            `json:"scale"`
	Properties       map[string]float64 `json:"properties"`
	State            map[string]float64 `json:"state"`
	SemanticTags     []string           `json:"semantic_tags"`
	Relationships    []string           `json:"relationships"`
	Health           float64            `json:"health"`
	Importance       float64            `json:"importance"`
	CreatedBy        string             `json:"created_by"`
	CreatedAtTurn    int                `json:"created_at_turn"`
	LastModifiedTurn int                `json:"last_modified_turn"`
}

// Relation describes a semantic link between two entities.
type Relation struct {
	ID       string  `json:"id"`
	FromID   string  `json:"from_id"`
	ToID     string  `json:"to_id"`
	Type     string  `json:"type"`
	Strength float64 `json:"strength"`
	Active   bool    `json:"active"`
}

// Region is a procedural area within the world arena.
type Region struct {
	ID           string             `json:"id"`
	Name         string             `json:"name"`
	Type         string             `json:"type"`
	Center       Vector3            `json:"center"`
	Radius       float64            `json:"radius"`
	Properties   map[string]float64 `json:"properties"`
	EntityIDs    []string           `json:"entity_ids"`
	SemanticTags []string           `json:"semantic_tags"`
}

// EnvironmentalState tracks lightweight continuous simulation.
type EnvironmentalState struct {
	Weather       string  `json:"weather"`
	TimeOfDay     float64 `json:"time_of_day"`
	WaterLevel    float64 `json:"water_level"`
	Temperature   float64 `json:"temperature"`
	WindSpeed     float64 `json:"wind_speed"`
	Visibility    float64 `json:"visibility"`
	FireSpread    float64 `json:"fire_spread"`
	AtmosphericFX string  `json:"atmospheric_fx"`
}

// WorldEvent is an active or queued world event.
type WorldEvent struct {
	ID         string             `json:"id"`
	Type       string             `json:"type"`
	SourceID   string             `json:"source_id"`
	TargetID   string             `json:"target_id"`
	Intensity  float64            `json:"intensity"`
	Turn       int                `json:"turn"`
	Properties map[string]float64 `json:"properties"`
	Processed  bool               `json:"processed"`
}

// CausalEvent records cascading consequence chains.
type CausalEvent struct {
	ID        string   `json:"id"`
	Turn      int      `json:"turn"`
	Actor     string   `json:"actor"`
	Prompt    string   `json:"prompt"`
	Action    string   `json:"action"`
	TargetIDs []string `json:"target_ids"`
	Chain     []string `json:"chain"`
}

// HistoryEntry stores world memory for research replay.
type HistoryEntry struct {
	Turn          int                    `json:"turn"`
	Actor         string                 `json:"actor"`
	Prompt        string                 `json:"prompt"`
	Action        string                 `json:"action"`
	AffectedIDs   []string               `json:"affected_entities"`
	PreviousState map[string]interface{} `json:"previous_state"`
	NewState      map[string]interface{} `json:"new_state"`
	CausalChain   []string               `json:"causal_chain"`
}

// WorldState is the canonical representation of the dynamic semantic world.
type WorldState struct {
	WorldID            string                 `json:"world_id"`
	Seed               int64                  `json:"seed"`
	Turn               int                    `json:"turn"`
	ScenarioID         string                 `json:"scenario_id"`
	Entities           map[string]Entity      `json:"entities"`
	Relationships      []Relation             `json:"relationships"`
	Regions            []Region               `json:"regions"`
	EnvironmentalState EnvironmentalState     `json:"environmental_state"`
	ActiveEvents       []WorldEvent           `json:"active_events"`
	CausalHistory      []CausalEvent          `json:"causal_history"`
	SemanticState      map[string]interface{} `json:"semantic_state"`
	WorldParameters    map[string]float64     `json:"world_parameters"`
	History            []HistoryEntry         `json:"history"`
}

// NewWorldState creates an empty world state with defaults.
func NewWorldState(worldID string, seed int64, scenarioID string) *WorldState {
	return &WorldState{
		WorldID:    worldID,
		Seed:       seed,
		Turn:       0,
		ScenarioID: scenarioID,
		Entities:   make(map[string]Entity),
		Relationships: []Relation{},
		Regions:    []Region{},
		EnvironmentalState: EnvironmentalState{
			Weather:     "clear",
			TimeOfDay:   0.35,
			WaterLevel:  0.0,
			Temperature: 18.0,
			WindSpeed:   0.2,
			Visibility:  1.0,
			FireSpread:  0.0,
			AtmosphericFX: "none",
		},
		ActiveEvents:  []WorldEvent{},
		CausalHistory: []CausalEvent{},
		SemanticState: make(map[string]interface{}),
		WorldParameters: map[string]float64{
			"arena_size": 32.0,
			"difficulty": 0.5,
		},
		History: []HistoryEntry{},
	}
}

// CloneEntityState returns a shallow copy of entity state for history.
func CloneEntityState(e Entity) map[string]interface{} {
	props := make(map[string]float64, len(e.Properties))
	for k, v := range e.Properties {
		props[k] = v
	}
	state := make(map[string]float64, len(e.State))
	for k, v := range e.State {
		state[k] = v
	}
	return map[string]interface{}{
		"health":     e.Health,
		"properties": props,
		"state":      state,
	}
}

// FindEntitiesByType returns all entities matching a semantic type.
func (ws *WorldState) FindEntitiesByType(entityType string) []Entity {
	var result []Entity
	for _, e := range ws.Entities {
		if e.Type == entityType {
			result = append(result, e)
		}
	}
	return result
}

// FindEntityBySemanticTag returns first entity containing a tag.
func (ws *WorldState) FindEntityBySemanticTag(tag string) *Entity {
	for id, e := range ws.Entities {
		for _, t := range e.SemanticTags {
			if t == tag {
				copy := e
				copy.ID = id
				return &copy
			}
		}
	}
	return nil
}

// FindEntityByID returns entity by id.
func (ws *WorldState) FindEntityByID(id string) *Entity {
	if e, ok := ws.Entities[id]; ok {
		return &e
	}
	return nil
}

// Distance returns Euclidean distance between two entities.
func Distance(a, b Vector3) float64 {
	dx := a.X - b.X
	dy := a.Y - b.Y
	dz := a.Z - b.Z
	return math.Sqrt(dx*dx + dy*dy + dz*dz)
}
