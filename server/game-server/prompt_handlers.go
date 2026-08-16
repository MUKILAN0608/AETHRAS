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
	Prompt        string                 `json:"prompt"`
	PlayerID      string                 `json:"player_id"`
	Turn          int                    `json:"turn"`
	WorldID       string                 `json:"world_id"`
	WorldContext  map[string]interface{} `json:"world_context"`
	History       []map[string]interface{} `json:"history"`
	Actor         string                 `json:"actor"`
}

type ExecuteRequest struct {
	Prompt string                 `json:"prompt"`
	Actor  string                 `json:"actor"`
	Action map[string]interface{} `json:"action"`
}

type InterpretResponse struct {
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
	if len(req.WorldContext) == 0 && state != nil {
		req.WorldContext = buildWorldContextFromState(state)
	}
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

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(respBody)
}

func handlePromptExecute(w http.ResponseWriter, r *http.Request, _ Config) {
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

	valid, reason := world.NewRules().ValidateAction(structured)
	if !valid {
		writeJSON(w, http.StatusUnprocessableEntity, map[string]string{"error": reason})
		return
	}

	result, err := worldManager.ApplyAction(structured, req.Actor, req.Prompt)
	if err != nil {
		writeJSON(w, http.StatusUnprocessableEntity, map[string]string{"error": err.Error()})
		return
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
