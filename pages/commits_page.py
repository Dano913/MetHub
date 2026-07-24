# =========== #
# 📦 IMPORTS #
# ========== #
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

from config.repo_selector import obtener_repositorios
from helpers.gui_utils import cargar_commits, hacer_push


# ====================== #
# 📄 VIEW: COMMITS PAGE #
# ===================== #
class CommitsPage(tk.Frame):

    # ================ #
    # 🚀 INIT / SETUP #
    # =============== #
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.build_ui()
        self.apply_theme()


    # =================== #
    # 🧱 UI CONSTRUCTION #
    # ================== #
    def build_ui(self):

        t = self.controller.themes[self.controller.theme]

        # ----------- #
        # 🔝 TOP BAR #
        # ---------- #
        self.top_bar = tk.Frame(self, height=50, bg=t["bg"], bd=1, relief="raised")
        self.top_bar.pack(fill="x", pady=5, padx=5)

        # 🎯 ICONOS
        self.icon_refresh = tk.PhotoImage(file="icons/refresh.png")
        self.icon_folder = tk.PhotoImage(file="icons/folder.png")
        self.icon_push = tk.PhotoImage(file="icons/push.png")

        # ------------------ #
        # 📦 MAIN CONTAINER #
        # ----------------- #
        self.main_container = tk.Frame(
            self,
            bg=t["bg"],
            bd=2,
            relief="solid",
            width=700,
            height=300
        )
        self.main_container.pack(padx=10, pady=10)
        self.main_container.pack_propagate(False)

        # layout grid
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=2)
        self.main_container.grid_columnconfigure(1, weight=1)

        # ---------------------- #
        # 📊 LEFT PANEL (STATS) #
        # --------------------- #
        self.left_panel = tk.Frame(
            self.main_container,
            bg=t["bg"],
            bd=4,
            relief="groove",
            width=400
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_panel.grid_propagate(False)

        # 📌 LABELS INFO
        self.lbl_commits = tk.Label(self.left_panel, text="Commits: 0")
        self.lbl_pushes = tk.Label(self.left_panel, text="Pushes: 0")
        self.lbl_project_start = tk.Label(self.left_panel, text="Inicio del proyecto: -")
        self.lbl_total_time = tk.Label(self.left_panel, text="Tiempo total: 0:00:00")
        self.lbl_days_passed = tk.Label(self.left_panel, text="Días: 0")

        for lbl in [
            self.lbl_commits,
            self.lbl_pushes,
            self.lbl_project_start,
            self.lbl_total_time,
            self.lbl_days_passed
        ]:
            lbl.pack(fill="x", pady=5, padx=5)

        # ---------------------------- #
        # 📋 TREEVIEW (COMMITS TABLE) #
        # --------------------------- #
        self.tree = ttk.Treeview(
            self.main_container,
            columns=("SHA", "Commit Date", "Time", "Message"),
            show="headings"
        )

        for col in ("SHA", "Commit Date", "Time", "Message"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col != "Message" else 400)

        self.tree.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # --------------------- #
        # 📐 RESPONSIVE RESIZE #
        # -------------------- #
        def ajustar_main_container(event):
            self.main_container.config(
                width=int(event.width * 0.7),
                height=int(event.height * 0.6)
            )

        self.bind("<Configure>", ajustar_main_container)

        # --------------------------- #
        # 📁 SELECTOR DE REPOSITORIO #
        # -------------------------- #
        self.title_label = tk.Label(self.top_bar, text="Repositorio:", bg=t["bg"])
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

        # ------------------ #
        # 🔘 ACTION BUTTONS #
        # ----------------- #
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
                bg=t["bg"]
            )
            btn.pack(side="right", padx=5)

            if cmd == self.hacer_push:
                self.btn_push = btn
            elif cmd == self.actualizar_commits and icon == self.icon_refresh:
                self.btn_update = btn
            else:
                self.btn_select = btn


    # ======================== #
    # 🧠 LOGIC (DATA + STATE) #
    # ======================= #

    # 🔄 REFRESH COMMITS
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

        # ------------------- #
        # 📊 PARSEO DE DATOS #
        # ------------------ #
        parsed = []

        for c in commits:
            date = c.get("commit_date") or datetime.now()
            msg = c.get("message") or ""

            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date.replace("Z", "+00:00"))
                except:
                    date = datetime.now()

            parsed.append({"date": date, "message": msg})

        # ------------------------- #
        # 📈 MÉTRICAS DEL PROYECTO #
        # ------------------------ #
        fecha_inicio = min(p["date"] for p in parsed)

        commit_end = next(
            (p for p in reversed(parsed) if "[END]" in p["message"]),
            None
        )

        if commit_end:
            fecha_fin = commit_end["date"]
            finalizado = True
        else:
            fecha_fin = datetime.now()
            finalizado = False

        dias = max(0, (fecha_fin.date() - fecha_inicio.date()).days)

        # ------------------- #
        # 🖥 ACTUALIZACIÓN UI #
        # ------------------ #
        self.lbl_project_start.config(
            text=f"Inicio del proyecto: {fecha_inicio.date()}"
        )

        if finalizado:
            self.lbl_days_passed.config(
                text=f"Días: {dias} (final: {fecha_fin.date()})"
            )
            self.btn_push.config(state="disabled")
            self.btn_update.config(state="disabled")
        else:
            self.lbl_days_passed.config(text=f"Días: {dias}")
            self.btn_push.config(state="normal")
            self.btn_update.config(state="normal")


    # 🚀 PUSH
    def hacer_push(self):
        hacer_push(
            self.selected_repo.get(),
            self.tree,
            self.lbl_commits,
            self.lbl_pushes,
            self.lbl_total_time
        )


    # ================ #
    # 🎨 THEME SYSTEM #
    # =============== #
    def apply_theme(self):

        t = self.controller.themes[self.controller.theme]

        self.config(bg=t["bg"])
        self.top_bar.config(bg=t["bg"])

        # labels
        for lbl in [
            self.title_label,
            self.lbl_commits,
            self.lbl_pushes,
            self.lbl_total_time,
            self.lbl_project_start,
            self.lbl_days_passed
        ]:
            lbl.config(bg=t["bg"], fg=t["fg"])

        # botones
        for btn in [self.btn_select, self.btn_update, self.btn_push]:
            btn.config(
                bg=t["button_bg"],
                fg=t["fg"],
                activebackground=t["button_active"]
            )

        # combobox + treeview styles
        style = ttk.Style()
        style.theme_use("default")

        tree_bg = "#2d2d2d" if self.controller.theme == "dark" else "white"

        style.configure(
            "Treeview",
            background=tree_bg,
            foreground=t["fg"],
            fieldbackground=tree_bg
        )