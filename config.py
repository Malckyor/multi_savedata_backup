import json
import os

CONFIG_FILE = "config.json"

# ===== Funções para detectar diretórios padrão =====
def detect_default_ppsspp():
    path = os.path.join(os.getenv('APPDATA'), "PPSSPP")
    return path if os.path.isdir(path) else ""

def validate_ppsspp_path(path):
    """Verifica se o diretório contém a estrutura PSP/SAVEDATA"""
    return (
        os.path.isdir(os.path.join(path, "memstick", "PSP", "SAVEDATA")) or
        os.path.isdir(os.path.join(path, "PSP", "SAVEDATA"))
    )

def detect_default_pcsx2():
    path = os.path.join(os.getenv('USERPROFILE'), "Documents", "PCSX2")
    return path if os.path.isdir(path) else ""

def validate_pcsx2_path(path):
    """Verifica se o diretório contém a estrutura PCSX2/memcards"""
    return os.path.isdir(os.path.join(path, "memcards"))

def detect_default_citra():
    path = os.path.join(os.getenv('APPDATA'), "Citra")
    return path if os.path.isdir(path) else ""

def validate_citra_path(path):
    """Verifica se o diretório contém a estrutura Citra/sdmc"""
    return os.path.isdir(os.path.join(path, "sdmc"))

def add_custom_dir(name, path, structure):
    custom_dirs = config.get("custom_dirs", [])
    
    # Verifica se já existe
    for d in custom_dirs:
        if d["name"] == name:
            d["path"] = path
            d["structure"] = structure
            break
    else:
        custom_dirs.append({"name": name, "path": path, "structure": structure})

    config["custom_dirs"] = custom_dirs
    save_config(config)

def validate_custom_dir(dir_entry):
    """
    dir_entry = {"name": ..., "path": ..., "structure": [...]}
    Retorna True se todas as subpastas listadas existem.
    """
    path = dir_entry["path"]
    for sub in dir_entry.get("structure", []):
        if not os.path.isdir(os.path.join(path, sub)):
            return False
    return True

def detect_google_drive():
    path = os.path.join(os.getenv('USERPROFILE'), "Google Drive")
    return path if os.path.isdir(path) else ""

# ===== Configuração padrão =====
DEFAULT_CONFIG = {
    "ppsspp_path": detect_default_ppsspp(),
    "pcsx2_path": detect_default_pcsx2(),
    "citra_path": detect_default_citra(),
    "backup_root": detect_google_drive(),
    "ppsspp_enabled": False,
    "pcsx2_enabled": False,
    "citra_enabled": False,
    "theme": "system",
    "window_width": 900,
    "window_height": 700,
    "window_x": None,
    "window_y": None
}

# ===== Carregar configuração =====
def load_config():
    # PRIMEIRA EXECUÇÃO (sem config.json)
    if not os.path.exists(CONFIG_FILE):
        cfg = DEFAULT_CONFIG.copy()

        # UX: mostrar um exemplo funcional
        cfg["ppsspp_enabled"] = True

        return cfg

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Completa apenas chaves ausentes
    for key, default_value in DEFAULT_CONFIG.items():
        if key not in cfg:
            cfg[key] = default_value

    return cfg

# ===== Salvar configuração =====
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
