import json
from pathlib2 import Path


with open(str(Path(__file__).parent / Path('typedef.json')), 'r') as f:
    TYPEDEF = json.load(f)

with open(str(Path(__file__).parent / Path('feerate.json')), 'r') as f:
    FEERATE = json.load(f)

API_URL = 'http://47.75.57.213:3001/api'