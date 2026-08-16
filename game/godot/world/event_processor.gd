extends Node
class_name EventProcessor

## Visual event queue processor — causal chain display helper.

var _queue: Array = []

func enqueue(event: WorldEvent) -> void:
	_queue.append(event)


func process_all() -> Array:
	var processed: Array = []
	while _queue.size() > 0:
		var event: WorldEvent = _queue.pop_front()
		processed.append(event.type)
	return processed
