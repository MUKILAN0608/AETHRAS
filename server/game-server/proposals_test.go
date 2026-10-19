package main

import (
	"bytes"
	"encoding/json"
	"github.com/aethras/game-server/world"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
	"time"
)

func setupProposal(t *testing.T) string {
	t.Helper()
	previousLogPath := researchLogPath
	researchLogPath = filepath.Join(t.TempDir(), "experiments.jsonl")
	t.Cleanup(func() { researchLogPath = previousLogPath })
	worldManager = world.NewManager()
	worldManager.Generate(world.GenerateRequest{Seed: 42, ScenarioID: "scenario_1", Scenario: "A fortress stands between a living forest and a restless ocean."})
	proposals = map[string]pendingProposal{}
	action := map[string]interface{}{"action_id": "test", "action_type": "RAISE_WATER", "actor": "human", "target_entities": []interface{}{"fortress"}, "source_entities": []interface{}{}, "parameters": map[string]interface{}{"intensity": 0.8}, "confidence": 0.9}
	response := &InterpretResponse{Status: "VALID", Validation: map[string]interface{}{"status": "VALID"}, Action: action}
	token, err := registerProposal(response, "ocean rises", "human", stateDigest())
	if err != nil || token == "" {
		t.Fatalf("register: %v", err)
	}
	return token
}

func executeTest(token string) *httptest.ResponseRecorder {
	body, _ := json.Marshal(map[string]interface{}{"proposal_id": token, "prompt": "ocean rises", "actor": "human", "action": map[string]interface{}{"action_type": "DESTROY_ENTITY"}})
	request := httptest.NewRequest("POST", "/api/prompt/execute", bytes.NewReader(body))
	recorder := httptest.NewRecorder()
	handlePromptExecute(recorder, request, Config{})
	return recorder
}

func TestProposalExecutionAndReplay(t *testing.T) {
	token := setupProposal(t)
	response := executeTest(token)
	if response.Code != 200 {
		t.Fatalf("%d %s", response.Code, response.Body)
	}
	if worldManager.State().History[0].Action != "FLOOD" {
		t.Fatal("client modified server action")
	}
	digest := stateDigest()
	if executeTest(token).Code != 409 || digest != stateDigest() {
		t.Fatal("replay modified state")
	}
	data, err := os.ReadFile(researchLogPath)
	if err != nil || !bytes.Contains(data, []byte(`"go_validation_outcome":"accepted"`)) || !bytes.Contains(data, []byte(`"world_event_ids":["event_`)) {
		t.Fatal("execution outcome or event IDs missing from research stream")
	}
}

func TestStaleMissingExpiredProposals(t *testing.T) {
	for _, mode := range []string{"stale", "missing", "expired"} {
		t.Run(mode, func(t *testing.T) {
			token := setupProposal(t)
			if mode == "stale" {
				worldManager.Tick()
			}
			if mode == "missing" {
				token = "unknown"
			}
			if mode == "expired" {
				p := proposals[token]
				p.Expires = time.Now().Add(-time.Minute)
				proposals[token] = p
			}
			digest := stateDigest()
			if executeTest(token).Code != 409 || digest != stateDigest() {
				t.Fatal("invalid proposal changed world")
			}
		})
	}
}

func TestCriticAndReviewCannotIssueTokens(t *testing.T) {
	setupProposal(t)
	for _, status := range []string{"INVALID", "AMBIGUOUS"} {
		token, _ := registerProposal(&InterpretResponse{Status: status, Action: map[string]interface{}{"action_type": "RAISE_WATER"}}, "p", "human", stateDigest())
		if token != "" {
			t.Fatal("invalid pipeline issued token")
		}
	}
	response := &InterpretResponse{Status: "VALID", Validation: map[string]interface{}{"status": "VALID"}, Action: map[string]interface{}{}, Decision: map[string]interface{}{"review_required": true}}
	token, _ := registerProposal(response, "p", "human", stateDigest())
	if token != "" {
		t.Fatal("review bypassed")
	}
}

func TestCurrentValidationBlocksMutation(t *testing.T) {
	for _, mode := range []string{"target", "limits", "action"} {
		t.Run(mode, func(t *testing.T) {
			token := setupProposal(t)
			p := proposals[token]
			if mode == "target" {
				p.Action["target_entities"] = []interface{}{"missing_entity"}
			}
			if mode == "limits" {
				p.Action["parameters"] = map[string]interface{}{"intensity": 2.0}
			}
			if mode == "action" {
				p.Action["action_type"] = "INVENTED"
			}
			proposals[token] = p
			digest := stateDigest()
			if executeTest(token).Code != 422 || digest != stateDigest() {
				t.Fatal("invalid action modified state")
			}
		})
	}
}
