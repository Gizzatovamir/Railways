import json


def get_json(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return data
