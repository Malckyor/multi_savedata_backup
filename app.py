import os
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from config import load_config, save_config, detect_google_drive, detect_default_ppsspp, validate_ppsspp_path, detect_default_pcsx2, validate_pcsx2_path, detect_default_citra, validate_citra_path
from backup import backup_ppsspp, backup_pcsx2, backup_citra, backup_custom_dir
from restore import restore_ppsspp, restore_pcsx2, restore_citra, restore_custom_dir
from extra_backups import load_extra_backups, save_extra_backups

# Fontes padrão
FONT_DEFAULT = ("Segoe UI", 14)        # Para labels e entradas
FONT_BOLD = ("Segoe UI", 16, "bold")   # Para títulos e botões

# ====================== Variáveis globais ======================
translations = {}       # dicionário que vai guardar o idioma atual
current_language = "EN" # idioma padrão

# ===== Função para carregar idioma =====
def load_language(lang_code):
    """Carrega idioma e atualiza variável global"""
    global translations, current_language
    current_language = lang_code
    path = os.path.join("locales", f"{lang_code}.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            translations = json.load(f)
    except FileNotFoundError:
        translations = {}  # fallback

# ===== Função t() para pegar tradução =====
def t(key, *args):
    """Retorna o texto traduzido, usa key como fallback se não existir"""
    text = translations.get(key, key)
    if args:
        try:
            text = text.format(*args)
        except:
            pass
    return text

# ====================== CONFIGURAÇÕES DE COR ======================
COLORS = {
    "off": "#B23A3A",
    "off_hover": "#8F2E2E",
    "on": "#2E7D32",
    "on_hover": "#1F5A24",
    "backup": "#1976D2",
    "backup_hover": "#125AA0",
    "text": "#FFFFFF"
}

# ====================== INICIALIZAÇÃO ======================
ctk.set_appearance_mode("System")  # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")

class CTkNameDialog(ctk.CTkToplevel):
    def __init__(self, parent, title=t("name"), message=t("name_entry")):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        self.result = None

        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=message,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 10))

        self.entry = ctk.CTkEntry(frame, width=250)
        self.entry.pack(pady=(0, 15))
        self.entry.focus()

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text=t("cancel"),
            font=("Segoe UI", 16, "bold"),
            command=self.cancel
        ).pack(side="left", expand=True, padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text=t("ok"),
            font=("Segoe UI", 16, "bold"),
            fg_color=COLORS["on"],
            hover_color=COLORS["on_hover"],
            command=self.confirm
        ).pack(side="left", expand=True, padx=(5, 0))

        self.bind("<Return>", lambda e: self.confirm())
        self.bind("<Escape>", lambda e: self.cancel())

        self.update_idletasks()
        self.center(parent)

    def center(self, parent):
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def confirm(self):
        value = self.entry.get().strip()
        if value:
            self.result = value
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

class MultiSavedataBackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi Savedata Backup")  # Título

        self.config = load_config()

        # carregar idioma salvo no config.json
        saved_lang = self.config.get("language", "EN")  # pega do config ou usa EN
        load_language(saved_lang)
        
        self.extra_data = load_extra_backups()
        self.extra_units = []
        self.emulator_units = []

        # ===== Restaurar tamanho e posição da janela =====
        width = self.config.get("window_width", 900)
        height = self.config.get("window_height", 700)
        x = self.config.get("window_x")
        y = self.config.get("window_y")

        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")

        self.root.resizable(True, True)
        # ===== Registrar fechamento da janela =====
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # ===== Criar widgets e carregar dados =====
        self.create_widgets()
        self.load_defaults()
        self.update_emulator_layout()

    # ====================== CARREGA LISTA DE EXTRAS ======================
    def load_extra_units_from_json(self):
        extras = self.extra_data.get("extras", [])

        if not extras:
            # Primeira execução: cria um extra visível
            self.create_extra_unit(t("extra_default"))
            return

        for entry in extras:
            name = entry.get("name", t("extra_default"))
            path = entry.get("root_path", "")
            enabled = entry.get("enabled", True)

            path_var = ctk.StringVar(value=path)
            self.create_extra_unit(name, path_var)

            # Ajustes pós-criação
            container, _, enabled_var = self.extra_units[-1]
            enabled_var.set(enabled)

            # Atualiza botão e metadados
            container.extra_button.configure(text=name)
            container.extra_name = name
            container.extra_path = path

    # ====================== ATUALIZAR TRADUÇÃO ======================
    def update_ui_language(self):
        """Atualiza todos os textos da interface quando o idioma muda"""
        self.backup_btn.configure(text=t("start_backup"))
        self.restore_btn.configure(text=t("restore_backup"))
        self.sync_folder_label.configure(text=t("sync_folder"))
        self.choose_folder_btn.configure(text=t("choose_folder"))

        # Botões e labels dos emuladores
        for container in self.emulator_units:
            if hasattr(container, "choose_dir_btn"):
                container.choose_dir_btn.configure(text=t("choose_folder"))
            if hasattr(container, "main_btn") and hasattr(container, "name_key"):
                container.main_btn.configure(text=t(container.name_key))

        # Botões de escolher diretório dos extras
        for container, path_var, enabled_var in self.extra_units:
            if hasattr(container, "choose_dir_btn"):
                container.choose_dir_btn.configure(text=t("choose_folder"))
        
        # aqui você adiciona qualquer outro label, título, botão que dependa de idioma

    # ====================== CRIAÇÃO DE WIDGETS ======================
    def create_widgets(self):
        # ===== Container principal horizontal =====
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ===== Frame de Emuladores com Scroll =====
        self.emu_frame = ctk.CTkScrollableFrame(self.main_container, height=250, corner_radius=10)
        self.emu_frame.pack(side="left", fill="both", expand=True, padx=(0,10))

        # Variáveis de toggle
        self.ppsspp_enabled = ctk.BooleanVar(value=self.config.get("ppsspp_enabled", False))
        self.pcsx2_enabled = ctk.BooleanVar(value=self.config.get("pcsx2_enabled", False))
        self.citra_enabled = ctk.BooleanVar(value=self.config.get("citra_enabled", False))

        # ===== Frames independentes para cada emulador (botão + diretório) =====
        self.ppsspp_container = self.create_emulator_unit(
            self.emu_frame, "PPSSPP", self.toggle_ppsspp, self.choose_ppsspp, "ppsspp_var"
        )
        self.pcsx2_container = self.create_emulator_unit(
            self.emu_frame, "PCSX2", self.toggle_pcsx2, self.choose_pcsx2, "pcsx2_var"
        )
        self.citra_container = self.create_emulator_unit(
            self.emu_frame, "CITRA", self.toggle_citra, self.choose_citra, "citra_var"
        )

        # Atualiza layout inicialmente
        self.update_emulator_layout()

        # ===== Frame Extras (lado direito) com scroll =====
        self.extra_frame = ctk.CTkFrame(self.main_container, width=250, corner_radius=10)
        self.extra_frame.pack(side="right", fill="y")
        
        # ===== Frame para os botões topo (+ e tema) =====
        top_buttons_frame = ctk.CTkFrame(self.extra_frame, corner_radius=0)
        top_buttons_frame.pack(fill="x", pady=5)

        default_language = "EN"
        # Função para carregar idioma de JSON
        def create_language_dropdown(parent, default_lang):
            locales_dir = "locales"

            # Lista arquivos JSON
            languages = [f.replace(".json","").upper()[:2] for f in os.listdir(locales_dir) if f.endswith(".json")]
            if not languages:
                languages = ["EN"]

            # pega idioma salvo ou default
            language_var = ctk.StringVar(value=current_language)

            def on_language_change(choice):
                load_language(choice)
                language_var.set(choice)
                self.update_ui_language()
                self.config["language"] = choice
                save_config(self.config)

            lang_menu = ctk.CTkOptionMenu(
                master=parent,
                values=languages,
                variable=language_var,
                command=on_language_change,
                width=50,
                height=30,
                button_color="#333333",
                button_hover_color="#555555",
                dropdown_fg_color="#222222",
                dropdown_hover_color="#444444",
                text_color="#AAAAAA"
            )
            return lang_menu

        # Criar dropdown e adicionar ao frame topo
        self.language_dropdown = create_language_dropdown(top_buttons_frame, default_language)
        self.language_dropdown.pack(side="left", padx=5, pady=2)

        # Botão "+"
        self.add_extra_btn = ctk.CTkButton(
            top_buttons_frame, text="+", font=("Segoe UI", 24, "bold"),
            width=40, height=40, corner_radius=10,
            command=self.add_extra_unit
        )
        self.add_extra_btn.pack(side="left", padx=(15,5))

        # ===== Botão de Tema =====
        # Carrega tema atual do config ou usa System
        self.theme_modes = ["Dark", "System", "Light"]
        self.current_theme = self.config.get("theme_mode", "System")
        ctk.set_appearance_mode(self.current_theme)

        def toggle_theme():
            # Alterna para o próximo tema
            index = self.theme_modes.index(self.current_theme)
            index = (index + 1) % len(self.theme_modes)
            self.current_theme = self.theme_modes[index]
            ctk.set_appearance_mode(self.current_theme)
            self.theme_btn.configure(text=self.current_theme.lower())
            # Salva no config
            self.config["theme_mode"] = self.current_theme
            save_config(self.config)

        self.theme_btn = ctk.CTkButton(
            top_buttons_frame,
            text=self.current_theme.lower(),
            font=("Segoe UI", 14, "bold"),
            width=70, height=40, corner_radius=10,
            command=toggle_theme
        )
        self.theme_btn.pack(side="right", padx=(10,5))

        # Scrollable frame para conter os extras
        self.extra_scroll_frame = ctk.CTkScrollableFrame(self.extra_frame, corner_radius=0)
        self.extra_scroll_frame.pack(fill="both", expand=True)
        self.extra_scroll_frame.grid_columnconfigure(0, weight=1)  # Para centralizar extras

        # Lista para armazenar unidades extras
        self.extra_units = []
        self.load_extra_units_from_json()

        # ===== CONTAINER INFERIOR FIXO =====
        self.bottom_container = ctk.CTkFrame(self.root, corner_radius=10)
        self.bottom_container.pack(side="bottom", fill="x", padx=10, pady=10)

        # ===== Pasta sincronizada =====
        self.backup_frame = ctk.CTkFrame(self.bottom_container, corner_radius=10)
        self.backup_frame.pack(fill="x", pady=(0, 6))
        self.sync_folder_label = ctk.CTkLabel(self.backup_frame, text=t("sync_folder"), font=FONT_BOLD)
        self.sync_folder_label.pack(anchor="center")
        self.backup_var = ctk.StringVar()
        ctk.CTkEntry(self.backup_frame, textvariable=self.backup_var, font=FONT_DEFAULT).pack(fill="x", pady=5)
        self.choose_folder_btn = ctk.CTkButton(
            self.backup_frame, text=t("choose_folder"), font=FONT_BOLD,
            height=35, width=200, command=self.choose_backup_root
        )
        self.choose_folder_btn.pack(pady=5)

        # ===== Progresso =====
        self.progress_var = ctk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(self.bottom_container, variable=self.progress_var)
        self.progress_bar.pack(fill="x", pady=(0, 6))
        self.progress_label = ctk.CTkLabel(self.bottom_container, text="0%", anchor="w")
        self.progress_label.pack(fill="x")
        # Label da assinatura (à direita, mesma linha)
        self.signature_var = ctk.StringVar()
        self.signature_var.set("v1.0 \n© 2026 Malckyor")

        self.signature_label = ctk.CTkLabel(
            self.bottom_container,
            textvariable=self.signature_var,
            anchor="e",
            font=("Segoe UI", 10),
            text_color="#AAAAAA"
        )
        self.signature_label.place(relx=1.0, y=130, anchor="ne", x=-5)  # relx=1.0 → canto direito

        # ===== Botões Backup/Restore =====
        btn_frame = ctk.CTkFrame(self.bottom_container, corner_radius=0)
        btn_frame.pack(fill="x", pady=(5, 0))

        self.backup_btn = ctk.CTkButton(
            btn_frame, text=t("start_backup"),
            fg_color=COLORS["backup"],
            hover_color=COLORS["backup_hover"],
            text_color=COLORS["text"],
            font=("Segoe UI", 22, "bold"),
            height=55,
            command=self.start_backup
        )
        self.backup_btn.pack(side="left", expand=True, fill="x", padx=(0,5))

        self.restore_btn = ctk.CTkButton(
            btn_frame, text=t("restore_backup"),
            fg_color=COLORS["backup"],
            hover_color=COLORS["backup_hover"],
            text_color=COLORS["text"],
            font=("Segoe UI", 22, "bold"),
            height=55,
            command=self.start_restore
        )
        self.restore_btn.pack(side="left", expand=True, fill="x", padx=(5,0))

        # ===== Bind eficiente para redimensionamento =====
        self._resize_job = None
        self.emu_frame.bind("<Configure>", self._on_resize)

    # ====================== Função de debounce para redimensionamento ======================
    def _on_resize(self, event):
        if hasattr(self, "_resize_job") and self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(100, self.update_emulator_layout)

    # ====================== CRIA EMULADOR (BOTÃO + DIRETÓRIO) ======================
    def create_emulator_unit(self, parent, name, toggle_command, choose_command, var_name):
        container = ctk.CTkFrame(parent, corner_radius=10)
        
        # Botão sempre visível
        container.main_btn = ctk.CTkButton(container, text=name, font=("Segoe UI", 14, "bold"), height=30, command=toggle_command)
        container.main_btn.pack(fill="x", pady=(0,5))

        # Variável de diretório
        setattr(self, var_name, ctk.StringVar())

        # Frame interno apenas para o diretório
        container.dir_frame = ctk.CTkFrame(container, corner_radius=0)
        container.dir_frame.pack(fill="x")

        # Entry e botão de escolher diretório dentro do dir_frame
        ctk.CTkEntry(container.dir_frame, textvariable=getattr(self, var_name)).pack(fill="x", pady=5)
        container.choose_dir_btn = ctk.CTkButton(
            container.dir_frame,
            text=t("choose_folder"),
            font=FONT_BOLD,
            height=35,
            width=200,
            command=choose_command
        )
        container.choose_dir_btn.pack(pady=5)

        # Adiciona container à lista de emuladores
        self.emulator_units.append(container)
        return container

    # ====================== TOGGLES ======================
    def toggle_ppsspp(self):
        self.ppsspp_enabled.set(not self.ppsspp_enabled.get())
        self.config["ppsspp_enabled"] = self.ppsspp_enabled.get()
        save_config(self.config)
        self.update_emulator_layout()

    def toggle_pcsx2(self):
        self.pcsx2_enabled.set(not self.pcsx2_enabled.get())
        self.config["pcsx2_enabled"] = self.pcsx2_enabled.get()
        save_config(self.config)
        self.update_emulator_layout()

    def toggle_citra(self):
        self.citra_enabled.set(not self.citra_enabled.get())
        self.config["citra_enabled"] = self.citra_enabled.get()
        save_config(self.config)
        self.update_emulator_layout()

    # ====================== UPDATE EMULATOR LAYOUT ======================
    def update_emulator_layout(self):
        # Atualiza cores e visibilidade dos botões e frames
        for container in self.emulator_units:
            # Determina se está habilitado
            if container.main_btn.cget("text") == "PPSSPP":
                enabled = self.ppsspp_enabled.get()
            elif container.main_btn.cget("text") == "PCSX2":
                enabled = self.pcsx2_enabled.get()
            elif container.main_btn.cget("text") == "CITRA":
                enabled = self.citra_enabled.get()
            else:
                enabled = True  # caso algum outro container apareça futuramente

            # Atualiza cor do botão
            container.main_btn.configure(
                fg_color=COLORS["on"] if enabled else COLORS["off"],
                hover_color=COLORS["on_hover"] if enabled else COLORS["off_hover"],
                height=30,
                width=200
            )

            # Mostra ou esconde frame de diretório
            if enabled:
                container.dir_frame.pack(fill="x")
            else:
                container.dir_frame.pack_forget()

        # Reposiciona os containers em grid, ON primeiro
        units_sorted = sorted(
            self.emulator_units,
            key=lambda c: not (
                self.ppsspp_enabled.get() if c.main_btn.cget("text") == "PPSSPP" else
                self.pcsx2_enabled.get() if c.main_btn.cget("text") == "PCSX2" else
                self.citra_enabled.get() if c.main_btn.cget("text") == "CITRA" else True
            )
        )

        # Largura do frame e largura aproximada de cada unidade
        self.emu_frame.update_idletasks()
        frame_width = self.emu_frame.winfo_width()
        if frame_width < 10:
            frame_width = 500

        unit_width = 200
        padding_x = 5
        padding_y = 5
        units_per_row = max(1, frame_width // (unit_width + padding_x))

        # Limpa grid
        for container in self.emulator_units:
            container.grid_forget()

        # Reposiciona no grid
        for index, container in enumerate(units_sorted):
            row = index // units_per_row
            col = index % units_per_row
            container.grid(row=row, column=col, padx=padding_x, pady=padding_y, sticky="n")


    # ====================== LOAD DEFAULTS ======================
    def load_defaults(self):
        self.ppsspp_var.set(self.config.get("ppsspp_path") or detect_default_ppsspp() or "")
        self.pcsx2_var.set(self.config.get("pcsx2_path" or detect_default_pcsx2 or ""))
        self.citra_var.set(self.config.get("citra_path" or detect_default_citra or ""))
        self.backup_var.set(self.config.get("backup_root") or detect_google_drive() or "")

    # ====================== CHOOSERS ======================
    def choose_ppsspp(self):
        initial_dir = self.config.get("ppsspp_path") or detect_default_ppsspp() or os.path.expanduser("~")
        path = filedialog.askdirectory(initialdir=initial_dir)
        if not path:
            return
        if validate_ppsspp_path(path):
            self.ppsspp_var.set(path)
            self.config["ppsspp_path"] = path
            save_config(self.config)
        else:
            messagebox.showwarning(t("invalid_structure_title"),t("invalid_ppsspp_struct"))

    def choose_pcsx2(self):
        initial_dir = self.config.get("pcsx2_path") or detect_default_pcsx2() or os.path.expanduser("~")
        path = filedialog.askdirectory(initialdir=initial_dir)
        if not path:
            return
        if path and validate_pcsx2_path(path):
            self.pcsx2_var.set(path)
            self.config["pcsx2_path"] = path
            save_config(self.config)
        else:
            messagebox.showwarning(t("invalid_structure_title"),t("invalid_pcsx2_struct"))

    def choose_citra(self):
        initial_dir = self.config.get("citra_path") or detect_default_citra() or os.path.expanduser("~")
        path = filedialog.askdirectory(initialdir=initial_dir)
        if not path:
            return
        if path and validate_citra_path(path):
            self.citra_var.set(path)
            self.config["citra_path"] = path
            save_config(self.config)
        else:
            messagebox.showwarning(t("invalid_structure_title"),t("invalid_citra_struct"))

    def choose_backup_root(self):
        initial_dir = self.config.get("backup_root") or detect_google_drive() or os.path.expanduser("~")
        path = filedialog.askdirectory(initialdir=initial_dir)
        if not path:
            return
        self.backup_var.set(path)
        self.config["backup_root"] = path
        save_config(self.config)

    # ====================== BACKUP/RESTORE ======================
    def start_backup(self):
        self.progress_var.set(0)
        self.progress_label.configure(text="0%")
        threading.Thread(target=self.run_backup, daemon=True).start()

    def start_restore(self):
        self.progress_var.set(0)
        self.progress_label.configure(text="0%")
        threading.Thread(target=self.run_restore, daemon=True).start()

    def progress_callback(self, percent, message=None):
        self.progress_var.set(percent)
        self.progress_label.configure(text=f"{int(percent)}%")

    def run_backup(self):
        backup_root = self.backup_var.get()
        messages = []
        
        # PPSSPP
        if self.ppsspp_enabled.get():
            success, msg = backup_ppsspp(self.ppsspp_var.get(), backup_root, progress_callback=self.progress_callback)
            messages.append(msg)
            
        # PCSX2
        if self.pcsx2_enabled.get():
            success, msg = backup_pcsx2(self.pcsx2_var.get(), backup_root, progress_callback=self.progress_callback)
            messages.append(msg)
            
        # CITRA
        if self.citra_enabled.get():
            success, msg = backup_citra(self.citra_var.get(), backup_root, progress_callback=self.progress_callback)
            messages.append(msg)

        # ================== BACKUPS EXTRAS ==================
        extras = self.extra_data.get("extras", [])

        for extra in extras:
            if not extra.get("enabled", True):
                continue

            success, msg = backup_custom_dir(
                extra,
                backup_root,
                progress_callback=self.progress_callback
            )
            messages.append(msg)

        self.progress_var.set(100)
        self.progress_label.configure(text="100%")
        self.show_backup_messages(t("backup_finished"), messages)

    def run_restore(self):
        backup_root = self.backup_var.get()
        messages = []

        # PPSSPP
        if self.ppsspp_enabled.get():
            success, msg = restore_ppsspp(self.ppsspp_var.get(), backup_root, progress_callback=self.progress_callback)
            messages.append(msg)
            
        # PCSX2
        if self.pcsx2_enabled.get():
            success, msg = restore_pcsx2(self.pcsx2_var.get(), backup_root, progress_callback=self.progress_callback)
            messages.append(msg)
            
        # CITRA
        if self.citra_enabled.get():
            success, msg = restore_citra(self.citra_var.get(), backup_root, progress_callback=self.progress_callback)
            messages.append(msg)

        # ================== RESTORES EXTRAS ==================
        extras = self.extra_data.get("extras", [])

        for extra in extras:
            if not extra.get("enabled", True):
                continue

            success, msg = restore_custom_dir(
                extra,
                backup_root,
                progress_callback=self.progress_callback
            )
            messages.append(msg)

        self.progress_var.set(100)
        self.progress_label.configure(text="100%")
        messagebox.showinfo(t("restore_finished"), "\n\n".join(messages))

    # ================== BACKUP MESSAGES ==================        
    def show_backup_messages(self, title, messages):
        """
        Cria uma janela moderna CTk para exibir mensagens de backup/restore.
        """
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("480x320")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # Centralizar
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 240
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 160
        dialog.geometry(f"+{x}+{y}")

        # Label com texto explicativo
        text_frame = ctk.CTkScrollableFrame(dialog)
        text_frame.pack(fill="both", expand=True, padx=15, pady=15)

        for msg in messages:
            ctk.CTkLabel(
                text_frame,
                text=msg,
                font=("Segoe UI", 14),
                wraplength=440,
                justify="left"
            ).pack(anchor="w", pady=5)

        # Botão OK
        ok_btn = ctk.CTkButton(
            dialog,
            text=t("ok"),
            width=120,
            fg_color=COLORS["on"],
            hover_color=COLORS["on_hover"],
            command=dialog.destroy
        )
        ok_btn.pack(pady=(0, 15))

    # ====================== FUNÇÕES DE EXTRAS ======================
    def create_extra_unit(self, name, path_var=None):
        container = ctk.CTkFrame(self.extra_scroll_frame, corner_radius=10)

        enabled_var = ctk.BooleanVar(value=True)

        if path_var is None:
            path_var = ctk.StringVar()

        # Botão principal (nome do Extra)
        btn = ctk.CTkButton(
            container,
            text=name,
            font=("Segoe UI", 16, "bold"),
            height=30,
            width=200,
            fg_color=COLORS["on"],
            hover_color=COLORS["on_hover"],
            text_color=COLORS["text"],
            command=lambda c=container: self.show_remove_extra_dialog(c)
        )
        btn.pack(fill="x", pady=(0, 5))
        container.extra_button = btn  # referência principal

        # Frame interno
        dir_frame = ctk.CTkFrame(container, corner_radius=0)
        dir_frame.pack(fill="x")
        container.dir_frame = dir_frame  # referência para pack_forget / pack

        # Entry
        ctk.CTkEntry(dir_frame, textvariable=path_var).pack(fill="x", pady=5)

        # Botão de escolher diretório (referência para update_ui_language)
        choose_btn = ctk.CTkButton(
            dir_frame,
            text=t("choose_folder"),
            font=FONT_BOLD,
            height=35,
            width=200,
            command=lambda c=container, v=path_var: self.choose_extra_dir(c, v)
        )
        choose_btn.pack(pady=5)
        container.choose_dir_btn = choose_btn  # referência para atualizar texto

        # Salva unidade extra
        self.extra_units.append((container, path_var, enabled_var))
        self.update_extra_layout()

        return container  # importante retornar para usar na criação e layout


    def update_extra_layout(self):
        for index, (container, _, _) in enumerate(self.extra_units):
            container.grid(row=index, column=0, padx=5, pady=5, sticky="n")

    def add_extra_unit(self):
        name = f"{t('extra_default')} {len(self.extra_units) + 1}"
        self.create_extra_unit(name)

    def choose_extra_dir(self, container, var):
        # Se já existe caminho registrado, abre na pasta antiga, senão abre no padrão
        initial_dir = getattr(container, "extra_path", None) or os.path.expanduser("~")
        
        path = filedialog.askdirectory(initialdir=initial_dir)
        if not path:
            return

        # Pergunta o nome do Extra
        dialog = CTkNameDialog(
            self.root,
            title=t("backup_name_window"),
            message=t("backup_window")
        )
        self.root.wait_window(dialog)

        name = dialog.result
        if not name:
            return

        base_folder = os.path.basename(os.path.normpath(path))

        # Atualiza UI
        var.set(path)
        container.extra_button.configure(text=name)

        # Salva metadados no container
        container.extra_name = name
        container.extra_path = path

        # Atualiza / cria registro no JSON
        extras = self.extra_data["extras"]
        existing = next((e for e in extras if e["name"] == name), None)

        payload = {
            "name": name,
            "root_path": path,
            "base_folder": base_folder,
            "structure": [],
            "enabled": True
        }

        if existing:
            existing.update(payload)
        else:
            extras.append(payload)

        save_extra_backups(self.extra_data)

    def remove_extra_unit(self, container):
        # Remove do frame e da lista
        for i, (cont, var, enabled_var) in enumerate(self.extra_units):
            if cont == container:
                cont.destroy()
                self.extra_units.pop(i)
                break
        self.update_extra_layout()

    # ====================== JANELA DE REMOÇÃO DE EXTRA ======================
    def show_remove_extra_dialog(self, container):
        # Verifica se o extra tem nome registrado
        name = getattr(container, "extra_name", None)
        if not name:
            # Extra recém-criado, sem registro: remove só da UI
            self.remove_extra_unit(container)
            return

        # Carrega dados extras atuais do JSON
        extras = self.extra_data.get("extras", [])
        # Verifica se esse extra tem registro salvo
        has_saved_data = any(e.get("name") == name for e in extras if isinstance(e, dict))

        if not has_saved_data:
            # Se não tiver dados salvos, apenas remove da UI
            self.remove_extra_unit(container)
            return

        # ===== Cria diálogo para confirmação =====
        root = self.root

        dialog = ctk.CTkToplevel(root)
        dialog.title(t("backup_manage_window"))
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()

        # Centralizar
        root.update_idletasks()

        x = root.winfo_x() + (root.winfo_width() // 2) - 210
        y = root.winfo_y() + (root.winfo_height() // 2) - 110

        dialog.geometry(f"+{x}+{y}")

        # Texto explicativo
        label = ctk.CTkLabel(
            dialog,
            text=t("backup_manage",
                name
            ),
            justify="center",
            font=("Segoe UI", 14)
        )
        label.pack(padx=20, pady=20)

        # Frame de botões
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        # Funções dos botões
        def confirm():
            # Remove do JSON e UI
            if name:
                self.extra_data["extras"] = [
                    e for e in self.extra_data.get("extras", [])
                    if e.get("name") != name
                ]
                save_extra_backups(self.extra_data)
            self.remove_extra_unit(container)
            dialog.destroy()

        def remove_only_ui():
            self.remove_extra_unit(container)
            dialog.destroy()

        def cancel():
            dialog.destroy()

        # Botões
        ctk.CTkButton(
            btn_frame, text=t("yes"),
            width=100,
            fg_color=COLORS["off"],
            hover_color=COLORS["off_hover"],
            command=confirm
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            btn_frame, text=t("no"),
            width=100,
            command=remove_only_ui
        ).grid(row=0, column=1, padx=8)

        ctk.CTkButton(
            btn_frame, text=t("cancel"),
            width=100,
            fg_color=COLORS["on"],
            hover_color=COLORS["on_hover"],
            command=cancel
        ).grid(row=0, column=2, padx=8)

    # ====================== SALVAR E FECHAR ======================
    def on_close(self):
        # Salva tamanho e posição da janela
        self.config["window_width"] = self.root.winfo_width()
        self.config["window_height"] = self.root.winfo_height()
        self.config["window_x"] = self.root.winfo_x()
        self.config["window_y"] = self.root.winfo_y()
        save_config(self.config)
        # Fecha a janela
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = MultiSavedataBackupApp(root)
    root.mainloop()
