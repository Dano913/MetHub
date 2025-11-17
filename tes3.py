# combined_commits_tasks_push.py
import subprocess
from datetime import datetime, timedelta
import os

# --- Configuración ---
LOCAL_REPO_PATH = r"C:\Users\danie\Desktop\Proyectos\Funcionan\CodexJs"
BRANCH = "main"
LOG_FILE = os.path.join(LOCAL_REPO_PATH, "push_log.txt")

# --- Funciones ---
def get_local_commits(local_repo_path=LOCAL_REPO_PATH):
    """Obtiene todos los commits locales con SHA completo, fecha y mensaje"""
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H|%cI|%s"],
        cwd=local_repo_path,
        capture_output=True, text=True
    )
    commits = []
    for line in result.stdout.splitlines():
        sha, commit_date, message = line.split("|", 2)
        commits.append({
            "sha": sha,
            "commit_date": commit_date,
            "message": message
        })
    return commits

def git_push_and_log(local_repo_path=LOCAL_REPO_PATH, branch=BRANCH, log_file=LOG_FILE):
    """Hace git push y registra la hora exacta en que se hizo push"""
    result = subprocess.run(
        ['git', '-C', local_repo_path, 'push', 'origin', branch],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error en git push:", result.stderr)
        return None
    
    result = subprocess.run(
        ['git', '-C', local_repo_path, 'rev-parse', 'HEAD'],
        capture_output=True, text=True
    )
    sha = result.stdout.strip()[:7]

    push_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, 'a') as f:
        f.write(f"{sha};{push_time}\n")
    
    print(f"Pushed {sha} at {push_time}")
    return sha, push_time

def get_push_dates_from_log(log_file=LOG_FILE):
    """Devuelve diccionario {SHA corto: push_datetime}"""
    if not os.path.exists(log_file):
        return {}
    push_dates = {}
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) != 2:
                continue
            sha, push_time = parts
            push_dates[sha] = push_time
    return push_dates

def format_timedelta(delta):
    """Convierte un timedelta en string legible: Xd HH:MM"""
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    if days > 0:
        return f"{days}d {hours:02}:{minutes:02}"
    else:
        return f"{hours:02}:{minutes:02}"

def map_task_duration(commits):
    """Devuelve diccionario: sha del commit '-' → duración del bloque"""
    task_start = None
    task_name = None
    duration_map = {}

    for c in reversed(commits):  # de más antiguo a más reciente
        msg = c['message'].strip()
        if msg.startswith("+"):
            task_start = c
            task_name = msg[1:].strip()
        elif msg.startswith("-") and task_start:
            commit_start_dt = datetime.fromisoformat(task_start['commit_date'])
            commit_end_dt = datetime.fromisoformat(c['commit_date'])
            duration_map[c['sha'][:7]] = {
                "duracion": commit_end_dt - commit_start_dt,
                "tarea": task_name
            }
            task_start = None
            task_name = None
    return duration_map

# --- Flujo principal ---
commits = get_local_commits()
push_dates = get_push_dates_from_log()

# Hacer push y registrar hora exacta
push_result = git_push_and_log()
if push_result:
    sha_push, push_time = push_result
    push_dates[sha_push] = push_time

# Mapear duraciones de tareas
task_duration_map = map_task_duration(commits)

# --- Mostrar tabla de commits con duración de tareas ---
print(f"{'SHA':<8} {'Commit Date':<20} {'Duracion Tarea':<15} {'Mensaje'}")
print("-"*100)

for c in commits:
    sha_short = c['sha'][:7]

    # Commit date
    commit_dt = datetime.fromisoformat(c['commit_date']).replace(tzinfo=None)
    commit_str = commit_dt.strftime("%Y-%m-%d %H:%M:%S")

    # Duración de tarea solo para commit '-'
    duracion_tarea = ""
    if sha_short in task_duration_map:
        duracion_tarea = format_timedelta(task_duration_map[sha_short]["duracion"])

    print(f"{sha_short:<8} {commit_str:<20} {duracion_tarea:<15} {c['message']}")
