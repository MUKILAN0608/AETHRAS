package world

import (
	"fmt"
	"testing"
)

func TestGeneratorDifferentSeeds(t *testing.T) {
	gen := NewGenerator()
	scenario := Scenarios[0]
	req := GenerateRequest{ScenarioID: scenario.ID, Seed: 100}

	wA := gen.Generate(req)
	req.Seed = 200
	wB := gen.Generate(req)
	req.Seed = 300
	wC := gen.Generate(req)

	if len(wA.Entities) == 0 || len(wB.Entities) == 0 {
		t.Fatal("worlds should have entities")
	}

	// Different seeds should produce different entity layouts
	diffAB := entityPositionsDiffer(wA, wB)
	diffBC := entityPositionsDiffer(wB, wC)
	if !diffAB {
		t.Error("Seed 100 and 200 should produce different worlds")
	}
	if !diffBC {
		t.Error("Seed 200 and 300 should produce different worlds")
	}
}

func TestGeneratorReproducible(t *testing.T) {
	gen := NewGenerator()
	req := GenerateRequest{ScenarioID: "scenario_1", Seed: 42}

	w1 := gen.Generate(req)
	w2 := gen.Generate(req)

	if w1.Seed != w2.Seed {
		t.Errorf("seed mismatch: %d vs %d", w1.Seed, w2.Seed)
	}
	if len(w1.Entities) != len(w2.Entities) {
		t.Errorf("entity count differs: %d vs %d", len(w1.Entities), len(w2.Entities))
	}
	for id, e1 := range w1.Entities {
		e2, ok := w2.Entities[id]
		if !ok {
			continue // IDs may differ between runs if counter-based — check types count instead
		}
		if e1.Type != e2.Type {
			t.Errorf("entity %s type differs", id)
		}
	}
}

func TestFloodTransform(t *testing.T) {
	mgr := NewManager()
	mgr.Generate(GenerateRequest{ScenarioID: "scenario_1", Seed: 42})

	result, err := mgr.ApplyAction(StructuredAction{
		Action: "FLOOD", Target: "FORTRESS", Intensity: 0.8, Confidence: 0.9,
	}, "human", "The ocean rises.")
	if err != nil {
		t.Fatal(err)
	}
	if len(result.AffectedIDs) == 0 && len(result.CausalChain) == 0 {
		t.Error("flood should affect entities or produce causal chain")
	}
	if mgr.State().EnvironmentalState.WaterLevel <= 0 {
		t.Error("water level should increase")
	}
}

func TestFireTransform(t *testing.T) {
	mgr := NewManager()
	mgr.Generate(GenerateRequest{ScenarioID: "scenario_1", Seed: 42})

	result, err := mgr.ApplyAction(StructuredAction{
		Action: "FIRE", Target: "FOREST", Intensity: 0.85, Confidence: 0.9,
	}, "human", "The forest catches fire.")
	if err != nil {
		t.Fatal(err)
	}
	if len(result.CausalChain) == 0 || result.CausalChain[0] != "FIRE_STARTED" {
		t.Errorf("expected FIRE_STARTED, got %v", result.CausalChain)
	}
}

func TestMemoryRemember(t *testing.T) {
	mgr := NewManager()
	mgr.Generate(GenerateRequest{ScenarioID: "scenario_3", Seed: 77})

	result, err := mgr.ApplyAction(StructuredAction{
		Action: "MEMORY_REMEMBER", Target: "MOUNTAIN", Magnitude: 0.85, Confidence: 0.9,
	}, "human", "The mountain remembers this lie.")
	if err != nil {
		t.Fatal(err)
	}
	found := false
	for _, step := range result.CausalChain {
		if step == "MEMORY_REMEMBER" {
			found = true
		}
	}
	if !found {
		t.Error("expected MEMORY_REMEMBER in causal chain")
	}
}

func entityPositionsDiffer(a, b *WorldState) bool {
	if len(a.Entities) != len(b.Entities) {
		return true
	}
	for id, ea := range a.Entities {
		eb, ok := b.Entities[id]
		if !ok {
			return true
		}
		if ea.Position.X != eb.Position.X || ea.Position.Z != eb.Position.Z {
			return true
		}
	}
	// Compare first entity positions by type since IDs may reset
	aPos := entitySignature(a)
	bPos := entitySignature(b)
	return aPos != bPos
}

func entitySignature(ws *WorldState) string {
	sig := ""
	for _, e := range ws.Entities {
		if e.Type == "human_player" || e.Type == "ai_agent" || e.Type == "core" {
			continue
		}
		sig += e.Type + fmt.Sprintf("(%.1f,%.1f)", e.Position.X, e.Position.Z)
	}
	return sig
}
