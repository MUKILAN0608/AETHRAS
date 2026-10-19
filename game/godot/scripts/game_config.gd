extends Node

## Game configuration — server URLs from environment or defaults.

var GAME_SERVER_URL: String = OS.get_environment("GODOT_GAME_SERVER_URL") if OS.has_environment("GODOT_GAME_SERVER_URL") else "http://localhost:8080"
const DEFAULT_PROMPT := "The ocean rises and consumes the fortress."
