import os
from flask import Flask, render_template, request
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

    # Detectar proyecto finalizado
    commit_end = next(
        (c for c in reversed(commits) if "[END]" in c.get('message', '')),
        None
    )
    project_finalizado = commit_end is not None

    # Detectar fechas
    fechas = []
    for c in commits:
        try:
            cd = c.get('commit_date')
            if cd:
                fechas.append(datetime.fromisoformat(cd.replace("Z", "+00:00")))
        except:
            continue

    project_start = min(fechas) if fechas else None
    fecha_fin = datetime.fromisoformat(commit_end['commit_date'].replace("Z", "+00:00")) if commit_end else datetime.now()

    days_passed = (
        max(0, (fecha_fin.date() - project_start.date()).days)
        if project_start else 0
    )

    # ------------------------------
    #        DURACIÓN DE TAREAS
    # ------------------------------
    tareas = calcular_duracion_tareas(commits)

    total_duration = timedelta()
    for info in tareas.values():
        total_duration += info["duracion"]

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

    try:
        repos_dict = obtener_repositorios() or {}
        repo_choices = list(repos_dict.values())
        selected_repo = repo_choices[0] if repo_choices else None

        if request.method == "POST":
            selected_repo = request.form.get("repo") or selected_repo
            action = request.form.get("action")

            log_file = os.path.join(selected_repo, "push_log.txt") if selected_repo else None

            if selected_repo and action == "push":
                git_push_and_log(selected_repo, BRANCH, log_file)

        if selected_repo:
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
        total_duration=total_duration_str,   # TOTAL SUMADO
        tareas=tareas,                       # TAREAS INDIVIDUALES
        project_finalizado=project_finalizado,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)
