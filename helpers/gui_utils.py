import os                                   # Para manejar rutas de archivos y carpetas
from datetime import (                      # Para trabajar con fechas y duraciones
    datetime, 
    timedelta
)
from git_utils.git_operations import (      # Importa funciones que obtienen commits, hacen push y leen el log de pushes
    get_local_commits,
    git_push_and_log,
    get_push_dates_from_log
)
from helpers.time_utils import (            # Importa funciones que calculan duración de tareas y las formatean
    map_task_duration, 
    format_timedelta
)
from config.settings import BRANCH          # Importa la rama por defecto para push
from tkinter import messagebox              # Para mostrar alertas en ventanas

def cargar_commits(                                    # Carga commits en la tabla y actualiza panel superior
        path, 
        tree, 
        lbl_commits, 
        lbl_pushes, 
        lbl_total_time
):
    log_file = os.path.join(path, "push_log.txt")      # Ruta al archivo de log de pushes
    commits = get_local_commits(path)                  # Obtiene todos los commits locales del repo
    push_dates = get_push_dates_from_log(log_file)     # Obtiene las fechas de pushes desde el log
    task_map = map_task_duration(commits)              # Calcula duración de tareas a partir de commits

    # Limpiar tabla
    for row in tree.get_children():
        tree.delete(row)                               # Elimina todas las filas anteriores del Treeview

    total_duration = timedelta()                                                      # Inicializa duración total en cero
    for c in commits:                                                                 # Recorre cada commit
        sha_short = c['sha'][:7]                                                      # SHA corto para mostrar en la tabla
        commit_dt = datetime.fromisoformat(c['commit_date']).replace(tzinfo=None)     # Convierte la fecha ISO a datetime sin zona horaria
        commit_str = commit_dt.strftime("%Y-%m-%d %H:%M:%S")                          # Formatea fecha para mostrar
        duracion_tarea = ""                                                           # Inicializa duración de tarea vacía
        if sha_short in task_map:                                                     # Verifica si el commit se asocia a una tarea
            duracion_tarea = format_timedelta(task_map[sha_short]["duracion"])        # Obtiene su duración formateada
            total_duration += task_map[sha_short]["duracion"]                         # Suma a duración total
        tree.insert(                                                                  # Inserta fila en la tabla con SHA, fecha, duración y mensaje
            "", 
            "end", 
            values=(
                sha_short,
                commit_str, 
                duracion_tarea, 
                c['message']
            )
        )

    # Actualizar panel superior
    lbl_commits.config(text=f"Commits: {len(commits)}")                               # Actualiza número de commits
    lbl_pushes.config(text=f"Pushes: {len(push_dates)}")                              # Actualiza número de pushes
    lbl_total_time.config(text=f"Tiempo total trabajado: {str(total_duration)}")      # Actualiza tiempo total trabajado


def hacer_push(                                             # Hace push y refresca la tabla
        path, 
        tree, 
        lbl_commits, 
        lbl_pushes, 
        lbl_total_time
):
    log_file = os.path.join(                                # Ruta al log de pushes
        path, 
        "push_log.txt"
    )
    push_result = git_push_and_log(                         # Ejecuta git push y guarda SHA y timestamp en el log
        path, 
        BRANCH, 
        log_file
    )
    if push_result:
        sha_push, push_time = push_result
        messagebox.showinfo(
            "Push", 
            f"Push realizado: {sha_push} a las {push_time}" # Mensaje informando push exitoso
        )
    else:
        messagebox.showinfo(                                
            "Push", 
            "No había cambios para hacer push."             # Mensaje si no había nada que pushear
        )
    cargar_commits(                                         # Refresca la tabla y panel superior después del push
        path, 
        tree, 
        lbl_commits, 
        lbl_pushes, 
        lbl_total_time
    )
