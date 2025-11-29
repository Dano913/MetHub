import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import logging

from config.repo_selector import obtener_repositorios
from git_utils.git_operations import get_local_commits, git_push_and_log, get_push_dates_from_log
from config.settings import BRANCH

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def format_timedelta(td: timedelta) -> str:
    """Convierte timedelta a string HH:MM:SS o MM:SS si es menor a 1h."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"

def calcular_datos_repo(selected_repo):
    """Obtiene commits, pushes, duración total y datos de proyecto."""
    commits = get_local_commits(selected_repo) or []
    log_file = os.path.join(selected_repo, "push_log.txt")
    push_dates = get_push_dates_from_log(log_file) or {}

    # Convertir fechas a datetime
    for c in commits:
        commit_date_str = c.get('commit_date')
        try:
            c['_dt'] = datetime.fromisoformat(commit_date_str)
        except Exception:
            c['_dt'] = None

    # Ordenar commits por fecha ascendente
    commits_sorted = sorted([c for c in commits if c['_dt']], key=lambda x: x['_dt'])

    # Detectar fin de proyecto
    commit_end = next((c for c in reversed(commits) if "[END]" in c.get('message', '')), None)
    project_finalizado = commit_end is not None

    # Fechas del proyecto
    fechas = [c['_dt'] for c in commits if c['_dt']]
    project_start_dt = min(fechas) if fechas else None

    # Formatear fecha de inicio con hora
    if project_start_dt:
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        dia = project_start_dt.day
        mes = meses[project_start_dt.month - 1]
        anio = project_start_dt.year
        hora = project_start_dt.strftime("%H:%M")
        project_start_formateado = f"{dia} de {mes} de {anio} a las {hora}"
    else:
        project_start_formateado = ""

    fecha_fin = datetime.fromisoformat(commit_end['commit_date']) if commit_end else datetime.now()
    days_passed = (max(0, (fecha_fin.date() - project_start_dt.date()).days) if project_start_dt else 0)

    # Preparar tabla combined con duraciones correctas
    combined = []
    last_plus_commit = None
    for c in commits_sorted:
        sha = c.get('sha', '')[:7]
        message = c.get('message', '')
        commit_datetime = c.get('_dt')
        duracion_str = ''

        if message.startswith("+") and commit_datetime:
            last_plus_commit = c
        elif message.startswith("-") and commit_datetime and last_plus_commit:
            duracion_td = commit_datetime - last_plus_commit['_dt']
            if duracion_td.total_seconds() < 0:
                duracion_td = timedelta(0)
            duracion_str = format_timedelta(duracion_td)
            logging.info(f"TAREA DETECTADA: {message}, DURACIÓN: {duracion_str}")
            last_plus_commit = None

        # Formatear fecha y hora del commit
        if commit_datetime:
            meses = [
                "ene", "feb", "mar", "abr", "may", "jun",
                "jul", "ago", "sep", "oct", "nov", "dic"
            ]
            dia = commit_datetime.day
            mes = meses[commit_datetime.month - 1]
            anio = commit_datetime.year
            fecha_formateada = f"{dia} de {mes} {anio}"
            hora_formateada = commit_datetime.strftime("%H:%M")
        else:
            fecha_formateada = ""
            hora_formateada = ""

        combined.append({
            "sha": sha,
            "message": message,
            "date": fecha_formateada,
            "time": hora_formateada,
            "duration": duracion_str if message.startswith("-") else ''
        })

    # Duración total de todas las tareas
    total_duration = sum(
        (
            timedelta(
                hours=int(d.split(":")[0]),
                minutes=int(d.split(":")[1]),
                seconds=int(d.split(":")[2])
            ) if len(d.split(":")) == 3 else timedelta(
                minutes=int(d.split(":")[0]),
                seconds=int(d.split(":")[1])
            )
            for d in [row['duration'] for row in combined if row['duration']]
        ),
        timedelta()
    )
    total_duration_str = format_timedelta(total_duration)

    return commits, push_dates, project_start_formateado, days_passed, total_duration_str, project_finalizado, combined


@app.route("/", methods=["GET", "POST"])
def index():
    error_message = None
    selected_repo = None
    commits = []
    push_dates = {}
    project_start = None
    days_passed = 0
    total_duration_str = "0:00"
    project_finalizado = False
    combined = []
    repo_choices = []

    # Obtener repositorios disponibles
    repos_dict = obtener_repositorios() or {}
    repo_choices = list(repos_dict.values())
    selected_repo = request.form.get("repo") or repo_choices[0] if repo_choices else None

    if request.method == "POST":
        action = request.form.get("action")
        log_file = os.path.join(selected_repo, "push_log.txt") if selected_repo else None

        if selected_repo and action == "push":
            try:
                git_push_and_log(selected_repo, BRANCH, log_file)
            except Exception as e:
                error_message = str(e)
            return redirect(url_for('index'))

    if selected_repo:
        try:
            (commits,
             push_dates,
             project_start,
             days_passed,
             total_duration_str,
             project_finalizado,
             combined) = calcular_datos_repo(selected_repo)
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
        project_finalizado=project_finalizado,
        combined=combined,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)
