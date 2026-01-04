import json
import os

EXTRA_BACKUP_FILE = "extra_backups.json"


def _default_data():
    return {
        "extras": []
    }


def load_extra_backups():
    if not os.path.exists(EXTRA_BACKUP_FILE):
        return _default_data()

    try:
        with open(EXTRA_BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return _default_data()

    # Garantir estrutura mínima
    if "extras" not in data or not isinstance(data["extras"], list):
        return _default_data()

    validated = []
    for extra in data["extras"]:
        if not isinstance(extra, dict):
            continue
        if not all(k in extra for k in ("name", "root_path", "base_folder")):
            continue

        extra.setdefault("structure", [])
        extra.setdefault("enabled", True)

        validated.append(extra)

    return {"extras": validated}


def save_extra_backups(data: dict):
    with open(EXTRA_BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
