import json

with open("src/configs/onedrive_sync_config.json", "r") as f:
    path_mappings = json.load(f)
    print(f"Loaded {len(path_mappings)} path mappings")
    print(path_mappings.items())