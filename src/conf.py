import json

Conf = {}

with open('config/default.json', 'r') as f:
    Conf = json.load(f)
