package world

import (
	"fmt"
	"math"
	"math/rand"
	"strings"
)

// Scenario defines a procedurally generatable world template.
type Scenario struct {
	ID          string   `json:"id"`
	Description string   `json:"description"`
	Keywords    []string `json:"keywords"`
}

// Scenarios are the three required Phase 2 test scenarios.
var Scenarios = []Scenario{
	{
		ID:          "scenario_1",
		Description: "A fortress stands between a living forest and a restless ocean.",
		Keywords:    []string{"fortress", "forest", "ocean"},
	},
	{
		ID:          "scenario_2",
		Description: "A ruined city floats above a world of endless storms.",
		Keywords:    []string{"city", "ruins", "storm", "float"},
	},
	{
		ID:          "scenario_3",
		Description: "A civilization survives around a mountain that changes shape whenever someone lies.",
		Keywords:    []string{"civilization", "mountain", "memory", "lie"},
	},
}

// GenerateRequest is the input for procedural world generation.
type GenerateRequest struct {
	ScenarioID string  `json:"scenario_id"`
	Scenario   string  `json:"scenario"`
	Seed       int64   `json:"seed"`
	Difficulty float64 `json:"difficulty"`
	WorldSize  float64 `json:"world_size"`
}

// Generator creates procedural worlds from scenario + seed.
type Generator struct{}

func NewGenerator() *Generator {
	return &Generator{}
}

func (g *Generator) Generate(req GenerateRequest) *WorldState {
	scenario := g.resolveScenario(req)
	seed := req.Seed
	if seed == 0 {
		seed = 42
	}
	rng := rand.New(rand.NewSource(seed))
	arena := req.WorldSize
	if arena <= 0 {
		arena = 32.0
	}

	ws := NewWorldState(fmt.Sprintf("world_%d", seed), seed, scenario.ID)
	ws.WorldParameters["arena_size"] = arena
	ws.WorldParameters["difficulty"] = req.Difficulty
	if ws.WorldParameters["difficulty"] <= 0 {
		ws.WorldParameters["difficulty"] = 0.5
	}

	g.generateTerrain(ws, rng, arena)
	g.generateFromScenario(ws, scenario, rng, arena)
	g.generateRelationships(ws, rng)
	g.placeActors(ws, rng, arena)

	ws.SemanticState["scenario_description"] = scenario.Description
	ws.SemanticState["generation_complete"] = true
	return ws
}

func (g *Generator) resolveScenario(req GenerateRequest) Scenario {
	if req.ScenarioID != "" {
		for _, s := range Scenarios {
			if s.ID == req.ScenarioID {
				return s
			}
		}
	}
	text := strings.ToLower(req.Scenario)
	for _, s := range Scenarios {
		if strings.Contains(text, strings.ToLower(s.ID)) {
			return s
		}
		for _, kw := range s.Keywords {
			if strings.Contains(text, kw) {
				return s
			}
		}
	}
	// Default: derive keywords from free-text scenario
	return Scenario{
		ID:          "custom",
		Description: req.Scenario,
		Keywords:    extractKeywords(text),
	}
}

func extractKeywords(text string) []string {
	candidates := []string{"ocean", "forest", "fortress", "mountain", "city", "storm", "civilization", "ruins", "memory"}
	var found []string
	for _, c := range candidates {
		if strings.Contains(text, c) {
			found = append(found, c)
		}
	}
	if len(found) == 0 {
		found = []string{"plain", "core"}
	}
	return found
}

func (g *Generator) generateTerrain(ws *WorldState, rng *rand.Rand, arena float64) {
	types := []string{"plain", "valley", "hill", "water_basin", "cliff"}
	for i := 0; i < 4+rng.Intn(3); i++ {
		angle := rng.Float64() * 6.28
		dist := rng.Float64() * arena * 0.35
		ws.Regions = append(ws.Regions, Region{
			ID:   fmt.Sprintf("region_%d", i),
			Name: fmt.Sprintf("Region %d", i),
			Type: types[rng.Intn(len(types))],
			Center: Vector3{
				X: math.Cos(angle) * dist,
				Y: 0,
				Z: math.Sin(angle) * dist,
			},
			Radius: 4 + rng.Float64()*6,
			Properties: map[string]float64{
				"height":     rng.Float64() * 4,
				"moisture":   rng.Float64(),
				"vegetation": rng.Float64(),
			},
			SemanticTags: []string{types[rng.Intn(len(types))]},
		})
	}
}

