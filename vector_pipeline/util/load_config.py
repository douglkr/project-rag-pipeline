import os
import yaml

def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file '{path}' not found.")
    with open(path, 'r') as f:
        return yaml.safe_load(f)