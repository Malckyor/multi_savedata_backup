import os
import subprocess
import shutil
from datetime import datetime
from utils import find_compressor
import json

# ===================== CONFIGURAÇÃO DE LOCALE =====================
def get_translations():
    """Carrega o idioma atual do config.json e retorna o dicionário de traduções."""
    language = "EN"  # padrão
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            language = config.get("language", language)
    except Exception:
        pass

    translations = {}
    locale_path = os.path.join("locales", f"{language}.json")
    try:
        with open(locale_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except Exception as e:
        print(f"Não foi possível carregar traduções de {locale_path}: {e}")
    return translations

def tr(key, **kwargs):
    """Retorna a tradução atual da chave, recarregando o idioma se necessário."""
    translations = get_translations()
    text = translations.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

# ===================== FUNÇÕES DE BACKUP =====================

def backup_ppsspp(ppsspp_path, sync_dir=None, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    savedata = os.path.join(ppsspp_path, "memstick", "PSP", "SAVEDATA")
    if not os.path.isdir(savedata):
        savedata = os.path.join(ppsspp_path, "PSP", "SAVEDATA")
    if not os.path.isdir(savedata):
        return False, tr("folder_not_found", folder="SAVEDATA")
    if not os.listdir(savedata):
        return False, tr("folder_empty", folder="SAVEDATA")

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    project_root = os.getcwd()
    local_backup_dir = os.path.join(project_root, "Multi Savedata Backup")
    os.makedirs(local_backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"PPSSPP_SAVES_{timestamp}.zip"
    local_zip_path = os.path.join(local_backup_dir, zip_name)

    try:
        progress(30, tr("compacting") + " SAVEDATA")
        items = [os.path.join(savedata, f) for f in os.listdir(savedata)]
        if tool == "winrar":
            cmd = [exe, "a", "-afzip", "-r", local_zip_path] + items
        else:
            cmd = [exe, "a", "-tzip", local_zip_path] + items
        subprocess.run(cmd, check=True)

        if sync_dir:
            progress(70, tr("syncing_backup"))
            sync_dir = os.path.abspath(sync_dir)
            os.makedirs(sync_dir, exist_ok=True)
            sync_zip_path = os.path.join(sync_dir, zip_name)
            shutil.copy2(local_zip_path, sync_zip_path)
            os.remove(local_zip_path)
            progress(100, tr("backup_finished"))
            return True, tr("backup_synced_success", path=sync_zip_path)

        progress(100, tr("backup_finished"))
        return True, tr("backup_success", path=local_zip_path)

    except subprocess.CalledProcessError as e:
        progress(0, tr("error_compressing"))
        return False, tr("error_compressing_detail", detail=e)
    except Exception as e:
        progress(0, tr("unexpected_error"))
        return False, tr("unexpected_error_detail", detail=e)

# =======================================================

def backup_pcsx2(pcsx2_path, sync_dir=None, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    memcards = os.path.join(pcsx2_path, "memcards")
    if not os.path.isdir(memcards):
        return False, tr("folder_not_found", folder="memcards")
    if not os.listdir(memcards):
        return False, tr("folder_empty", folder="memcards")

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    project_root = os.getcwd()
    local_backup_dir = os.path.join(project_root, "Multi Savedata Backup")
    os.makedirs(local_backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"PCSX2_MEMCARDS_{timestamp}.zip"
    local_zip_path = os.path.join(local_backup_dir, zip_name)

    try:
        progress(30, tr("compacting") + " memcards")
        items = [os.path.join(memcards, f) for f in os.listdir(memcards)]
        if tool == "winrar":
            cmd = [exe, "a", "-afzip", "-r", local_zip_path] + items
        else:
            cmd = [exe, "a", "-tzip", local_zip_path] + items
        subprocess.run(cmd, check=True)

        if sync_dir:
            progress(70, tr("syncing_backup"))
            sync_dir = os.path.abspath(sync_dir)
            os.makedirs(sync_dir, exist_ok=True)
            sync_zip_path = os.path.join(sync_dir, zip_name)
            shutil.copy2(local_zip_path, sync_zip_path)
            os.remove(local_zip_path)
            progress(100, tr("backup_finished"))
            return True, tr("backup_synced_success", path=sync_zip_path)

        progress(100, tr("backup_finished"))
        return True, tr("backup_success", path=local_zip_path)

    except subprocess.CalledProcessError as e:
        progress(0, tr("error_compressing"))
        return False, tr("error_compressing_detail", detail=e)
    except Exception as e:
        progress(0, tr("unexpected_error"))
        return False, tr("unexpected_error_detail", detail=e)

# =======================================================

def backup_citra(citra_path, sync_dir=None, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    sdmc = os.path.join(citra_path, "sdmc")
    if not os.path.isdir(sdmc):
        return False, tr("folder_not_found", folder="sdmc")
    if not os.listdir(sdmc):
        return False, tr("folder_empty", folder="sdmc")

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    project_root = os.getcwd()
    local_backup_dir = os.path.join(project_root, "Multi Savedata Backup")
    os.makedirs(local_backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_name = f"CITRA_SDMC_{timestamp}.zip"
    local_zip_path = os.path.join(local_backup_dir, zip_name)

    try:
        progress(30, tr("compacting") + " sdmc")
        items = [os.path.join(sdmc, f) for f in os.listdir(sdmc)]
        if tool == "winrar":
            cmd = [exe, "a", "-afzip", "-r", local_zip_path] + items
        else:
            cmd = [exe, "a", "-tzip", local_zip_path] + items
        subprocess.run(cmd, check=True)

        if sync_dir:
            progress(70, tr("syncing_backup"))
            sync_dir = os.path.abspath(sync_dir)
            os.makedirs(sync_dir, exist_ok=True)
            sync_zip_path = os.path.join(sync_dir, zip_name)
            shutil.copy2(local_zip_path, sync_zip_path)
            os.remove(local_zip_path)
            progress(100, tr("backup_finished"))
            return True, tr("backup_synced_success", path=sync_zip_path)

        progress(100, tr("backup_finished"))
        return True, tr("backup_success", path=local_zip_path)

    except subprocess.CalledProcessError as e:
        progress(0, tr("error_compressing"))
        return False, tr("error_compressing_detail", detail=e)
    except Exception as e:
        progress(0, tr("unexpected_error"))
        return False, tr("unexpected_error_detail", detail=e)

# =======================================================

def backup_custom_dir(dir_entry, sync_dir=None, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    name = dir_entry.get("name")
    root_path = dir_entry.get("root_path")

    if not name or not root_path:
        return False, tr("custom_backup_invalid")

    if not os.path.isdir(root_path):
        return False, tr("folder_not_found", folder=name)
    if not os.listdir(root_path):
        return False, tr("folder_empty", folder=name)

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    project_root = os.getcwd()
    local_backup_dir = os.path.join(project_root, "Multi Savedata Backup")
    os.makedirs(local_backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_name = name.replace(" ", "_")
    zip_name = f"{safe_name}_{timestamp}.zip"
    local_zip_path = os.path.join(local_backup_dir, zip_name)

    try:
        progress(30, tr("compacting") + f" '{name}'")
        items = [os.path.join(root_path, f) for f in os.listdir(root_path)]
        if tool == "winrar":
            cmd = [exe, "a", "-afzip", "-r", local_zip_path] + items
        else:
            cmd = [exe, "a", "-tzip", local_zip_path] + items
        subprocess.run(cmd, check=True)

        if sync_dir:
            progress(70, tr("syncing_backup"))
            sync_dir = os.path.abspath(sync_dir)
            os.makedirs(sync_dir, exist_ok=True)
            sync_zip_path = os.path.join(sync_dir, zip_name)
            shutil.copy2(local_zip_path, sync_zip_path)
            os.remove(local_zip_path)
            progress(100, tr("backup_finished"))
            return True, tr("backup_synced_success", path=sync_zip_path)

        progress(100, tr("backup_finished"))
        return True, tr("backup_success", path=local_zip_path)

    except subprocess.CalledProcessError as e:
        progress(0, tr("error_compressing"))
        return False, tr("error_compressing_detail", detail=e)
    except Exception as e:
        progress(0, tr("unexpected_error"))
        return False, tr("unexpected_error_detail", detail=e)
