import os
import shutil
import subprocess
from utils import find_compressor
import json

# ===================== LOCALE DINÂMICO =====================
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

# ===================== FUNÇÕES DE RESTAURAÇÃO =====================

def restore_ppsspp(ppsspp_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    memstick_psp = os.path.join(ppsspp_path, "memstick", "PSP")
    direct_psp = os.path.join(ppsspp_path, "PSP")

    if os.path.isdir(os.path.join(ppsspp_path, "memstick")):
        psp_dir = memstick_psp
    else:
        psp_dir = direct_psp

    savedata_dir = os.path.join(psp_dir, "SAVEDATA")
    os.makedirs(savedata_dir, exist_ok=True)

    backups = [
        f for f in os.listdir(sync_dir)
        if f.startswith("PPSSPP_SAVES_") and f.endswith(".zip")
    ]
    if not backups:
        return False, tr("no_backup_found", emulator="PPSSPP")

    backups.sort(reverse=True)
    zip_name = backups[0]
    zip_sync_path = os.path.join(sync_dir, zip_name)

    progress(30, tr("copying_backup"))
    zip_local_path = os.path.join(psp_dir, zip_name)
    shutil.copy2(zip_sync_path, zip_local_path)

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    progress(50, tr("extracting_backup"))
    try:
        if tool == "winrar":
            cmd = [exe, "x", "-y", zip_local_path, savedata_dir]
        else:
            cmd = [exe, "x", "-y", zip_local_path, f"-o{savedata_dir}"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        progress(0, tr("error_extracting"))
        return False, tr("error_extracting_detail", detail=e)

    progress(90, tr("removing_temp_file"))
    try:
        os.remove(zip_local_path)
    except Exception:
        pass

    progress(100, tr("restore_finished"))
    return True, tr("restore_success", path=zip_name)

# =======================================================

def restore_pcsx2(pcsx2_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    memcards_dir = os.path.join(pcsx2_path, "memcards")
    os.makedirs(memcards_dir, exist_ok=True)

    backups = [
        f for f in os.listdir(sync_dir)
        if f.startswith("PCSX2_MEMCARDS_") and f.endswith(".zip")
    ]
    if not backups:
        return False, tr("no_backup_found", emulator="PCSX2")

    backups.sort(reverse=True)
    zip_name = backups[0]
    zip_sync_path = os.path.join(sync_dir, zip_name)

    progress(30, tr("copying_backup"))
    zip_local_path = os.path.join(pcsx2_path, zip_name)
    shutil.copy2(zip_sync_path, zip_local_path)

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    progress(50, tr("extracting_backup"))
    try:
        if tool == "winrar":
            cmd = [exe, "x", "-y", zip_local_path, memcards_dir]
        else:
            cmd = [exe, "x", "-y", zip_local_path, f"-o{memcards_dir}"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        progress(0, tr("error_extracting"))
        return False, tr("error_extracting_detail", detail=e)

    progress(90, tr("removing_temp_file"))
    try:
        os.remove(zip_local_path)
    except Exception:
        pass

    progress(100, tr("restore_finished"))
    return True, tr("restore_success", path=zip_name)

# =======================================================

def restore_citra(citra_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    sdmc_dir = os.path.join(citra_path, "sdmc")
    os.makedirs(sdmc_dir, exist_ok=True)

    backups = [
        f for f in os.listdir(sync_dir)
        if f.startswith("CITRA_SDMC_") and f.endswith(".zip")
    ]
    if not backups:
        return False, tr("no_backup_found", emulator="CITRA")

    backups.sort(reverse=True)
    zip_name = backups[0]
    zip_sync_path = os.path.join(sync_dir, zip_name)

    progress(30, tr("copying_backup"))
    zip_local_path = os.path.join(citra_path, zip_name)
    shutil.copy2(zip_sync_path, zip_local_path)

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    progress(50, tr("extracting_backup"))
    try:
        if tool == "winrar":
            cmd = [exe, "x", "-y", zip_local_path, sdmc_dir]
        else:
            cmd = [exe, "x", "-y", zip_local_path, f"-o{sdmc_dir}"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        progress(0, tr("error_extracting"))
        return False, tr("error_extracting_detail", detail=e)

    progress(90, tr("removing_temp_file"))
    try:
        os.remove(zip_local_path)
    except Exception:
        pass

    progress(100, tr("restore_finished"))
    return True, tr("restore_success", path=zip_name)

# =======================================================

def restore_custom_dir(dir_entry, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    name = dir_entry.get("name")
    root_path = dir_entry.get("root_path")

    if not name or not root_path:
        return False, tr("custom_restore_invalid")

    if not os.path.isdir(root_path):
        return False, tr("folder_not_found", folder=name)

    safe_name = name.replace(" ", "_")

    backups = [
        f for f in os.listdir(sync_dir)
        if f.startswith(f"{safe_name}_") and f.endswith(".zip")
    ]
    if not backups:
        return False, tr("no_backup_found", emulator=name)

    backups.sort(reverse=True)
    zip_name = backups[0]
    zip_sync_path = os.path.join(sync_dir, zip_name)

    progress(30, tr("copying_backup_name", name=name))
    zip_local_path = os.path.join(root_path, zip_name)
    shutil.copy2(zip_sync_path, zip_local_path)

    tool, exe = find_compressor()
    if not exe:
        return False, tr("compressor_not_found")

    progress(50, tr("extracting_backup_name", name=name))
    try:
        if tool == "winrar":
            cmd = [exe, "x", "-y", zip_local_path, root_path]
        else:
            cmd = [exe, "x", "-y", zip_local_path, f"-o{root_path}"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        progress(0, tr("error_extracting_detail_name", name=name, detail=e))
        return False, tr("error_extracting_detail_name", name=name, detail=e)

    progress(90, tr("removing_temp_file"))
    try:
        os.remove(zip_local_path)
    except Exception:
        pass

    progress(100, tr("restore_finished"))
    return True, tr("restore_success_name", name=name, path=zip_name)
