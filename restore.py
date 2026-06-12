import os
import shutil
import subprocess
from utils import find_compressor
import re
import json

# ===================== PADRONIZAR NOMES ====================
def normalize_backup_name(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

# ===================== CONFIGURAÇÃO DE LOCALE =====================
def get_translations():
    # Carrega o idioma atual do config.json e retorna o dicionário de traduções.
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
    # Retorna a tradução atual da chave, recarregando o idioma se necessário.
    translations = get_translations()
    text = translations.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

# ===================== FUNÇÕES DE RESTAURAÇÃO STEAM =====================
def restore_steam(steam_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        userdata_dir = os.path.join(steam_path, "userdata")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
        os.makedirs(userdata_dir, exist_ok=True)

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("STEAM_USERDATA_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="STEAM")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(userdata_dir, zip_name)
        shutil.copy2(zip_sync_path, zip_local_path)

        tool, exe = find_compressor()
        if not exe:
            return False, tr("compressor_not_found")

        progress(50, tr("extracting_backup"))
        try:
            if tool == "winrar":
                cmd = [exe, "x", "-y", zip_local_path, userdata_dir]
            else:
                cmd = [exe, "x", "-y", zip_local_path, f"-o{userdata_dir}"]
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="STEAM"))
        return False, tr("permission_denied_emulator", emulator="STEAM")

# ===================== FUNÇÕES DE RESTAURAÇÃO PPSSPP =====================
def restore_ppsspp(ppsspp_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        memstick_psp = os.path.join(ppsspp_path, "memstick", "PSP")
        direct_psp = os.path.join(ppsspp_path, "PSP")

        if os.path.isdir(os.path.join(ppsspp_path, "memstick")):
            psp_dir = memstick_psp
        else:
            psp_dir = direct_psp

        savedata_dir = os.path.join(psp_dir, "SAVEDATA")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="PPSSPP"))
        return False, tr("permission_denied_emulator", emulator="PPSSPP")

# ===================== FUNÇÕES DE RESTAURAÇÃO VITA3K =====================
def restore_vita3k(vita3k_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        savedata = os.path.join(vita3k_path, "Vita3K", "ux0", "user")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
        os.makedirs(savedata, exist_ok=True)

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("VITA3K_SAVEDATA_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="VITA3K")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(vita3k_path, zip_name)
        shutil.copy2(zip_sync_path, zip_local_path)

        tool, exe = find_compressor()
        if not exe:
            return False, tr("compressor_not_found")

        progress(50, tr("extracting_backup"))
        try:
            if tool == "winrar":
                cmd = [exe, "x", "-y", zip_local_path, savedata]
            else:
                cmd = [exe, "x", "-y", zip_local_path, f"-o{savedata}"]
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="VITA3K"))
        return False, tr("permission_denied_emulator", emulator="VITA3K")

# ===================== FUNÇÕES DE RESTAURAÇÃO DUCKSTATION =====================
def restore_duckstation(duckstation_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        memcards_dir = os.path.join(duckstation_path, "memcards")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
        os.makedirs(memcards_dir, exist_ok=True)

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("DUCKSTATION_MEMCARDS_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="DUCKSTATION")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(duckstation_path, zip_name)
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="DUCKSTATION"))
        return False, tr("permission_denied_emulator", emulator="DUCKSTATION")

# ===================== FUNÇÕES DE RESTAURAÇÃO PCSX2 =====================
def restore_pcsx2(pcsx2_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        memcards_dir = os.path.join(pcsx2_path, "memcards")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="PCSX2"))
        return False, tr("permission_denied_emulator", emulator="PCSX2")

# ===================== FUNÇÕES DE RESTAURAÇÃO RPCS3 =====================
def restore_rpcs3(rpcs3_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        savedata_dir = os.path.join(rpcs3_path, "dev_hdd0", "savedata")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
        os.makedirs(savedata_dir, exist_ok=True)

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("RPCS3_SAVEDATA_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="RPCS3")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(rpcs3_path, zip_name)
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="RPCS3"))
        return False, tr("permission_denied_emulator", emulator="RPCS3")

# ===================== FUNÇÕES DE RESTAURAÇÃO MELONDS =====================
def restore_melonds(melonds_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        save_dir = melonds_path
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
        # os.makedirs(save_dir, exist_ok=True)

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("MELONDS_SAVE_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="MELONDS")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(melonds_path, zip_name)
        shutil.copy2(zip_sync_path, zip_local_path)

        tool, exe = find_compressor()
        if not exe:
            return False, tr("compressor_not_found")

        progress(50, tr("extracting_backup"))
        try:
            if tool == "winrar":
                cmd = [exe, "x", "-y", zip_local_path, save_dir]
            else:
                cmd = [exe, "x", "-y", zip_local_path, f"-o{save_dir}"]
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="MELONDS"))
        return False, tr("permission_denied_emulator", emulator="MELONDS")

# ===================== FUNÇÕES DE RESTAURAÇÃO CITRA =====================
def restore_citra(citra_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        sdmc_dir = os.path.join(citra_path, "sdmc")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="CITRA"))
        return False, tr("permission_denied_emulator", emulator="CITRA")

