import os                                                  #Módulo para manejar rutas y archivos
import tkinter as tk                                       #Módulo para la interfaz gráfica
from tkinter import ttk, messagebox                        #Submódulos de tkinter
from config.repo_selector import obtener_repositorios      #Importa la función obtener_repositorios
from helpers.gui_utils import cargar_commits, hacer_push   #Importa las funciones que cargan los comits y hacen el push

#-Ventana principal-
root = tk.Tk()                  #Crea la ventana principal de la App
root.title("Git Repo Manager")  #Establece el título de la ventana
root.geometry("1000x700")       #Define el tamaño inical de la ventana en píxeles

#-Variables-
selected_repo = tk.StringVar()  #Variable que contiene el repo seleccionado

#-Repositorios detectados-
repositorios = obtener_repositorios() #Llama a la funcion para detectar todos los repositorios disponibles
if not repositorios:
    messagebox.showerror("Error", "No se detectaron repositorios.")
    root.destroy()

repo_choices = list(repositorios.values())    #Convierte el diccionario de repositorios en una lista con las rutas
selected_repo.set(repo_choices[0])            #Define el repositorio por defecto en el Combobox

#-Selector de repositorio-
tk.Label(                                #Widget estático para mostrar el placeholder del selector
    root, 
    text="Selecciona repositorio:"
).pack(pady=5)
repo_menu = ttk.Combobox(                #Widget interactivo que permite al usuario seleccionar un valor de la lista
    root, 
    textvariable=selected_repo, 
    values=repo_choices, 
    state="readonly", 
    width=80
)
repo_menu.pack(pady=5)

# --- Panel superior ---
info_frame = tk.Frame(root)                    #Contenedor para organizar widgets horizontalmente          
info_frame.pack(fill="x", pady=10)             #El frame ocupa toda la ventana
lbl_commits = tk.Label(                        #Etiqueta que mostrará numero de commits
    info_frame, 
    text="Commits: 0", 
    font=("Arial", 12)
)
lbl_commits.pack(side="left", padx=10)         #Coloca elementos horizontalmente
lbl_pushes = tk.Label(                         #Etiqueta que mostrará numero de pushes
    info_frame, 
    text="Pushes: 0", 
    font=("Arial", 12)
)
lbl_pushes.pack(side="left", padx=10)          #Coloca elementos horizontalmente
lbl_total_time = tk.Label(                     #Etiqueta que mostrará tiempo total trabajado
    info_frame, 
    text="Tiempo total trabajado: 0:00:00", 
    font=("Arial", 12)
)
lbl_total_time.pack(side="left", padx=10)       #Coloca elementos horizontalmente

# --- Tabla de commits ---
columns = (               #Define las columnas de la tabla
    "SHA", 
    "Commit Date", 
    "Time", 
    "Message"
)
tree = ttk.Treeview(      #Tabla donde se mostrarán los commits
    root, 
    columns=columns, 
    show="headings"
)
for col in columns:
    tree.heading(          #Coloca el título de cada columna
        col, 
        text=col
    )
    tree.column(           #Define el ancho de columna
        col, 
        width=200 if col != "Message" else 400
    )
tree.pack(                 #Define que la tabla ocupe el resto de la ventana
    fill="both", 
    expand=True, 
    pady=10
)

# --- Botones ---
tk.Button(   #Se encarga de seleccionar el repo, carga los commits y actualiza métricas
    root, 
    text="Seleccionar repositorio", 
    command=lambda: cargar_commits(
        selected_repo.get(), 
        tree, 
        lbl_commits, 
        lbl_pushes, 
        lbl_total_time)
    ).pack(pady=5)
tk.Button(   #Se encarga de actualizar la tabla de commits  de ese repo
    root, 
    text="Actualizar commits", 
    command=lambda: cargar_commits(
        selected_repo.get(), 
        tree, 
        lbl_commits, 
        lbl_pushes, 
        lbl_total_time)
    ).pack(pady=5)
tk.Button(   #Se encarga de ejecutar el push en el repo actual y refresca la tabla y las métricas
    root, 
    text="Hacer push", 
    command=lambda: hacer_push(
        selected_repo.get(), 
        tree, 
        lbl_commits, 
        lbl_pushes, 
        lbl_total_time)
    ).pack(pady=5)
root.mainloop()   #Lanza la ventana y mantiene el bucle de eventos de Tkinter, esperando interacciones de usuario                 
