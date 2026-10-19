package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/aethras/game-server/world"
)

type InterpretRequest struct {
	Prompt       string                   `json:"prompt"`
	PlayerID     string                   `json:"player_id"`
	Turn         int                      `json:"turn"`
	WorldID      string                   `json:"world_id"`
	WorldContext map[string]interface{}   `json:"world_context"`
	History      []map[string]interface{} `json:"history"`
	Actor        string                   `json:"actor"`
}

type ExecuteRequest struct {
	ProposalID string                 `json:"proposal_id"`
	Prompt     string                 `json:"prompt"`
	Actor      string                 `json:"actor"`
	Action     map[string]interface{} `json:"action"`
}

type InterpretResponse struct {
	CriticFindings []string               `json:"critic_findings"`
	Decision       map[string]interface{} `json:"decision"`
	ProposalID     string                 `json:"proposal_id,omitempty"`
	Status         string                 `json:"status"`
	Interpretation map[string]interface{} `json:"interpretation"`
	Action         map[string]interface{} `json:"action"`
	Confidence     map[string]interface{} `json:"confidence"`
	Novelty        float64                `json:"novelty"`
	Validation     map[string]interface{} `json:"validation"`
	InferenceMode  string                 `json:"inference_mode"`
	Model          string                 `json:"model"`
	Latency        map[string]interface{} `json:"latency"`
}

func buildWorldContextFromState(ws *world.WorldState) map[string]interface{} {
	if ws == nil {
		return map[string]interface{}{}
	}
	entities := make(map[string]interface{})
	nearby := make([]map[string]interface{}, 0)
	for id, e := range ws.Entities {
		entry := map[string]interface{}{
			"id":     id,
			"type":   e.Type,
			"name":   e.Name,
			"health": e.Health,
		}
		entities[id] = entry
		nearby = append(nearby, entry)
	}
	return map[string]interface{}{
		"entities":        entities,
		"nearby_entities": nearby,
		"turn":            ws.Turn,
		"environmental_state": map[string]interface{}{
			"water_level": ws.EnvironmentalState.WaterLevel,
			"weather":     ws.EnvironmentalState.Weather,
			"fire_spread": ws.EnvironmentalState.FireSpread,
		},
	}
}

func handlePromptInterpret(w http.ResponseWriter, r *http.Request, cfg Config) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}

	var req InterpretRequest
	if err := json.Unmarshal(body, &req); err != nil || req.Prompt == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "prompt is required"})
		return
	}
	if req.PlayerID == "" {
		req.PlayerID = "human"
	}
	if req.WorldID == "" {
		req.WorldID = "world_001"
	}
	if req.History == nil {
		req.History = []map[string]interface{}{}
	}

	state := worldManager.State()
	if state != nil {
		req.WorldContext = buildWorldContextFromState(state)
		req.WorldID = state.WorldID
		req.Turn = state.Turn
	}
	if req.PlayerID != "human" {
		writeJSON(w, 422, map[string]string{"error": "unsupported player"})
		return
	}
	digest := stateDigest()
	if req.Turn == 0 && state != nil {
		req.Turn = state.Turn
	}

	aiBody, _ := json.Marshal(req)
	aiURL := cfg.AIServiceURL + "/api/v1/prompt/interpret"
	client := &http.Client{Timeout: 15 * time.Second}
	aiResp, err := client.Post(aiURL, "application/json", bytes.NewReader(aiBody))
	if err != nil {
		log.Printf("AI interpret unreachable: %v", err)
		writeJSON(w, http.StatusBadGateway, map[string]string{"error": "AI service unavailable"})
		return
	}
	defer aiResp.Body.Close()

	respBody, err := io.ReadAll(aiResp.Body)
	if err != nil {
		writeJSON(w, http.StatusBadGateway, map[string]string{"error": "failed to read AI response"})
		return
	}
	if aiResp.StatusCode != http.StatusOK {
		writeJSON(w, aiResp.StatusCode, map[string]string{"error": string(respBody)})
		return
	}

	var interpretation InterpretResponse
	if json.Unmarshal(respBody, &interpretation) != nil {
		writeJSON(w, 502, map[string]string{"error": "invalid AI response"})
		return
	}
	token, tokenErr := registerProposal(&interpretation, req.Prompt, req.PlayerID, digest)
	if tokenErr != nil {
		writeJSON(w, 503, map[string]string{"error": "proposal unavailable"})
		return
	}
	interpretation.ProposalID = token
	writeJSON(w, http.StatusOK, interpretation)
}