# ===================== FUNÇÕES DE RESTAURAÇÃO PROJECT64 =====================
def restore_project64(project64_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        save_dir = os.path.join(project64_path, "Save")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)

        if not os.path.isdir(save_dir):
            return False, tr("folder_not_found", folder="Save", emulator="PROJECT64")

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("PROJECT64_SAVE_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="PROJECT64")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(project64_path, zip_name)
        shutil.copy2(zip_sync_path, zip_local_path)

        tool, exe = find_compressor()
        if not exe:
            return False, tr("compressor_not_found")

        progress(50, tr("extracting_backup"))
        try:
            if tool == "winrar":
                cmd = [exe, "x", "-y", zip_local_path, save_dir]
            else:
                cmd = [exe, "x", "-y", zip_local_path, f"-o{save_dir}"]
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="PROJECT64"))
        return False, tr("permission_denied_emulator", emulator="PROJECT64")

# ===================== FUNÇÕES DE RESTAURAÇÃO DOLPHIN =====================
def restore_dolphin(dolphin_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        for folder in ["GBA", "GC", "Wii"]:
            if not os.path.exists(sync_dir):
                return False, tr("sync_folder_not_found", path=sync_dir)
            os.makedirs(
                os.path.join(dolphin_path, folder),
                exist_ok=True
            )

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("DOLPHIN_SAVES_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="DOLPHIN")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(dolphin_path, zip_name)
        shutil.copy2(zip_sync_path, zip_local_path)

        tool, exe = find_compressor()
        if not exe:
            return False, tr("compressor_not_found")

        progress(50, tr("extracting_backup"))
        try:
            if tool == "winrar":
                cmd = [exe, "x", "-y", zip_local_path, dolphin_path]
            else:
                cmd = [exe, "x", "-y", zip_local_path, f"-o{dolphin_path}"]
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="DOLPHIN"))
        return False, tr("permission_denied_emulator", emulator="DOLPHIN")

# ===================== FUNÇÕES DE RESTAURAÇÃO CEMU =====================
def restore_cemu(cemu_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        save_dir = os.path.join(cemu_path, "mlc01", "usr", "save")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
        os.makedirs(save_dir, exist_ok=True)

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("CEMU_SAVE_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="CEMU")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(cemu_path, zip_name)
        shutil.copy2(zip_sync_path, zip_local_path)

        tool, exe = find_compressor()
        if not exe:
            return False, tr("compressor_not_found")

        progress(50, tr("extracting_backup"))
        try:
            if tool == "winrar":
                cmd = [exe, "x", "-y", zip_local_path, save_dir]
            else:
                cmd = [exe, "x", "-y", zip_local_path, f"-o{save_dir}"]
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="CEMU"))
        return False, tr("permission_denied_emulator", emulator="CEMU")

# ===================== FUNÇÕES DE RESTAURAÇÃO EDEN =====================
def restore_eden(eden_path, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        save_dir = os.path.join(eden_path, "nand", "user", "save")
        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)
        os.makedirs(save_dir, exist_ok=True)

        backups = [
            f for f in os.listdir(sync_dir)
            if f.startswith("EDEN_SAVE_") and f.endswith(".zip")
        ]
        if not backups:
            return False, tr("no_backup_found", emulator="EDEN")

        backups.sort(reverse=True)
        zip_name = backups[0]
        zip_sync_path = os.path.join(sync_dir, zip_name)

        progress(30, tr("copying_backup"))
        zip_local_path = os.path.join(eden_path, zip_name)
        shutil.copy2(zip_sync_path, zip_local_path)

        tool, exe = find_compressor()
        if not exe:
            return False, tr("compressor_not_found")

        progress(50, tr("extracting_backup"))
        try:
            if tool == "winrar":
                cmd = [exe, "x", "-y", zip_local_path, save_dir]
            else:
                cmd = [exe, "x", "-y", zip_local_path, f"-o{save_dir}"]
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

    except PermissionError:
        progress(0, tr("permission_denied_emulator", emulator="EDEN"))
        return False, tr("permission_denied_emulator", emulator="EDEN")

# ===================== FUNÇÕES DE RESTAURAÇÃO EXTRAS =====================
def restore_custom_dir(dir_entry, sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    name = dir_entry.get("name")
    root_path = dir_entry.get("root_path")

    try:
        if not name or not root_path:
            return False, tr("custom_restore_invalid")

        if not os.path.isdir(root_path):
            return False, tr("folder_not_found", folder=name, emulator=name)

        if not os.path.exists(sync_dir):
            return False, tr("sync_folder_not_found", path=sync_dir)

        target_name = normalize_backup_name(name)
        backups = []
        for filename in os.listdir(sync_dir):
            if not filename.endswith(".zip"):
                continue
            stem = filename[:-4]  # remove .zip
            match = re.match(
                r"^(.*?)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$",
                stem
            )
            if not match:
                continue
            backup_name = match.group(1)
            timestamp = match.group(2)

            if normalize_backup_name(backup_name) == target_name:
                backups.append((timestamp, filename))

        if not backups:
            return False, tr("extra_no_backup_found", emulator=name)

        # Pega o backup mais recente
        latest_backup = max(backups, key=lambda x: x[0])
        zip_name = latest_backup[1]
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
    
    except PermissionError:
        progress(0, tr("permission_denied_name", name=name))
        return False, tr("permission_denied_name", name=name)