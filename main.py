
# ======= #
# IMPORTS #
# ======= #
import os                                                             # Manejo de rutas del sistema
from flask import Flask, render_template, request, redirect, url_for  # Framework web
from datetime import datetime, timedelta                              # Manejo de fechas y tiempos
import logging                                                        # Para imprimir logs en consola

from config.repo_selector import obtener_repositorios                                              # Obtiene repos locales
from git_utils.git_operations import get_local_commits, git_push_and_log, get_push_dates_from_log  # Funciones Git

# ================= #
# APP INIT + CONFIG #
# ================= #
logging.basicConfig(level=logging.INFO)      # Activa logs informativos
app = Flask(__name__)                        # Inicializa la app Flask

# =============== #
# TIME FORMATTING #
# =============== #
def format_timedelta(td: timedelta) -> str:          # Convierte timedelta a string legible HH:MM:SS
    total_seconds = int(td.total_seconds())          # Total de segundos
    hours, remainder = divmod(total_seconds, 3600)   # Divide en horas
    minutes, seconds = divmod(remainder, 60)         # Divide resto en minutos y segundos
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"  # Formato con horas
    return f"{minutes}:{seconds:02d}"                  # Formato sin horas

# ========================== #
# REPOSITORY DATA PROCESSING #
# ========================== #
def calcular_datos_repo(selected_repo):

    # ================================== #
    # 📥 CARGA DE DATOS DEL REPOSITORIO #
    # ================================= #
    commits = get_local_commits(selected_repo) or []        # Obtiene commits
    log_file = os.path.join(selected_repo, "push_log.txt")  # Ruta del log de push
    push_dates = get_push_dates_from_log(log_file) or {}    # Fechas de push

    # =============================== #
    # 🧠 PARSEO DE FECHAS DE COMMITS #
    # ============================== #
    for c in commits:
        commit_date_str = c.get('commit_date')                  # Fecha en string
        try:
            c['_dt'] = datetime.fromisoformat(commit_date_str)  # Convertir a datetime
        except Exception:
            c['_dt'] = None                                     # Si falla, se pone None

    commits_sorted = sorted([c for c in commits if c['_dt']], key=lambda x: x['_dt'])  # Ordenar commits por fecha ascendente

    # ============================================== #
    # 📌 ESTADO DEL PROYECTO (START / END / STATUS) #
    # ============================================= #
    commit_end = next((c for c in reversed(commits) if "[END]" in c.get('message', '')), None)  # Busca commit con [END]
    project_finalizado = commit_end is not None                                                 # Booleano proyecto finalizado

    fechas = [c['_dt'] for c in commits if c['_dt']]    # Lista de fechas válidas
    project_start_dt = min(fechas) if fechas else None  # Fecha inicio proyecto

    # 📅 FORMATEO FECHA INICIO PROYECTO
    if project_start_dt:                                                                # Formatear fecha de inicio
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]  # Meses en español
        dia = project_start_dt.day
        mes = meses[project_start_dt.month - 1]
        anio = project_start_dt.year
        hora = project_start_dt.strftime("%H:%M")
        project_start_formateado = f"{dia} de {mes} de {anio} a las {hora}"             # Formateado bonito
    else:
        project_start_formateado = ""

    # 📊 DÍAS TRANSCURRIDOS
    fecha_fin = datetime.fromisoformat(commit_end['commit_date']) if commit_end else datetime.now()       # Fin del proyecto
    days_passed = (max(0, (fecha_fin.date() - project_start_dt.date()).days) if project_start_dt else 0)  # Días transcurridos

    # ===================================== #
    # ⏱ TRACKING DE TAREAS (+ / - COMMITS) #
    # ==================================== #
    combined = []             # Lista final para el frontend
    last_plus_commit = None   # Último commit de inicio de tarea

    for c in commits_sorted:
        sha = c.get('sha', '')[:7]         # SHA corto
        message = c.get('message', '')     # Mensaje del commit
        commit_datetime = c.get('_dt')     # Fecha en datetime
        duracion_str = ''                  # Duración inicial vacía

        # 🔹 INICIO DE TAREA
        if message.startswith("+") and commit_datetime:
            last_plus_commit = c                                                  # Marca inicio de tarea

        # 🔹 FIN DE TAREA
        elif message.startswith("-") and commit_datetime and last_plus_commit:    # Marca final de tarea
            duracion_td = commit_datetime - last_plus_commit['_dt']               # Calcula duración
            if duracion_td.total_seconds() < 0:
                duracion_td = timedelta(0)                                        # Evita negativos
            duracion_str = format_timedelta(duracion_td)                          # Convierte a string
            logging.info(f"TAREA DETECTADA: {message}, DURACIÓN: {duracion_str}") # Log
            last_plus_commit = None                                               # Resetea

        # ====================================== #
        # 🗓 FORMATEO DE FECHA Y HORA POR COMMIT #
        # ====================================== #
        if commit_datetime:
            meses = ["ene", "feb", "mar", "abr", "may", "jun",
                     "jul", "ago", "sep", "oct", "nov", "dic"]
            dia = commit_datetime.day
            mes = meses[commit_datetime.month - 1]
            anio = commit_datetime.year
            fecha_formateada = f"{dia} de {mes} {anio}"          # Fecha corta
            hora_formateada = commit_datetime.strftime("%H:%M")  # Hora
        else:
            fecha_formateada = ""
            hora_formateada = ""

        combined.append({
            "sha": sha,
            "message": message,
            "date": fecha_formateada,
            "time": hora_formateada,
            "duration": duracion_str if message.startswith("-") else ''  # Solo en commits "-"
        })

    # =============================== #
    # 🧮 DURACIÓN TOTAL DEL PROYECTO #
    # ============================== #
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
            for d in [row['duration'] for row in combined if row['duration']]  # Solo duraciones válidas
        ),
        timedelta()
    )

    total_duration_str = format_timedelta(total_duration)

    # ======================================== #
    # 📤 RETURN FINAL (DATASET PARA FRONTEND) #
    # ======================================= #
    return (commits, 
            push_dates, 
            project_start_formateado, 
            days_passed, 
            total_duration_str, 
            project_finalizado, 
            combined
    )

