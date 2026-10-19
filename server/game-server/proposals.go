package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"

	"github.com/aethras/game-server/world"
)

// Access is serialized by withCORS together with all world mutations.
type pendingProposal struct {
	Action     map[string]interface{}
	Prompt     string
	Actor      string
	State      [32]byte
	Expires    time.Time
	DecisionID string
	Provider   string
}

var proposals = map[string]pendingProposal{}

func stateDigest() [32]byte {
	data, _ := json.Marshal(worldManager.State())
	return sha256.Sum256(data)
}

func registerProposal(response *InterpretResponse, prompt, actor string, digest [32]byte) (string, error) {
	if response.Status != "VALID" || response.Validation["status"] != "VALID" || response.Action == nil {
		return "", nil
	}
	if response.Decision != nil {
		review, ok := response.Decision["review_required"].(bool)
		if !ok || review {
			return "", nil
		}
	}
	for token, proposal := range proposals {
		if time.Now().After(proposal.Expires) {
			delete(proposals, token)
		}
	}
	if len(proposals) >= 1024 {
		return "", fmt.Errorf("proposal capacity reached")
	}
	bytes := make([]byte, 32)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}
	token := hex.EncodeToString(bytes)
	decisionID, _ := response.Decision["request_id"].(string)
	provider, _ := response.Decision["provider"].(string)
	proposals[token] = pendingProposal{Action: response.Action, Prompt: prompt, Actor: actor,
		State: digest, Expires: time.Now().Add(5 * time.Minute), DecisionID: decisionID, Provider: provider}
	return token, nil
}

func validateCurrentTargets(action map[string]interface{}, structured *world.StructuredAction) error {
	state := worldManager.State()
	if state == nil {
		return fmt.Errorf("no world generated")
	}
	if action["actor"] != "human" {
		return fmt.Errorf("unsupported actor")
	}
	for _, field := range []string{"source_entities", "target_entities"} {
		values, ok := action[field].([]interface{})
		if !ok {
			return fmt.Errorf("invalid entity list")
		}
		if field == "target_entities" && len(values) == 0 {
			return fmt.Errorf("target required")
		}
		if field == "target_entities" && len(values) > 1 {
			return fmt.Errorf("multiple targets are not supported by the current transformer")
		}
		for _, value := range values {
			target, ok := value.(string)
			if !ok || target == "" {
				return fmt.Errorf("invalid target")
			}
			if target == "world" && structured.Action == "STORM" {
				continue
			}
			if entity, exists := state.Entities[target]; exists {
				if field == "target_entities" {
					structured.Target = entity.ID
				}
				continue
			}
			found := false
			for _, entity := range state.Entities {
				if world.ResolveTargetType(entity.Type) == world.ResolveTargetType(target) {
					found = true
					break
				}
			}
			if !found {
				return fmt.Errorf("entity no longer exists")
			}
		}
	}
	return nil
}
