import os
import json
from kivy.logger import Logger

def get_app_config_path(app):
    try:
        base = app.user_data_dir
    except Exception:
        base = os.getcwd()
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, 'dj_player_config.json')

def load_config(path):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            Logger.warning(f"Config load failed: {e}")
    return {}

def save_config(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e:
        Logger.warning(f"Config save failed: {e}")
