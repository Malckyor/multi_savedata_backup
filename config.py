import json
import os

CONFIG_FILE = "config.json"

# ===================== Funções para detectar diretórios padrão =====================
def detect_default_steam():
    candidates = [
        os.path.join(os.getenv("ProgramFiles", ""), "Steam"),
        os.path.join(os.getenv("ProgramFiles(x86)", ""), "Steam"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path

    return ""

def validate_steam_path(path):
    # Verifica se o diretório contém a estrutura Steam/userdata
    return os.path.isdir(os.path.join(path, "userdata"))

def detect_default_ppsspp():
    path = os.path.join(os.getenv('APPDATA'), "PPSSPP")
    return path if os.path.isdir(path) else ""

def validate_ppsspp_path(path):
    # Verifica se o diretório contém a estrutura PSP/SAVEDATA
    return (
        os.path.isdir(os.path.join(path, "memstick", "PSP", "SAVEDATA")) or
        os.path.isdir(os.path.join(path, "PSP", "SAVEDATA"))
    )

def detect_default_vita3k():
    path = os.path.join(os.getenv('APPDATA'), "Vita3K")
    return path if os.path.isdir(path) else ""

def validate_vita3k_path(path):
    # Verifica se o diretório contém a estrutura Vita3K/Vita3K/ux0/user
    return os.path.isdir(os.path.join(path, "Vita3K", "ux0", "user"))

def detect_default_duckstation():
    candidates = [
        os.path.join(os.getenv('LOCALAPPDATA', ''), "DuckStation"),
        os.path.join(os.getenv('APPDATA', ''), "DuckStation"),
    ]

    for path in candidates:
        if os.path.isdir(path):
            return path

    return ""

def validate_duckstation_path(path):
    # Verifica se o diretório contém a estrutura DuckStation/memcards
    return os.path.isdir(os.path.join(path, "memcards"))

def detect_default_pcsx2():
    path = os.path.join(os.getenv('USERPROFILE'), "Documents", "PCSX2")
    return path if os.path.isdir(path) else ""

def validate_pcsx2_path(path):
    # Verifica se o diretório contém a estrutura PCSX2/memcards
    return os.path.isdir(os.path.join(path, "memcards"))

def detect_default_rpcs3():
    return ""

def validate_rpcs3_path(path):
    # Verifica se o diretório contém a estrutura RPCS3/dev_hdd0/savedata
    return os.path.isdir(os.path.join(path, "dev_hdd0", "savedata"))

def detect_default_melonds():
    return ""

def validate_melonds_path(path):
    # Verificação flexível e genérica
    return os.path.isdir(path)

def detect_default_citra():
    path = os.path.join(os.getenv('APPDATA'), "Citra")
    return path if os.path.isdir(path) else ""

def validate_citra_path(path):
    # Verifica se o diretório contém a estrutura Citra/sdmc
    return os.path.isdir(os.path.join(path, "sdmc"))

def detect_default_project64():
    base_dirs = [
        os.getenv("ProgramFiles", ""),
        os.getenv("ProgramFiles(x86)", "")
    ]

    for base in base_dirs:
        if not os.path.isdir(base):
            continue

        for folder in os.listdir(base):
            full_path = os.path.join(base, folder)

            if (
                folder.lower().startswith("project64")
                and os.path.isdir(full_path)
                and os.path.isdir(os.path.join(full_path, "Save"))
            ):
                return full_path

    return ""

def validate_project64_path(path):
    # Verifica se o diretório contém a estrutura Project64/Save
    return os.path.isdir(os.path.join(path, "Save"))

def detect_default_dolphin():
    path = os.path.join(os.getenv('USERPROFILE'), "Documents", "Dolphin Emulator")
    return path if os.path.isdir(path) else ""

def validate_dolphin_path(path):
    # Verifica se o diretório contém a estrutura Dolphin/GBA, Dolphin/GC e Dolphin/Wii
    return (
        os.path.isdir(os.path.join(path, "GBA")) or
        os.path.isdir(os.path.join(path, "GC")) or
        os.path.isdir(os.path.join(path, "Wii"))
    )

def detect_default_cemu():
    path = os.path.join(os.getenv('APPDATA'), "Cemu")
    return path if os.path.isdir(path) else ""

def validate_cemu_path(path):
    # Verifica se o diretório contém a estrutura mlc01/usr/save
    return os.path.isdir(os.path.join(path, "mlc01", "usr", "save"))

def detect_default_eden():
    path = os.path.join(os.getenv('APPDATA'), "eden")
    return path if os.path.isdir(path) else ""

def validate_eden_path(path):
    # Verifica se o diretório contém a estrutura eden/nand
    return os.path.isdir(os.path.join(path, "nand", "user", "save"))

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
    # dir_entry = {"name": ..., "path": ..., "structure": [...]}
    # Retorna True se todas as subpastas listadas existem.
    path = dir_entry["path"]
    for sub in dir_entry.get("structure", []):
        if not os.path.isdir(os.path.join(path, sub)):
            return False
    return True

def detect_google_drive():
    path = os.path.join(os.getenv('USERPROFILE'), "Google Drive")
    return path if os.path.isdir(path) else ""

# ===================== Configuração padrão =====================
DEFAULT_CONFIG = {
    "steam_path": detect_default_steam(),
    "ppsspp_path": detect_default_ppsspp(),
    "vita3k_path": detect_default_vita3k(),
    "duckstation": detect_default_duckstation(),
    "pcsx2_path": detect_default_pcsx2(),
    "rpcs3_path": detect_default_rpcs3(),
    "melonds_path": detect_default_melonds(),
    "citra_path": detect_default_citra(),
    "project64_path": detect_default_project64(),
    "dolphin_path": detect_default_dolphin(),
    "cemu_path": detect_default_cemu(),
    "eden_path": detect_default_eden(),
    "backup_root": detect_google_drive(),
    "steam_enabled": False,
    "ppsspp_enabled": False,
    "vita3k_enabled": False,
    "duckstation_enabled": False,
    "pcsx2_enabled": False,
    "rpcs3_enabled": False,
    "melonds_enabled": False,
    "citra_enabled": False,
    "project64_enabled": False,
    "dolphin_enabled": False,
    "cemu_enabled": False,
    "eden_enabled": False,
    "theme": "system",
    "window_width": 900,
    "window_height": 700,
    "window_x": None,
    "window_y": None
}

# ===================== Carregar configuração =====================
def load_config():
    # PRIMEIRA EXECUÇÃO (sem config.json)
    if not os.path.exists(CONFIG_FILE):
        cfg = DEFAULT_CONFIG.copy()

        # UX: mostrar um exemplo funcional
        cfg["steam_enabled"] = True

        return cfg

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Completa apenas chaves ausentes
    for key, default_value in DEFAULT_CONFIG.items():
        if key not in cfg:
            cfg[key] = default_value

    return cfg

# ===================== Salvar configuração =====================
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
