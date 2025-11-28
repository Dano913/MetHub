import tkinter as tk

class TareasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.tareas = []

        self.build_ui()
        self.apply_theme()  # aplica el tema inicial

    def build_ui(self):
        self.title_label = tk.Label(self, text="Tareas", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=15)

        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=10)

        self.task_entry = tk.Entry(entry_frame, width=40)
        self.task_entry.pack(side="left", padx=5)

        self.add_btn = tk.Button(entry_frame, text="Añadir", command=self.add_task)
        self.add_btn.pack(side="left", padx=5)

        self.tasks_frame = tk.Frame(self)
        self.tasks_frame.pack(pady=15, fill="x")

    # -----------------------------
    #           LÓGICA
    # -----------------------------
    def add_task(self):
        tarea = self.task_entry.get().strip()
        if tarea:
            self.tareas.append({"text": tarea, "done": False})
            self.task_entry.delete(0, tk.END)
            self.render_tasks()

    def toggle_task(self, index):
        self.tareas[index]["done"] = not self.tareas[index]["done"]
        self.render_tasks()

    def delete_task(self, index):
        del self.tareas[index]
        self.render_tasks()

    def render_tasks(self):
        for w in self.tasks_frame.winfo_children():
            w.destroy()

        t = self.controller.themes[self.controller.theme]

        for i, tarea in enumerate(self.tareas):
            row = tk.Frame(self.tasks_frame, bg=t["bg"])
            row.pack(fill="x", pady=3)

            texto = f"✔ {tarea['text']}" if tarea["done"] else tarea["text"]

            tk.Button(
                row,
                text=texto,
                command=lambda i=i: self.toggle_task(i),
                bg=t["button_bg"],
                fg=t["fg"],
                activebackground=t["button_active"],
                relief="flat",
                anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=5)

            tk.Button(
                row,
                text="🗑",
                command=lambda i=i: self.delete_task(i),
                bg=t["button_bg"],
                fg=t["fg"],
                activebackground="red",
                width=3,
                relief="flat"
            ).pack(side="right", padx=5)

    # -----------------------------
    #      CAMBIO DE TEMA
    # -----------------------------
    def apply_theme(self):
        t = self.controller.themes[self.controller.theme]

        self.config(bg=t["bg"])
        self.title_label.config(bg=t["bg"], fg=t["fg"])

        # entry frame + botones
        for w in self.winfo_children():
            if isinstance(w, tk.Frame):
                try:
                    w.config(bg=t["bg"])
                except:
                    pass

        self.task_entry.config(bg="white" if self.controller.theme == "light" else "#252526",
                               fg=t["fg"])

        self.add_btn.config(
            bg=t["button_bg"], fg=t["fg"],
            activebackground=t["button_active"]
        )

        self.render_tasks()
