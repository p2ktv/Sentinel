Heartbeat = {
    "op": 1,
    "d": None
}

Identify = {
    "op": 2,
    "d": {
        "token": "",
        "intents": 0,
        "properties": {
            "$os": "linux",
            "$browser": "sentinel-discord-lib",
            "$device": "sentinel-discord-lib"
        },
    }
}

Presence = {
    "op": 3,
    "d": {
        "activities": [],
        "afk": False,
        "since": 0.0,
        "status": ""
    }
}