func (g *Generator) generateFromScenario(ws *WorldState, scenario Scenario, rng *rand.Rand, arena float64) {
	entityCount := 3 + rng.Intn(4)
	usedTypes := map[string]bool{}

	// Always generate from scenario keywords first
	for i, kw := range scenario.Keywords {
		eType := keywordToEntityType(kw)
		if usedTypes[eType] && rng.Float64() > 0.5 {
			continue
		}
		usedTypes[eType] = true
		pos := scatterPosition(rng, arena, float64(i))
		entity := g.createEntity(ws, eType, rng, pos, "generator")
		ws.Entities[entity.ID] = entity
	}

	// Fill with procedural extras based on seed — NOT fixed map
	for len(ws.Entities) < entityCount {
		types := []string{"forest", "ocean", "fortress", "mountain", "city", "ruins", "core", "bridge", "river"}
		eType := types[rng.Intn(len(types))]
		if usedTypes[eType] && rng.Float64() > 0.3 {
			continue
		}
		usedTypes[eType] = true
		pos := scatterPosition(rng, arena, float64(len(ws.Entities)))
		entity := g.createEntity(ws, eType, rng, pos, "generator")
		ws.Entities[entity.ID] = entity
	}
}

func keywordToEntityType(kw string) string {
	switch kw {
	case "forest", "ocean", "fortress", "mountain", "city", "storm", "civilization", "ruins", "memory", "lie", "float":
		if kw == "storm" {
			return "storm"
		}
		if kw == "civilization" {
			return "city"
		}
		if kw == "memory" || kw == "lie" {
			return "mountain"
		}
		if kw == "float" {
			return "ruins"
		}
		return kw
	default:
		return kw
	}
}

func (g *Generator) createEntity(ws *WorldState, eType string, rng *rand.Rand, pos Vector3, createdBy string) Entity {
	id := fmt.Sprintf("entity_%03d", len(ws.Entities)+1)
	name := generateName(eType, rng)
	props := defaultProperties(eType)
	scale := Vector3{1, 1, 1}
	switch eType {
	case "mountain":
		scale = Vector3{2 + rng.Float64()*2, 3 + rng.Float64()*3, 2 + rng.Float64()*2}
	case "fortress", "city", "ruins":
		scale = Vector3{1.5 + rng.Float64(), 2 + rng.Float64()*2, 1.5 + rng.Float64()}
	case "ocean", "river":
		scale = Vector3{6 + rng.Float64()*4, 0.3, 6 + rng.Float64()*4}
		pos.Y = -0.2
	case "forest":
		scale = Vector3{3 + rng.Float64()*2, 1.5, 3 + rng.Float64()*2}
	}

	return Entity{
		ID:       id,
		Type:     eType,
		Name:     name,
		Position: pos,
		Scale:    scale,
		Properties: props,
		State: map[string]float64{
			"active": 1.0,
		},
		SemanticTags:     semanticTagsForType(eType),
		Health:           100,
		Importance:       0.5 + rng.Float64()*0.5,
		CreatedBy:        createdBy,
		CreatedAtTurn:    0,
		LastModifiedTurn: 0,
	}
}

func defaultProperties(eType string) map[string]float64 {
	switch eType {
	case "fire":
		return map[string]float64{"temperature": 800, "spread": 0.5, "consumes": 1}
	case "ocean", "river":
		return map[string]float64{"volume": 100, "flow": 0.3, "floods": 1}
	case "forest":
		return map[string]float64{"vegetation": 0.9, "flammability": 0.8, "density": 0.7}
	case "fortress":
		return map[string]float64{"defense": 85, "height": 42, "structural_integrity": 1.0, "entrances": 2}
	case "mountain":
		return map[string]float64{"height": 50, "memory": 1.0, "shape_shift": 0.0}
	case "city", "ruins":
		return map[string]float64{"population": 50, "elevation": 0, "integrity": 0.8}
	case "storm":
		return map[string]float64{"intensity": 0.7, "lightning": 0.5}
	case "core":
		return map[string]float64{"power": 100, "awareness": 1.0}
	default:
		return map[string]float64{"integrity": 1.0}
	}
}

