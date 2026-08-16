package world

import "testing"

func TestMapPhase3Action(t *testing.T) {
	cases := []struct {
		inType   string
		wantAct  string
	}{
		{"RAISE_WATER", "FLOOD"},
		{"START_FIRE", "FIRE"},
		{"MEMORY_ADD", "MEMORY_REMEMBER"},
		{"SPATIAL_BYPASS", "STORM"},
		{"INDIRECT_STRUCTURAL_ATTACK", "TRANSFORM"},
	}
	for _, c := range cases {
		got := MapPhase3Action(c.inType, "fortress", 0.8)
		if got.Action != c.wantAct {
			t.Errorf("MapPhase3Action(%s) = %s, want %s", c.inType, got.Action, c.wantAct)
		}
	}
}
