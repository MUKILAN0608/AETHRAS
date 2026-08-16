package world

// EventProcessor handles sequential causal event propagation.
type EventProcessor struct{}

func NewEventProcessor() *EventProcessor {
	return &EventProcessor{}
}

// ProcessQueue processes events sequentially and returns cascading events.
func (p *EventProcessor) ProcessQueue(ws *WorldState, events []WorldEvent) []WorldEvent {
	var cascaded []WorldEvent
	for _, event := range events {
		if event.Processed {
			continue
		}
		switch event.Type {
		case "FIRE":
			cascaded = append(cascaded, p.processFireCascade(ws, event)...)
		case "FLOOD":
			cascaded = append(cascaded, p.processFloodCascade(ws, event)...)
		}
		event.Processed = true
	}
	return cascaded
}

func (p *EventProcessor) processFireCascade(ws *WorldState, event WorldEvent) []WorldEvent {
	var result []WorldEvent
	if ws.EnvironmentalState.Visibility < 0.5 {
		ws.EnvironmentalState.AtmosphericFX = "smoke"
	}
	if ws.EnvironmentalState.FireSpread > 0.4 && ws.EnvironmentalState.WindSpeed > 0.3 {
		result = append(result, WorldEvent{
			ID: fmtID("cascade", ws.Turn), Type: "FIRE_SPREAD",
			Intensity: ws.EnvironmentalState.FireSpread, Turn: ws.Turn,
		})
	}
	return result
}

func (p *EventProcessor) processFloodCascade(ws *WorldState, event WorldEvent) []WorldEvent {
	var result []WorldEvent
	if ws.EnvironmentalState.WaterLevel > 0.5 {
		ws.EnvironmentalState.Weather = "rain"
		result = append(result, WorldEvent{
			ID: fmtID("cascade", ws.Turn), Type: "FLOOD_EXPAND",
			Intensity: ws.EnvironmentalState.WaterLevel, Turn: ws.Turn,
		})
	}
	return result
}
