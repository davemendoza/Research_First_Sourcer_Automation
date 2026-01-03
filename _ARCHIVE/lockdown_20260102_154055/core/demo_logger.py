from datetime import datetime
import json

def emit(event_type, payload=None):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "payload": payload or {}
    }
    print(json.dumps(record))
