import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import platform

from pages.tareas_page import TareasPage
from pages.commits_page import CommitsPage
from components.sidebar import Sidebar


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # -------- CONFIG DE VENTANA --------
        self.WIDTH = 1600
        self.HEIGHT = 700
        self.RADIUS = 25
        self.TRANSPARENT = "#00FF00"

        self.overrideredirect(True)  # oculta barra nativa
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(800, 500)

        # Hacer transparente ese color
        self.config(bg=self.TRANSPARENT)
        self.attributes("-transparentcolor", self.TRANSPARENT)

        # CANVAS donde va el fondo redondeado
        self.canvas = tk.Canvas(
            self, width=self.WIDTH, height=self.HEIGHT,
            bg=self.TRANSPARENT, highlightthickness=0, bd=0
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # -------- TEMA --------
        self.theme = "dark"
        self.themes = {
            "dark": {
                "bg": "#1e1e1e",
                "sidebar_bg": "#252526",
                "button_bg": "#333333",
                "button_active": "#007ACC",
                "fg": "white",
            },
            "light": {
                "bg": "#f3f3f3",
                "sidebar_bg": "#dcdcdc",
                "button_bg": "#c6c6c6",
                "button_active": "#0e70c0",
                "fg": "black",
            },
        }

        # Pintar fondo redondeado según el tema
        self.draw_rounded_background()

        # -------- BARRA SUPERIOR PERSONALIZADA --------
        self.create_top_bar()

        # -------- CONTENEDOR PRINCIPAL --------
        container = tk.Frame(self, bg=self.themes[self.theme]["bg"])
        container.place(x=0, y=40, relwidth=1, relheight=1)

        # Sidebar
        self.sidebar = Sidebar(container, self)
        self.sidebar.pack(side="left", fill="y")

        # Contenedor páginas
        self.page_container = tk.Frame(container, bg=self.themes[self.theme]["bg"])
        self.page_container.pack(side="right", fill="both", expand=True)
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        # Páginas
        self.frames = {
            "Tareas": TareasPage(self.page_container, self),
            "Commits": CommitsPage(self.page_container, self)
        }
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.apply_theme()
        self.show_page("Tareas")

        # Estado maximizado
        self._is_maximized = False

        # Restaurar ventana al volver de minimizar
        self.bind("<Map>", self.restore_after_minimize)
        
        # Aplicar ventana redondeada después de que todo esté listo
        self.after(200, self.apply_rounded_window)

    # -----------------------------------------------------
    #      FONDO REDONDEADO
    # -----------------------------------------------------
    def draw_rounded_background(self):
        t = self.themes[self.theme]

        img = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle(
            (0, 0, self.WIDTH, self.HEIGHT),
            radius=self.RADIUS,
            fill=t["bg"]
        )

        self.round_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.round_img)

    # -----------------------------------------------------
    #      BARRA SUPERIOR CUSTOM
    # -----------------------------------------------------
    def create_top_bar(self):
        t = self.themes[self.theme]

        # Barra superior con relwidth para que se ajuste automáticamente
        self.top_bar = tk.Frame(self, bg=t["bg"], height=40)
        self.top_bar.place(x=0, y=0, relwidth=1, height=40)

        # Título a la izquierda
        self.title_label = tk.Label(
            self.top_bar, text="MetHub",
            bg=t["bg"], fg=t["fg"], font=("Arial", 12)
        )
        self.title_label.pack(side="left", padx=10)

        # Botón cerrar
        self.btn_close = tk.Button(
            self.top_bar, text="✕", command=self.destroy,
            bg=t["bg"], fg=t["fg"], bd=0,
            padx=8, activebackground="red"
        )
        self.btn_close.pack(side="right", padx=5)

        # Botón maximizar
        self.btn_max = tk.Button(
            self.top_bar, text="⬜", command=self.toggle_maximize,
            bg=t["bg"], fg=t["fg"], bd=0,
            padx=8, activebackground=t["button_bg"]
        )
        self.btn_max.pack(side="right")

        # Botón minimizar
        self.btn_min = tk.Button(
            self.top_bar, text="—", command=self.minimize,
            bg=t["bg"], fg=t["fg"], bd=0,
            padx=8, activebackground=t["button_bg"]
        )
        self.btn_min.pack(side="right")

        # Hacer la barra arrastrable
        self.top_bar.bind("<Button-1>", self.start_move)
        self.top_bar.bind("<B1-Motion>", self.do_move)

    # -----------------------------------------------------
    #      MOVILIDAD
    # -----------------------------------------------------
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.geometry(f"+{x}+{y}")

    # -----------------------------------------------------
    #      MINIMIZAR / RESTAURAR
    # -----------------------------------------------------
    def minimize(self):
        self.overrideredirect(False)
        self.iconify()

    def restore_after_minimize(self, event=None):
        self.overrideredirect(True)

    # -----------------------------------------------------
    #      MAXIMIZAR
    # -----------------------------------------------------
    def toggle_maximize(self):
        if self._is_maximized:
            self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
            self._is_maximized = False
            # Reaplica la máscara redondeada después de restaurar
            self.after(100, self.apply_rounded_window)
        else:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
            self._is_maximized = True
            # No aplicar esquinas redondeadas cuando está maximizado
            try:
                import win32gui
                hwnd = int(self.frame(), 16) if isinstance(self.frame(), str) else self.winfo_id()
                # Remover la región (ventana rectangular completa)
                win32gui.SetWindowRgn(hwnd, None, True)
            except:
                pass

    # -----------------------------------------------------
    #      VENTANA REDONDEADA
    # -----------------------------------------------------
    def apply_rounded_window(self):
        """Aplica una máscara redondeada a toda la ventana"""
        # Solo funciona en Windows
        if platform.system() != "Windows":
            print("Ventanas redondeadas solo disponibles en Windows")
            return
        
        try:
            import win32gui
            import win32con
            
            # Forzar actualización de la ventana
            self.update_idletasks()
            
            # Obtener el handle de la ventana
            hwnd = int(self.frame(), 16) if isinstance(self.frame(), str) else self.winfo_id()
            
            # Obtener dimensiones actuales
            width = self.winfo_width()
            height = self.winfo_height()
            
            print(f"Aplicando ventana redondeada: {width}x{height}, radio={self.RADIUS}")
            
            # Crear región redondeada (duplicamos el radio para hacerlo más pronunciado)
            region = win32gui.CreateRoundRectRgn(
                0, 0, 
                width + 1, height + 1,  # +1 para incluir el borde derecho/inferior
                self.RADIUS * 2, self.RADIUS * 2
            )
            
            # Aplicar la región a la ventana
            result = win32gui.SetWindowRgn(hwnd, region, True)
            print(f"Resultado de SetWindowRgn: {result}")
            
            # Forzar redibujado
            self.update()
            
        except ImportError as e:
            print(f"pywin32 no está instalado correctamente: {e}")
            print("Instala con: pip install pywin32")
        except Exception as e:
            print(f"Error al aplicar ventana redondeada: {e}")
            import traceback
            traceback.print_exc()

    # -----------------------------------------------------
    #      PÁGINAS
    # -----------------------------------------------------
    def show_page(self, name):
        self.frames[name].tkraise()

    # -----------------------------------------------------
    #      TEMA
    # -----------------------------------------------------
    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.draw_rounded_background()
        self.apply_rounded_window()  # Reaplicar máscara después de cambiar tema

    def apply_theme(self):
        t = self.themes[self.theme]

        self.top_bar.config(bg=t["bg"])
        self.title_label.config(bg=t["bg"], fg=t["fg"])
        self.btn_close.config(bg=t["bg"], fg=t["fg"])
        self.btn_min.config(bg=t["bg"], fg=t["fg"])
        self.btn_max.config(bg=t["bg"], fg=t["fg"])

        self.sidebar.apply_theme()
        for frame in self.frames.values():
            if hasattr(frame, "apply_theme"):
                frame.apply_theme()


if __name__ == "__main__":
    app = App()
    app.mainloop()