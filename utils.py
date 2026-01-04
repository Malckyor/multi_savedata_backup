import os

def find_compressor():
    """Localiza WinRAR ou 7-Zip no sistema"""
    # WinRAR
    rar = r"C:/Program Files/WinRAR/WinRAR.exe"
    if os.path.exists(rar):
        return "winrar", rar

    # 7-Zip
    seven = r"C:/Program Files/7-Zip/7z.exe"
    if os.path.exists(seven):
        return "7zip", seven

    return None, None
