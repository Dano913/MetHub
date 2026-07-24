# =========== #
# 📦 IMPORTS #
# ========== #
import os                    # Manejo de rutas y archivos
import subprocess            # Ejecución de comandos Git
from datetime import datetime  # Manejo de fechas y horas


# ================================== #
# 📥 GET COMMITS: REPOSITORIO LOCAL #
# ================================= #
def get_local_commits(repo_path):
    """
    Obtiene commits locales del repositorio usando git log
    """

    # 🔹 Comando Git:
    # -C → ejecuta en el repo indicado
    # --pretty → formatea salida: SHA | fecha ISO | mensaje
    cmd = [
        "git",
        "-C",
        repo_path,
        "log",
        "--pretty=format:%H|%cI|%s"
    ]

    # 🔹 Ejecuta el comando y captura salida como texto
    result = subprocess.check_output(
        cmd,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    # 🔹 Parseo de commits
    commits = []
    for line in result.splitlines():

        # Divide en: SHA | fecha | mensaje
        sha, date, msg = line.split("|", 2)

        commits.append({
            "sha": sha,
            "commit_date": date,
            "message": msg
        })

    return commits


# ===================================== #
# 📄 GET PUSH LOG: HISTORIAL DE PUSHES #
# ==================================== #
def get_push_dates_from_log(log_file):
    """
    Lee archivo de log y devuelve:
        { sha: fecha_push }
    """

    push_dates = {}

    # 🔹 Si no existe el archivo → vacío
    if not os.path.exists(log_file):
        return push_dates

    # 🔹 Lectura del archivo
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:

            # Cada línea: SHA + fecha
            sha, date = line.strip().split()

            push_dates[sha] = date

    return push_dates


# ================== #
# 🚀 GIT PUSH + LOG #
# ================= #
def git_push_and_log(repo_path, branch, log_file):
    """
    Ejecuta git push y guarda:
        SHA + timestamp en log_file
    """

    try:
        # 🔹 Ejecuta: git push origin <branch>
        subprocess.check_call([
            "git",
            "-C",
            repo_path,
            "push",
            "origin",
            branch
        ])

        # 🔹 Timestamp actual
        push_time = datetime.now().isoformat()

        # 🔹 Obtener último commit (HEAD)
        last_commit_sha = subprocess.check_output(
            [
                "git",
                "-C",
                repo_path,
                "rev-parse",
                "HEAD"
            ],
            text=True
        ).strip()

        # 🔹 Guardar en log: SHA + fecha
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{last_commit_sha} {push_time}\n")

        return last_commit_sha, push_time

    except subprocess.CalledProcessError:
        # 🔹 Si falla el push
        return None