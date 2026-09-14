import json
from datetime import datetime

def parse_json(value, default=None):
    try:
        return json.loads(value)
    except Exception:
        return default if default is not None else []

def today_label():
    return datetime.now().strftime("%d %b")
