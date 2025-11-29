import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

from config.repo_selector import obtener_repositorios
from git_utils.git_operations import get_local_commits, git_push_and_log, get_push_dates_from_log
from helpers.time_utils import calcular_duracion_tareas, format_timedelta
from config.settings import BRANCH

app = Flask(__name__)


def calcular_datos_repo(selected_repo):
    """Obtiene commits, pushes, duración total y datos de proyecto."""
    commits = get_local_commits(selected_repo) or []
    log_file = os.path.join(selected_repo, "push_log.txt")
    push_dates = get_push_dates_from_log(log_file) or {}

    # ------------------------------
    #     DETECTAR FIN DE PROYECTO
    # ------------------------------
    commit_end = next(
        (c for c in reversed(commits) if "[END]" in c.get('message', '')),
        None
    )
    project_finalizado = commit_end is not None

    # ------------------------------
    #        FECHAS DEL PROYECTO
    # ------------------------------
    fechas = []
    for c in commits:
        try:
            commit_date_str = c.get('commit_date')
            if commit_date_str:
                fechas.append(datetime.fromisoformat(commit_date_str.replace("Z", "+00:00")))
        except Exception:
            continue

    project_start = min(fechas) if fechas else None
    fecha_fin = (
        datetime.fromisoformat(commit_end['commit_date'].replace("Z", "+00:00"))
        if commit_end else datetime.now()
    )
    days_passed = (
        max(0, (fecha_fin.date() - project_start.date()).days)
        if project_start else 0
    )

    # ------------------------------
    #     DURACIÓN DE TAREAS (+ / -)
    # ------------------------------
    tareas = calcular_duracion_tareas(commits)

    # Suma de duraciones
    total_duration = timedelta()
    for t in tareas.values():
        total_duration += t["duracion"]

    total_duration_str = format_timedelta(total_duration)

    return (
        commits,
        push_dates,
        project_start,
        days_passed,
        total_duration_str,
        tareas,
        project_finalizado
    )


@app.route("/", methods=["GET", "POST"])
def index():
    error_message = None
    selected_repo = None
    commits = []
    push_dates = {}
    project_start = None
    days_passed = 0
    total_duration_str = "0:00"
    tareas = {}
    project_finalizado = False
    repo_choices = []

    # -------------------------------------
    #     Obtener repositorios disponibles
    # -------------------------------------
    repos_dict = obtener_repositorios() or {}
    repo_choices = list(repos_dict.values())
    selected_repo = request.form.get("repo") or repo_choices[0] if repo_choices else None

    # -------------------------------------
    #               POST
    # -------------------------------------
    if request.method == "POST":
        action = request.form.get("action")
        log_file = os.path.join(selected_repo, "push_log.txt") if selected_repo else None

        if selected_repo and action == "push":
            try:
                git_push_and_log(selected_repo, BRANCH, log_file)
            except Exception as e:
                error_message = str(e)
            # Después del push, hacemos redirect para evitar la advertencia del navegador
            return redirect(url_for('index'))

    # -------------------------------------
    #     GET: Cargar datos del repo elegido
    # -------------------------------------
    if selected_repo:
        try:
            (
                commits,
                push_dates,
                project_start,
                days_passed,
                total_duration_str,
                tareas,
                project_finalizado
            ) = calcular_datos_repo(selected_repo)
        except Exception as e:
            error_message = str(e)

    return render_template(
        "index.html",
        repo_choices=repo_choices,
        selected_repo=selected_repo,
        commits=commits,
        push_dates=push_dates,
        project_start=project_start,
        days_passed=days_passed,
        total_duration=total_duration_str,
        tareas=tareas,
        project_finalizado=project_finalizado,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)
