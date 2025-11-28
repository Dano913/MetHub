import tkinter as tk

class Sidebar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Button(
            self,
            text="Tareas",
            command=lambda: controller.show_page("Tareas")
        ).pack(fill="x", pady=5, padx=10)

        tk.Button(
            self,
            text="Commits",
            command=lambda: controller.show_page("Commits")
        ).pack(fill="x", pady=5, padx=10)

        tk.Button(
            self,
            text="🌙 / ☀️ Tema",
            command=controller.toggle_theme
        ).pack(fill="x", pady=5, padx=10)

    def apply_theme(self):
        t = self.controller.themes[self.controller.theme]
        self.config(bg=t["sidebar_bg"])

        for child in self.winfo_children():
            if isinstance(child, tk.Button):
                child.config(
                    bg=t["button_bg"],
                    fg=t["fg"],
                    activebackground=t["button_active"],
                    activeforeground=t["fg"]
                )
