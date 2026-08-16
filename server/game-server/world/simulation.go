package world

// Simulator runs lightweight continuous environmental simulation.
type Simulator struct{}

func NewSimulator() *Simulator {
	return &Simulator{}
}

// Tick advances environmental state by one turn deterministically.
func (s *Simulator) Tick(ws *WorldState) {
	ws.Turn++
	turn := ws.Turn

	// Weather progression cycle
	switch {
	case turn%11 == 0 && ws.EnvironmentalState.WaterLevel > 0.3:
		ws.EnvironmentalState.Weather = "flood"
	case turn%9 == 0:
		ws.EnvironmentalState.Weather = "rain"
		ws.EnvironmentalState.WaterLevel += 0.05
	case turn%7 == 0:
		ws.EnvironmentalState.Weather = "clouds"
	case turn%4 == 0:
		ws.EnvironmentalState.Weather = "clouds"
	default:
		if ws.EnvironmentalState.Weather == "" {
			ws.EnvironmentalState.Weather = "clear"
		}
	}

	// Time of day cycle
	ws.EnvironmentalState.TimeOfDay = float64(turn%24) / 24.0

	// Fire spread decay/growth
	if ws.EnvironmentalState.FireSpread > 0 {
		ws.EnvironmentalState.FireSpread *= 0.95
		if ws.EnvironmentalState.FireSpread < 0.01 {
			ws.EnvironmentalState.FireSpread = 0
			ws.EnvironmentalState.AtmosphericFX = "none"
		}
	}

	// Water movement
	if ws.EnvironmentalState.WaterLevel > 0 {
		ws.EnvironmentalState.WaterLevel *= 0.99
	}

	// Vegetation growth on ruins
	for id, e := range ws.Entities {
		if e.Type == "ruins" && turn%5 == 0 {
			veg := e.Properties["vegetation"]
			e.Properties["vegetation"] = veg + 0.05
			if e.Properties["vegetation"] > 0.5 {
				e.Type = "forest"
				e.SemanticTags = append(e.SemanticTags, "regrown")
			}
			ws.Entities[id] = e
		}
	}

	// Temperature variation
	ws.EnvironmentalState.Temperature = 18 + float64(turn%10)*0.5
}