func semanticTagsForType(eType string) []string {
	tags := map[string][]string{
		"ocean":    {"water", "environmental", "flood_source"},
		"forest":   {"vegetation", "flammable", "living"},
		"fortress": {"defensive", "ancient", "strategic"},
		"mountain": {"memory", "geological", "shape_changing"},
		"city":     {"civilization", "urban", "population"},
		"ruins":    {"ancient", "floating", "decayed"},
		"storm":    {"weather", "destructive", "atmospheric"},
		"core":     {"ai", "strategic", "central"},
		"river":    {"water", "flow", "flood_source"},
		"bridge":   {"connection", "crossing"},
	}
	if t, ok := tags[eType]; ok {
		return t
	}
	return []string{"generic"}
}

func generateName(eType string, rng *rand.Rand) string {
	prefixes := map[string][]string{
		"fortress": {"Citadel of Echoes", "Iron Hold", "Veil Fortress"},
		"forest":   {"Whisperwood", "Living Grove", "Ember Canopy"},
		"ocean":    {"Restless Deep", "Dying Ocean", "Tide Expanse"},
		"mountain": {"Memory Peak", "The Liar's Spine", "Traveler's Mount"},
		"city":     {"Floating Ruin", "Storm Haven", "Last City"},
		"ruins":    {"Sky Ruins", "Fallen Spire", "Echo City"},
	}
	if names, ok := prefixes[eType]; ok {
		return names[rng.Intn(len(names))]
	}
	return fmt.Sprintf("%s %d", eType, rng.Intn(100))
}

func scatterPosition(rng *rand.Rand, arena float64, index float64) Vector3 {
	angle := (index * 2.1) + rng.Float64()*1.5
	r := arena * 0.15 * (0.5 + rng.Float64())
	return Vector3{
		X: math.Cos(angle) * r,
		Y: 0,
		Z: math.Sin(angle) * r,
	}
}

func (g *Generator) generateRelationships(ws *WorldState, rng *rand.Rand) {
	ids := make([]string, 0, len(ws.Entities))
	for id := range ws.Entities {
		ids = append(ids, id)
	}
	if len(ids) < 2 {
		return
	}

	relationTypes := []string{"surrounds", "near", "blocks", "threatens", "protects", "connects"}
	for i := 0; i < len(ids)-1 && i < 6; i++ {
		from := ws.Entities[ids[i]]
		to := ws.Entities[ids[(i+1)%len(ids)]]
		relType := relationTypes[rng.Intn(len(relationTypes))]
		ws.Relationships = append(ws.Relationships, Relation{
			ID:       fmt.Sprintf("rel_%d", i),
			FromID:   from.ID,
			ToID:     to.ID,
			Type:     relType,
			Strength: 0.3 + rng.Float64()*0.7,
			Active:   true,
		})
	}
}

func (g *Generator) placeActors(ws *WorldState, rng *rand.Rand, arena float64) {
	human := g.createEntity(ws, "human_player", rng, Vector3{-arena * 0.2, 0.5, arena * 0.15}, "system")
	human.SemanticTags = []string{"player", "human"}
	human.Properties = map[string]float64{"movement": 1.0}
	ws.Entities[human.ID] = human

	ai := g.createEntity(ws, "ai_agent", rng, Vector3{arena * 0.2, 0.5, -arena * 0.15}, "system")
	ai.SemanticTags = []string{"player", "ai"}
	ai.Properties = map[string]float64{"movement": 1.0}
	ws.Entities[ai.ID] = ai

	core := g.createEntity(ws, "core", rng, Vector3{0, 1, 0}, "system")
	core.Name = "AI Core"
	core.Importance = 1.0
	ws.Entities[core.ID] = core
}
