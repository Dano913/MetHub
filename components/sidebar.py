# =========== #
# 📦 IMPORTS #
# ========== #
import tkinter as tk


# ================================= #
# 📄 COMPONENT: SIDEBAR NAVIGATION #
# ================================ #
class Sidebar(tk.Frame):

    # ================ #
    # 🚀 INIT / SETUP #
    # =============== #
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.build_ui()

    # =================== #
    # 🧱 UI CONSTRUCTION #
    # ================== #
    def build_ui(self):

        # ---------------------- #
        # 📂 NAVIGATION BUTTONS #
        # --------------------- #
        tk.Button(
            self,
            text="Tareas",
            command=lambda: self.controller.show_page("Tareas")
        ).pack(fill="x", pady=5, padx=10)

        tk.Button(
            self,
            text="Commits",
            command=lambda: self.controller.show_page("Commits")
        ).pack(fill="x", pady=5, padx=10)

        # ---------------- #
        # 🎨 THEME TOGGLE #
        # --------------- #
        tk.Button(
            self,
            text="🌙 / ☀️ Tema",
            command=self.controller.toggle_theme
        ).pack(fill="x", pady=5, padx=10)


    # ================ #
    # 🎨 THEME SYSTEM #
    # =============== #
    def apply_theme(self):

        theme = self.controller.themes[self.controller.theme]

        # fondo sidebar
        self.config(bg=theme["sidebar_bg"])

        # aplicar tema a botones
        for child in self.winfo_children():
            if isinstance(child, tk.Button):
                child.config(
                    bg=theme["button_bg"],
                    fg=theme["fg"],
                    activebackground=theme["button_active"],
                    activeforeground=theme["fg"]
                )