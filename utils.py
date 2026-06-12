import os
import time
import subprocess
import json
from pathlib import Path

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

# ===================== VERIFICAÇÃO DO COMPRESSOR =====================
def find_compressor():
    # Localiza WinRAR ou 7-Zip no sistema

    program_dirs = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramFiles(x86)")
    ]

    # WinRAR
    for base in program_dirs:
        if base:
            rar = Path(base) / "WinRAR" / "WinRAR.exe"
            if rar.exists():
                return "winrar", str(rar)

    # 7-Zip
    for base in program_dirs:
        if base:
            seven = Path(base) / "7-Zip" / "7z.exe"
            if seven.exists():
                return "7zip", str(seven)

    return None, None

# ===================== VERIFICAÇÃO DO GOOGLE DRIVE =====================
def ensure_sync_client_running(sync_dir, progress_callback=None):
    def progress(percent, message=None):
        if progress_callback:
            progress_callback(percent, message)

    try:
        output = subprocess.check_output("tasklist", shell=True).decode(errors="ignore")
        if "GoogleDriveFS.exe" in output:
            progress(5, tr("waiting_google_drive"))

            for _ in range(30):
                if os.path.exists(sync_dir):
                    return True, None
                time.sleep(1)
            return False, tr("google_drive_timeout")

    except Exception as e:
        print(e)

    possible_paths = []
    possible_paths.append(
        os.path.join(os.getenv("LOCALAPPDATA", ""), "Google", "DriveFS", "GoogleDriveFS.exe")
    )

    versioned_base = os.path.join(
        os.getenv("ProgramFiles", ""), "Google", "Drive File Stream"
    )
    if os.path.isdir(versioned_base):
        for folder in os.listdir(versioned_base):
            full = os.path.join(versioned_base, folder)

            if not os.path.isdir(full):
                continue

            exe = os.path.join(full, "GoogleDriveFS.exe")
            possible_paths.append(exe)

    for exe in possible_paths:
        if os.path.exists(exe):
            try:
                subprocess.Popen(exe)
                progress(5, tr("waiting_google_drive"))

                import time
                for _ in range(30):  # espera até 30 segundos
                    if os.path.exists(sync_dir):
                        return True, None
                    time.sleep(1)

                return False, tr("google_drive_start_failed")
            except Exception as e:
                print(e)

    return False, tr("google_drive_not_found")