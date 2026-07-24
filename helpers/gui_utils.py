# =========== #
# 📦 IMPORTS #
# ========== #
import os
from datetime import datetime, timedelta

from git_utils.git_operations import (
    get_local_commits,
    git_push_and_log,
    get_push_dates_from_log
)

from helpers.time_utils import (
    map_task_duration,
    format_timedelta
)

from tkinter import messagebox

BRANCH = "main"

# ============================ #
# 📊 LOAD COMMITS + UPDATE UI #
# =========================== #
def cargar_commits(
    path,
    tree,
    lbl_commits,
    lbl_pushes,
    lbl_total_time
):
    """
    Carga commits en la tabla (Treeview) y actualiza métricas:
    - número de commits
    - número de pushes
    - tiempo total trabajado
    """

    # ------------------ #
    # 📥 CARGA DE DATOS #
    # ----------------- #
    log_file = os.path.join(path, "push_log.txt")

    commits = get_local_commits(path)
    push_dates = get_push_dates_from_log(log_file)
    task_map = map_task_duration(commits)

    # --------------------- #
    # 🧹 LIMPIEZA DE TABLA #
    # -------------------- #
    for row in tree.get_children():
        tree.delete(row)

    # ------------------------ #
    # 🔄 PROCESADO DE COMMITS #
    # ----------------------- #
    total_duration = timedelta()

    for c in commits:

        sha_short = c["sha"][:7]

        commit_dt = datetime.fromisoformat(
            c["commit_date"]
        ).replace(tzinfo=None)

        commit_str = commit_dt.strftime("%Y-%m-%d %H:%M:%S")

        duracion_tarea = ""

        # ⏱ DURACIÓN DE TAREA (si aplica)
        if sha_short in task_map:
            duracion = task_map[sha_short]["duracion"]
            duracion_tarea = format_timedelta(duracion)
            total_duration += duracion

        # 📋 INSERTAR EN TABLA
        tree.insert(
            "",
            "end",
            values=(
                sha_short,
                commit_str,
                duracion_tarea,
                c["message"]
            )
        )

    # ---------------------------------- #
    # 📊 ACTUALIZACIÓN DE MÉTRICAS (UI) #
    # --------------------------------- #
    lbl_commits.config(text=f"Commits: {len(commits)}")
    lbl_pushes.config(text=f"Pushes: {len(push_dates)}")
    lbl_total_time.config(
        text=f"Tiempo total trabajado: {format_timedelta(total_duration)}"
    )

    return commits


# ========================= #
# 🚀 GIT PUSH + REFRESH UI #
# ======================== #
def hacer_push(
    path,
    tree,
    lbl_commits,
    lbl_pushes,
    lbl_total_time
):
    """
    Ejecuta git push, muestra resultado y recarga la UI
    """

    # ---------------------- #
    # 📁 CONFIGURACIÓN PUSH #
    # --------------------- #
    log_file = os.path.join(path, "push_log.txt")

    # --------------------- #
    # 🚀 EJECUCIÓN DE PUSH #
    # -------------------- #
    push_result = git_push_and_log(
        path,
        BRANCH,
        log_file
    )

    # ----------------------- #
    # 💬 FEEDBACK AL USUARIO #
    # ---------------------- #
    if push_result:
        sha_push, push_time = push_result

        messagebox.showinfo(
            "Push",
            f"Push realizado: {sha_push} a las {push_time}"
        )
    else:
        messagebox.showinfo(
            "Push",
            "No había cambios para hacer push."
        )

    # -------------- #
    # 🔄 REFRESH UI #
    # ------------- #
    cargar_commits(
        path,
        tree,
        lbl_commits,
        lbl_pushes,
        lbl_total_time
    )