func handlePromptExecute(w http.ResponseWriter, r *http.Request, _ Config) {
	audit := executionAudit{Outcome: "rejected", Reason: "invalid_request"}
	defer func() { logExecutionAudit(audit) }()
	body, err := io.ReadAll(r.Body)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}

	var req ExecuteRequest
	if err := json.Unmarshal(body, &req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}
	if req.Actor == "" {
		req.Actor = "human"
	}
	proposal, exists := proposals[req.ProposalID]
	if exists {
		audit.RequestID = proposal.DecisionID
		audit.Provider = proposal.Provider
		audit.ActionID, _ = proposal.Action["action_id"].(string)
	}
	if state := worldManager.State(); state != nil {
		audit.WorldID = state.WorldID
		audit.Turn = state.Turn
	}
	if !exists || time.Now().After(proposal.Expires) || proposal.State != stateDigest() {
		audit.Reason = "invalid_or_stale_proposal"
		writeJSON(w, http.StatusConflict, map[string]string{"error": "proposal missing, expired, used, or stale; reinterpret"})
		return
	}
	if req.Actor != proposal.Actor || req.Prompt != proposal.Prompt {
		audit.Reason = "context_changed"
		writeJSON(w, 422, map[string]string{"error": "proposal context changed"})
		return
	}
	// Execute the stored action, never client-supplied modifications.
	req.Action = proposal.Action

	actionMap := req.Action
	if actionMap == nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "action is required"})
		return
	}

	actionType, _ := actionMap["action_type"].(string)
	params, _ := actionMap["parameters"].(map[string]interface{})
	intensity := 0.8
	if params != nil {
		if v, ok := params["intensity"].(float64); ok {
			intensity = v
		}
	}

	target := "UNKNOWN"
	if targets, ok := actionMap["target_entities"].([]interface{}); ok && len(targets) > 0 {
		target = toString(targets[0])
	}

	structured := world.MapPhase3Action(actionType, world.ResolveTargetType(target), intensity)
	if conf, ok := actionMap["confidence"].(float64); ok {
		structured.Confidence = conf
	}
	if err := validateCurrentTargets(actionMap, &structured); err != nil {
		audit.Reason = "target_or_permission_rejected"
		writeJSON(w, 422, map[string]string{"error": err.Error()})
		return
	}

	valid, reason := world.NewRules().ValidateAction(structured)
	if !valid {
		audit.Reason = "action_rules_rejected"
		writeJSON(w, http.StatusUnprocessableEntity, map[string]string{"error": reason})
		return
	}

	delete(proposals, req.ProposalID)
	result, err := worldManager.ApplyAction(structured, req.Actor, req.Prompt)
	if err != nil {
		audit.Reason = "world_revalidation_rejected"
		writeJSON(w, http.StatusUnprocessableEntity, map[string]string{"error": err.Error()})
		return
	}

	audit.Outcome = "accepted"
	audit.Reason = ""
	if result.WorldState != nil {
		audit.Turn = result.WorldState.Turn
	}
	for _, event := range result.Events {
		audit.EventIDs = append(audit.EventIDs, event.ID)
	}
	writeJSON(w, http.StatusOK, map[string]interface{}{
		"action_proposal": actionMap,
		"parsed_action":   structured,
		"transform":       result,
	})
}

func toString(v interface{}) string {
	switch t := v.(type) {
	case string:
		return t
	default:
		b, _ := json.Marshal(t)
		return string(b)
	}
}
