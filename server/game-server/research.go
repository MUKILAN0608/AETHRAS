package main

import (
	"encoding/json"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"time"
)

// All three services in this repository use this one research stream.
var researchLogPath = func() string {
	_, source, _, _ := runtime.Caller(0)
	return filepath.Join(filepath.Dir(source), "..", "..", "ai", "app", "logs", "experiments.jsonl")
}()

type executionAudit struct {
	Event     string   `json:"event"`
	Timestamp string   `json:"timestamp"`
	RequestID string   `json:"request_id,omitempty"`
	ActionID  string   `json:"action_id,omitempty"`
	Provider  string   `json:"provider,omitempty"`
	WorldID   string   `json:"match_id,omitempty"`
	Turn      int      `json:"turn"`
	Outcome   string   `json:"go_validation_outcome"`
	Reason    string   `json:"reason,omitempty"`
	EventIDs  []string `json:"world_event_ids"`
}

func logExecutionAudit(record executionAudit) {
	record.Event = "execution"
	record.Timestamp = time.Now().UTC().Format(time.RFC3339Nano)
	if record.EventIDs == nil {
		record.EventIDs = []string{}
	}
	data, err := json.Marshal(record)
	if err == nil {
		err = os.MkdirAll(filepath.Dir(researchLogPath), 0700)
	}
	if err == nil {
		var file *os.File
		file, err = os.OpenFile(researchLogPath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
		if err == nil {
			_, err = file.Write(append(data, '\n'))
			file.Close()
		}
	}
	if err != nil {
		log.Print("Research outcome could not be recorded")
	}
}
