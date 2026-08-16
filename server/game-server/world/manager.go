package world

import "encoding/json"

// Snapshot captures world state at a specific turn for replay/research.
type Snapshot struct {
	Turn       int         `json:"turn"`
	WorldState *WorldState `json:"world_state"`
	Timestamp  string      `json:"timestamp"`
}

// SnapshotStore manages world snapshots.
type SnapshotStore struct {
	snapshots []Snapshot
}

func NewSnapshotStore() *SnapshotStore {
	return &SnapshotStore{snapshots: []Snapshot{}}
}

func (s *SnapshotStore) Save(ws *WorldState) Snapshot {
	clone := cloneWorldState(ws)
	snap := Snapshot{Turn: ws.Turn, WorldState: clone}
	s.snapshots = append(s.snapshots, snap)
	return snap
}

func (s *SnapshotStore) All() []Snapshot {
	return s.snapshots
}

func (s *SnapshotStore) AtTurn(turn int) *Snapshot {
	for i := range s.snapshots {
		if s.snapshots[i].Turn == turn {
			return &s.snapshots[i]
		}
	}
	return nil
}

func cloneWorldState(ws *WorldState) *WorldState {
	data, _ := json.Marshal(ws)
	var clone WorldState
	_ = json.Unmarshal(data, &clone)
	return &clone
}

// Manager is the authoritative world session manager.
type Manager struct {
	state      *WorldState
	generator  *Generator
	transformer *Transformer
	validator  *Rules
	simulator  *Simulator
	snapshots  *SnapshotStore
}

func NewManager() *Manager {
	return &Manager{
		generator:   NewGenerator(),
		transformer: NewTransformer(),
		validator:   NewRules(),
		simulator:   NewSimulator(),
		snapshots:   NewSnapshotStore(),
	}
}

func (m *Manager) Generate(req GenerateRequest) *WorldState {
	m.state = m.generator.Generate(req)
	m.snapshots.Save(m.state)
	return m.state
}

func (m *Manager) State() *WorldState {
	return m.state
}

func (m *Manager) ApplyAction(action StructuredAction, actor, prompt string) (TransformResult, error) {
	if m.state == nil {
		return TransformResult{}, errNoWorld
	}
	ok, reason := m.validator.ValidateAction(action)
	if !ok {
		return TransformResult{}, &ValidationError{Reason: reason}
	}
	m.snapshots.Save(m.state)
	result := m.transformer.Apply(m.state, action, actor, prompt)
	m.snapshots.Save(m.state)
	return result, nil
}

func (m *Manager) Tick() *WorldState {
	if m.state == nil {
		return nil
	}
	m.simulator.Tick(m.state)
	m.snapshots.Save(m.state)
	return m.state
}

func (m *Manager) Snapshots() []Snapshot {
	return m.snapshots.All()
}

func (m *Manager) History() []HistoryEntry {
	if m.state == nil {
		return nil
	}
	return m.state.History
}

type ValidationError struct {
	Reason string
}

func (e *ValidationError) Error() string {
	return e.Reason
}

var errNoWorld = &ValidationError{Reason: "no world generated"}