# =========================== #
# 🌐 ROUTE: HOME / MAIN PAGE #
# ========================== #
@app.route("/", methods=["GET", "POST"])  # Ruta principal
def index():

    # =================================== #
    # 📦 ESTADO INICIAL (DEFAULT VALUES) #
    # ================================== #
    error_message = None                  # Mensaje de error
    selected_repo = None                  # Repo seleccionado
    commits = []
    push_dates = {}
    project_start = None
    days_passed = 0
    total_duration_str = "0:00"
    project_finalizado = False
    combined = []
    repo_choices = []

    # ===================================== #
    # 📁 CARGA DE REPOSITORIOS DISPONIBLES #
    # ==================================== #
    repos_dict = obtener_repositorios() or {}                                              # Diccionario de repos
    repo_choices = list(repos_dict.values())                                               # Lista de rutas
    selected_repo = request.form.get("repo") or repo_choices[0] if repo_choices else None  # Repo seleccionado

    # ================================= #
    # ⚡ ACCIONES POST (FORM HANDLING) #
    # ================================ #
    if request.method == "POST":
        action = request.form.get("action")                                                # Acción del formulario
        log_file = os.path.join(selected_repo, "push_log.txt") if selected_repo else None  # Log de push

        if selected_repo and action == "push":
            try:
                git_push_and_log(selected_repo, BRANCH, log_file)  # Ejecuta push
            except Exception as e:
                error_message = str(e)                             # Guarda error
            return redirect(url_for('index'))                      # Redirige

    # ================================== #
    # 📊 CARGA DE DATOS DEL REPOSITORIO #
    # ================================= #
    if selected_repo:
        try:
            (commits,
             push_dates,
             project_start,
             days_passed,
             total_duration_str,
             project_finalizado,
             combined) = calcular_datos_repo(selected_repo)  # Calcula datos
        except Exception as e:
            error_message = str(e)                           # Error

    # ============================= #
    # 🎨 RENDER DE TEMPLATE (VIEW) #
    # ============================ #
    return render_template(
        "index.html",  # Template
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

# ================================== #
# 🚀 SERVER BOOTSTRAP (ENTRY POINT) #
# ================================= #
if __name__ == "__main__":
    app.run(debug=True) # Ejecuta servidor en modo debug