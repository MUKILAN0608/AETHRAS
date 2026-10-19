package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/aethras/game-server/world"
)

type Config struct {
	ServiceName  string
	Port         string
	AIServiceURL string
}

func loadConfig() Config {
	return Config{
		ServiceName:  getEnv("GAME_SERVER_NAME", "aethras-game-server"),
		Port:         getEnv("GAME_SERVER_PORT", "8080"),
		AIServiceURL: getEnv("AI_SERVICE_URL", "http://localhost:8000"),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

type HealthResponse struct {
	Service string `json:"service"`
	Status  string `json:"status"`
}

type PromptRequest struct {
	Prompt  string `json:"prompt"`
	Actor   string `json:"actor"`
	WorldID string `json:"world_id"`
}

type ParsedActionResponse struct {
	Intent     string  `json:"intent"`
	Action     string  `json:"action"`
	Target     string  `json:"target"`
	Source     string  `json:"source"`
	Intensity  float64 `json:"intensity"`
	Magnitude  float64 `json:"magnitude"`
	Confidence float64 `json:"confidence"`
	Demo       bool    `json:"demo"`
}

type PromptResponse struct {
	ParsedAction ParsedActionResponse  `json:"parsed_action"`
	Transform    world.TransformResult `json:"transform"`
}

var worldManager = world.NewManager()
var worldRequests sync.Mutex

func main() {
	cfg := loadConfig()
	mux := http.NewServeMux()

	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, HealthResponse{Service: cfg.ServiceName, Status: "ok"})
	})

	mux.HandleFunc("GET /api/scenarios", handleScenarios)
	mux.HandleFunc("POST /api/world/generate", handleWorldGenerate)
	mux.HandleFunc("GET /api/world/state", handleWorldState)
	mux.HandleFunc("GET /api/world/tick", handleWorldTick)
	mux.HandleFunc("POST /api/world/tick", handleWorldTick)
	mux.HandleFunc("GET /api/world/history", handleWorldHistory)
	mux.HandleFunc("GET /api/world/snapshots", handleWorldSnapshots)
	mux.HandleFunc("POST /api/prompt", func(w http.ResponseWriter, r *http.Request) {
		handlePrompt(w, r, cfg)
	})
	mux.HandleFunc("POST /api/prompt/interpret", func(w http.ResponseWriter, r *http.Request) {
		handlePromptInterpret(w, r, cfg)
	})
	mux.HandleFunc("POST /api/prompt/execute", func(w http.ResponseWriter, r *http.Request) {
		handlePromptExecute(w, r, cfg)
	})

	addr := ":" + cfg.Port
	log.Printf("AETHRAS game server starting on %s (AI: %s)", addr, cfg.AIServiceURL)
	if err := http.ListenAndServe(addr, withCORS(mux)); err != nil {
		log.Fatal(err)
	}
}

func handleScenarios(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, world.Scenarios)
}

func handleWorldGenerate(w http.ResponseWriter, r *http.Request) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid body"})
		return
	}
	var req world.GenerateRequest
	if err := json.Unmarshal(body, &req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid json"})
		return
	}
	state := worldManager.Generate(req)
	writeJSON(w, http.StatusOK, state)
}

func handleWorldState(w http.ResponseWriter, r *http.Request) {
	state := worldManager.State()
	if state == nil {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "no world generated"})
		return
	}
	writeJSON(w, http.StatusOK, state)
}

func handleWorldTick(w http.ResponseWriter, r *http.Request) {
	state := worldManager.Tick()
	if state == nil {
		writeJSON(w, http.StatusNotFound, map[string]string{"error": "no world generated"})
		return
	}
	writeJSON(w, http.StatusOK, state)
}

func handleWorldHistory(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, worldManager.History())
}

func handleWorldSnapshots(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, worldManager.Snapshots())
}

func handlePrompt(w http.ResponseWriter, r *http.Request, cfg Config) {
	body, err := io.ReadAll(r.Body)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}

	var req PromptRequest
	if err := json.Unmarshal(body, &req); err != nil || req.Prompt == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "prompt is required"})
		return
	}
	if req.Actor == "" {
		req.Actor = "human"
	}

	aiURL := cfg.AIServiceURL + "/api/parse"
	client := &http.Client{Timeout: 10 * time.Second}
	aiResp, err := client.Post(aiURL, "application/json", bytes.NewReader(body))
	if err != nil {
		log.Printf("AI service unreachable: %v", err)
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
		writeJSON(w, aiResp.StatusCode, map[string]string{"error": "AI service error"})
		return
	}

	var parsed ParsedActionResponse
	if err := json.Unmarshal(respBody, &parsed); err != nil {
		writeJSON(w, http.StatusBadGateway, map[string]string{"error": "invalid AI response"})
		return
	}

	action := world.StructuredAction{
		Intent: parsed.Intent, Action: parsed.Action, Target: parsed.Target,
		Source: parsed.Source, Intensity: parsed.Intensity, Magnitude: parsed.Magnitude,
		Confidence: parsed.Confidence, Demo: parsed.Demo,
	}

	result, err := worldManager.ApplyAction(action, req.Actor, req.Prompt)
	if err != nil {
		writeJSON(w, http.StatusUnprocessableEntity, map[string]string{"error": err.Error()})
		return
	}

	writeJSON(w, http.StatusOK, PromptResponse{
		ParsedAction: parsed,
		Transform:    result,
	})
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(payload)
}

func withCORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		worldRequests.Lock()
		defer worldRequests.Unlock()
		next.ServeHTTP(w, r)
	})
}

// parseSeed helper for query params (unused but available)
func parseSeed(s string) int64 {
	v, _ := strconv.ParseInt(s, 10, 64)
	return v
}
