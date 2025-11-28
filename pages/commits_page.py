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
        t = self.controller.themes[self.controller.theme]

        # -------- TOP BAR --------
        self.top_bar = tk.Frame(self, height=50, bg=t["bg"], bd=1, relief="raised")
        self.top_bar.pack(fill="x", pady=5, padx=5)

        # --- Cargar iconos ---
        self.icon_refresh = tk.PhotoImage(file="icons/refresh.png")
        self.icon_folder = tk.PhotoImage(file="icons/folder.png")
        self.icon_push = tk.PhotoImage(file="icons/push.png")

        # --- CONTENEDOR PRINCIPAL ---
        self.main_container = tk.Frame(self, bg=t["bg"], bd=3, relief="solid",width=700, height=300)
        self.main_container.pack(padx=10, pady=10)
        self.main_container.pack_propagate(False) 

        # Configurar grid en main_container
        self.main_container.grid_rowconfigure(0, minsize=200)
        self.main_container.grid_columnconfigure(0, weight=2)  # left panel 2/3
        self.main_container.grid_columnconfigure(1, weight=1)  # treeview 1/3

        # --- LEFT PANEL (stats, labels) ---
        self.left_panel = tk.Frame(self.main_container, bg=t["bg"], bd=4, relief="groove", height=200, width=400)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_panel.grid_propagate(False) 

        # --- INFO LABELS ---
        self.lbl_commits = tk.Label(self.left_panel, text="Commits: 0", font=("Arial", 11), relief="groove", bd=1, padx=5, pady=5)
        self.lbl_commits.pack(fill="x", pady=5, padx=5)

        self.lbl_pushes = tk.Label(self.left_panel, text="Pushes: 0", font=("Arial", 11), relief="groove", bd=1, padx=5, pady=5)
        self.lbl_pushes.pack(fill="x", pady=5, padx=5)

        self.lbl_project_start = tk.Label(self.left_panel, text="Inicio del proyecto: -", font=("Arial", 11), relief="groove", bd=1, padx=5, pady=5)
        self.lbl_project_start.pack(fill="x", pady=5, padx=5)

        self.lbl_total_time = tk.Label(self.left_panel, text="Tiempo total: 0:00:00", font=("Arial", 11), relief="groove", bd=1, padx=5, pady=5)
        self.lbl_total_time.pack(fill="x", pady=5, padx=5)

        self.lbl_days_passed = tk.Label(self.left_panel, text="Días: 0", font=("Arial", 11), relief="groove", bd=1, padx=5, pady=5)
        self.lbl_days_passed.pack(fill="x", pady=5, padx=5)

        # Spacer inferior
        spacer = tk.Frame(self.left_panel, height=10, bg=t["bg"])
        spacer.pack(side="bottom")

        # --- TREEVIEW (derecha) ---
        self.tree = ttk.Treeview(self.main_container, columns=("SHA", "Commit Date", "Time", "Message"),
                                show="headings", height=15)
        for col in ("SHA", "Commit Date", "Time", "Message"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col != "Message" else 400)
        self.tree.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Configurar grid del main_container para que los paneles ocupen proporciones 2/3 y 1/3
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=2)
        self.main_container.grid_columnconfigure(1, weight=1)

        # --- Ajustar ancho proporcional al tamaño de la ventana ---
        def ajustar_main_container(event):
            new_width = int(event.width * 0.7)  # 70% del ancho ventana
            new_height = int(event.height * 0.6)  # 60% del alto ventana
            self.main_container.config(width=new_width, height=new_height)
            self.left_panel.config(height=new_height)  # sincronizar alto del panel izquierdo

        self.bind("<Configure>", ajustar_main_container)

        # --- Label repositorio y combobox en top bar ---
        self.title_label = tk.Label(self.top_bar, text="Repositorio:", bg=t["bg"], fg=t["fg"])
        self.title_label.pack(side="left", padx=5)

        repositorios = obtener_repositorios()
        self.repo_choices = list(repositorios.values())
        self.selected_repo = tk.StringVar(value=self.repo_choices[0])

        self.repo_menu = ttk.Combobox(
            self.top_bar,
            textvariable=self.selected_repo,
            values=self.repo_choices,
            state="readonly",
            width=60,
            style="Custom.TCombobox"
        )
        self.repo_menu.pack(side="left", padx=10)

        # --- ICON BUTTONS ---
        buttons = [
            (self.icon_push, self.hacer_push),
            (self.icon_refresh, self.actualizar_commits),
            (self.icon_folder, self.actualizar_commits),
        ]
        for icon, cmd in buttons:
            btn = tk.Button(
                self.top_bar,
                image=icon,
                command=cmd,
                bg=t["bg"],
                activebackground=t["button_active"],
                bd=1,
                relief="raised"
            )
            btn.pack(side="right", padx=5)
            if cmd == self.hacer_push:
                self.btn_push = btn
            elif cmd == self.actualizar_commits and icon == self.icon_refresh:
                self.btn_update = btn
            else:
                self.btn_select = btn

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

        # --- parse de fechas y mensajes ---
        parsed_commits = []
        for c in commits:
            date = c.get("commit_date") or c.get("date") or datetime.now()
            msg = c.get("message") or c.get("commit_message") or ""
            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date.replace("Z", "+00:00"))
                except:
                    date = datetime.now()
            parsed_commits.append({"date": date, "message": msg})

        fecha_primera = min([p["date"] for p in parsed_commits])
        # buscar commit con [END]
        commit_end = next((p for p in reversed(parsed_commits) if "[END]" in p["message"]), None)
        if commit_end:
            fecha_fin = commit_end["date"]
            proyecto_finalizado = True
        else:
            fecha_fin = datetime.now()
            proyecto_finalizado = False

        dias_pasados = max(0, (fecha_fin.date() - fecha_primera.date()).days)

        self.lbl_project_start.config(text=f"Inicio del proyecto: {fecha_primera.date()}")
        if proyecto_finalizado:
            self.lbl_days_passed.config(text=f"Días transcurridos: {dias_pasados} (final: {fecha_fin.date()})")
            self.btn_push.config(state="disabled")
            self.btn_update.config(state="disabled")
        else:
            self.lbl_days_passed.config(text=f"Días transcurridos: {dias_pasados}")
            self.btn_push.config(state="normal")
            self.btn_update.config(state="normal")

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

        # botones
        buttons = [self.btn_select, self.btn_update, self.btn_push]
        for btn in buttons:
            btn.config(bg=t["button_bg"], fg=t["fg"], activebackground=t["button_active"], activeforeground=t["fg"])

        # combobox
        style = ttk.Style()
        style.theme_use("default")
        combo_bg = "#3b3b3b" if self.controller.theme == "dark" else "white"
        combo_fg = t["fg"]
        combo_select_bg = t["button_active"]
        style.configure("Custom.TCombobox",
                        fieldbackground=combo_bg,
                        background=t["button_bg"],
                        foreground=combo_fg,
                        arrowcolor=combo_fg)
        style.map('Custom.TCombobox',
                  fieldbackground=[('readonly', combo_bg)],
                  selectbackground=[('readonly', combo_bg)],
                  selectforeground=[('readonly', combo_fg)])
        self.controller.option_add('*TCombobox*Listbox.background', combo_bg)
        self.controller.option_add('*TCombobox*Listbox.foreground', combo_fg)
        self.controller.option_add('*TCombobox*Listbox.selectBackground', combo_select_bg)
        self.controller.option_add('*TCombobox*Listbox.selectForeground', combo_fg)

        # treeview
        tree_bg = "#2d2d2d" if self.controller.theme == "dark" else "white"
        style.configure("Treeview", background=tree_bg, foreground=t["fg"], fieldbackground=tree_bg)
        style.configure("Treeview.Heading", background=t["button_bg"], foreground=t["fg"])
        style.map("Treeview", background=[('selected', t["button_active"])], foreground=[('selected', t["fg"])])
