import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

from config.repo_selector import obtener_repositorios
from helpers.gui_utils import cargar_commits, hacer_push


class CommitsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.build_ui()
        self.apply_theme()  # aplica el tema inicial

    # -----------------------------
    #         UI
    # -----------------------------
    def build_ui(self):
        # === TOP BAR: todo en una sola línea ===
        self.top_bar = tk.Frame(self)
        self.top_bar.pack(fill="x", pady=5, padx=5)

        # --- Cargar iconos AQUÍ ---
        self.icon_refresh = tk.PhotoImage(file="icons/refresh.png")
        self.icon_folder = tk.PhotoImage(file="icons/folder.png")
        self.icon_push = tk.PhotoImage(file="icons/push.png")

        # --- INFO LABELS EN LA MISMA LINEA ---
        self.lbl_commits = tk.Label(self.top_bar, text="Commits: 0", font=("Arial", 11))
        self.lbl_commits.pack(side="left", padx=10)

        self.lbl_pushes = tk.Label(self.top_bar, text="Pushes: 0", font=("Arial", 11))
        self.lbl_pushes.pack(side="left", padx=10)

        self.lbl_project_start = tk.Label(self.top_bar, text="Inicio del proyecto: -", font=("Arial", 11))
        self.lbl_project_start.pack(side="left", padx=10)

        self.lbl_total_time = tk.Label(self.top_bar, text="Tiempo total: 0:00:00", font=("Arial", 11))
        self.lbl_total_time.pack(side="left", padx=10)

        self.lbl_days_passed = tk.Label(self.top_bar, text="Días: 0", font=("Arial", 11))
        self.lbl_days_passed.pack(side="left", padx=10)

        # Label repositorio
        self.title_label = tk.Label(self.top_bar, text="Repositorio:")
        self.title_label.pack(side="left", padx=5)

        # Combobox repositorios
        repositorios = obtener_repositorios()
        self.repo_choices = list(repositorios.values())
        self.selected_repo = tk.StringVar(value=self.repo_choices[0])

        self.repo_menu = ttk.Combobox(
            self.top_bar,
            textvariable=self.selected_repo,
            values=self.repo_choices,
            state="readonly",
            width=50,
            style="Custom.TCombobox"
        )
        self.repo_menu.pack(side="left", padx=10)

        # --- ICON BUTTONS A LA DERECHA ---

        t = self.controller.themes[self.controller.theme]
        self.btn_select = tk.Button(
            self.top_bar,
            image=self.icon_folder,
            command=self.actualizar_commits,
            bg=t["bg"],
            activebackground=t["button_active"],
            bd=0
        )
        self.btn_select.pack(side="right", padx=5)

        self.btn_update = tk.Button(
            self.top_bar,
            image=self.icon_refresh,
            command=self.actualizar_commits,
            bg=t["bg"],
            activebackground=t["button_active"],
            bd=0
        )
        self.btn_update.pack(side="right", padx=5)

        self.btn_push = tk.Button(
            self.top_bar,
            image=self.icon_push,
            command=self.hacer_push,
            bg=t["bg"],
            activebackground=t["button_active"],
            bd=0
        )
        self.btn_push.pack(side="right", padx=5)

        # === TREEVIEW ===
        columns = ("SHA", "Commit Date", "Time", "Message")

        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col != "Message" else 400)

        self.tree.pack(fill="both", expand=True, pady=10)

    # -----------------------------
    #         LÓGICA
    # -----------------------------
    def actualizar_commits(self):
        commits = cargar_commits(
            self.selected_repo.get(),
            self.tree,
            self.lbl_commits,
            self.lbl_pushes,
            self.lbl_total_time
        )

        if not commits:
            return

        # --- Helpers internos ---
        def parse_date(s):
            if not s:
                return None
            # intentar isoformat (con o sin tz)
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                pass
            # fallback a formatos comunes
            fmts = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
            for f in fmts:
                try:
                    return datetime.strptime(s, f)
                except Exception:
                    continue
            return None

        def get_commit_message(c):
            # comprobar varias claves posibles
            for k in ("message", "commit_message", "msg", "body"):
                if k in c and c[k]:
                    return str(c[k])
            # si la estructura usa nested dict
            if "commit" in c and isinstance(c["commit"], dict):
                for k in ("message", "committer", "author"):
                    if k in c["commit"] and c["commit"][k]:
                        return str(c["commit"].get("message", ""))
            return ""

        def get_commit_date(c):
            for k in ("commit_date", "date", "committed_date", "commit_date_iso"):
                if k in c and c[k]:
                    parsed = parse_date(str(c[k]))
                    if parsed:
                        return parsed
            # nested commit.date
            if "commit" in c and isinstance(c["commit"], dict) and "author" in c["commit"] and isinstance(c["commit"]["author"], dict):
                d = c["commit"]["author"].get("date") or c["commit"]["author"].get("commit_date")
                if d:
                    parsed = parse_date(str(d))
                    if parsed:
                        return parsed
            return None

        # --- Parsear todas las fechas ---
        parsed_commits = []
        for c in commits:
            date = get_commit_date(c)
            msg = get_commit_message(c)
            parsed_commits.append({"raw": c, "date": date, "message": msg})

        # DEBUG: mostrar un ejemplo si algo va mal (borra o comenta si no quieres prints)
        # print("Ejemplo commit:", parsed_commits[0] if parsed_commits else "sin commits")

        # Obtener fecha mínima (primer commit real)
        fechas_validas = [p["date"] for p in parsed_commits if p["date"] is not None]
        if not fechas_validas:
            # no hemos podido parsear fechas
            self.lbl_project_start.config(text="Inicio del proyecto: ?")
            self.lbl_days_passed.config(text="Días transcurridos: ? (no se pudieron leer fechas)")
            return

        fecha_primera = min(fechas_validas)

        # Buscar el commit con [END] (buscamos el más reciente que contenga la etiqueta)
        commit_end = None
        pattern = re.compile(r"\[END\]", re.IGNORECASE)
        # Buscar el commit más reciente que contenga [END] (recorremos parsed_commits por su fecha descendente)
        parsed_commits_sorted = sorted([p for p in parsed_commits if p["date"] is not None], key=lambda x: x["date"], reverse=True)
        for p in parsed_commits_sorted:
            if p["message"] and pattern.search(p["message"]):
                commit_end = p
                break

        if commit_end:
            fecha_fin = commit_end["date"]
            proyecto_finalizado = True
        else:
            fecha_fin = datetime.now()
            proyecto_finalizado = False

        # Calcular días (asegurarnos >= 0)
        dias_pasados = (fecha_fin.date() - fecha_primera.date()).days
        if dias_pasados < 0:
            dias_pasados = 0

        # Actualizar labels
        self.lbl_project_start.config(text=f"Inicio del proyecto: {fecha_primera.date()}")

        if proyecto_finalizado:
            # mostrar la fecha de finalización también si quieres
            self.lbl_days_passed.config(text=f"Días transcurridos: {dias_pasados} (final: {fecha_fin.date()})")
            # opcional: desactivar botones
            try:
                self.btn_push.config(state="disabled")
                self.btn_update.config(state="disabled")
            except Exception:
                pass
        else:
            self.lbl_days_passed.config(text=f"Días transcurridos: {dias_pasados}")
            try:
                self.btn_push.config(state="normal")
                self.btn_update.config(state="normal")
            except Exception:
                pass

    def hacer_push(self):
        hacer_push(
            self.selected_repo.get(),
            self.tree,
            self.lbl_commits,
            self.lbl_pushes,
            self.lbl_total_time
        )

    # -----------------------------
    #      CAMBIO DE TEMA
    # -----------------------------
    def apply_theme(self):
        t = self.controller.themes[self.controller.theme]

        self.config(bg=t["bg"])
        self.top_bar.config(bg=t["bg"])

        # labels
        labels = [
            self.title_label,
            self.lbl_commits,
            self.lbl_pushes,
            self.lbl_total_time,
            self.lbl_project_start,
            self.lbl_days_passed
        ]
        for lbl in labels:
            lbl.config(bg=t["bg"], fg=t["fg"])

        # botones (iconos)
        buttons = [self.btn_select, self.btn_update, self.btn_push]
        for btn in buttons:
            btn.config(
                bg=t["button_bg"],
                fg=t["fg"],
                activebackground=t["button_active"],
                activeforeground=t["fg"]
            )

        # estilos ttk
        style = ttk.Style()
        style.theme_use("default")

        # Colores según el tema
        combo_bg = "#3b3b3b" if self.controller.theme == "dark" else "white"
        combo_fg = t["fg"]
        combo_select_bg = t["button_active"]
        
        # Combobox - campo principal
        style.configure(
            "Custom.TCombobox",
            fieldbackground=combo_bg,
            background=t["button_bg"],
            foreground=combo_fg,
            arrowcolor=combo_fg,
            bordercolor=t["button_bg"],
            lightcolor=t["button_bg"],
            darkcolor=t["button_bg"]
        )
        
        # Combobox - estados
        style.map('Custom.TCombobox',
            fieldbackground=[('readonly', combo_bg)],
            selectbackground=[('readonly', combo_bg)],
            selectforeground=[('readonly', combo_fg)]
        )
        
        # CRÍTICO: Configurar el Listbox del dropdown
        self.controller.option_add('*TCombobox*Listbox.background', combo_bg)
        self.controller.option_add('*TCombobox*Listbox.foreground', combo_fg)
        self.controller.option_add('*TCombobox*Listbox.selectBackground', combo_select_bg)
        self.controller.option_add('*TCombobox*Listbox.selectForeground', combo_fg)

        # Treeview
        tree_bg = "#2d2d2d" if self.controller.theme == "dark" else "white"
        style.configure(
            "Treeview",
            background=tree_bg,
            foreground=t["fg"],
            fieldbackground=tree_bg
        )
        style.configure(
            "Treeview.Heading",
            background=t["button_bg"],
            foreground=t["fg"]
        )
        style.map("Treeview",
            background=[('selected', t["button_active"])],
            foreground=[('selected', t["fg"])]
        )