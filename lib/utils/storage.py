import json
import os
from models.user import User

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "project_tracker.json")

def ensure_data_directory():
    """Ensures the local data storage directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_data(users_dict: dict):
    """Persists all system users, projects, and tasks to a JSON file."""
    ensure_data_directory()
    data = {name: user.to_dict() for name, user in users_dict.items()}
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"❌ Error saving data: {e}")

def load_data() -> dict:
    """Loads all system data from the local JSON storage file."""
    ensure_data_directory()
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            data = json.loads(content)
            users_dict = {}
            for name, user_data in data.items():
                users_dict[name] = User.from_dict(user_data)
            return users_dict
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Error loading data file (might be corrupt): {e}")
        return {}