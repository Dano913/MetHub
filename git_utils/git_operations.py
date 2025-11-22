import os                           # Para manejar rutas y verificar existencia de archivos
import subprocess                   # Para ejecutar comandos de Git desde Python
from datetime import datetime       # Para trabajar con fechas y horas

def get_local_commits(repo_path):        # Obtiene commits locales del repositorio
    cmd = [                              #Construye el comando Git para listar los commits
        "git", 
        "-C", 
        repo_path,                       # Indica que el comando se ejecuta en ese repositorio
        "log", 
        "--pretty=format:%H|%cI|%s"      # Devuelve por cada commit hash completo, fecha en ISO 8601 y mensaje
    ]
    result = subprocess.check_output(    # Ejecuta el comando git log
        cmd, 
        text=True,                       # Captura la salida como texto
        encoding="utf-8",                
        errors="ignore"                  # Ignora errores de codificación
    )
    
    commits = []                             # Lista vacía para almacenar commits
    for line in result.splitlines():         # Recorre cada línea de salida
        sha, date, msg = line.split("|", 2)  # Separa la línea en 3 partes has, fecha y mensaje
        commits.append({                     # Lo agrega como diccionario
            "sha": sha, 
            "commit_date": date, 
            "message": msg
        })
    return commits                           # Devuelve la lista de commits


def get_push_dates_from_log(log_file):          # Lee las fechas de push desde el archivo de log 
    push_dates = {}                             # Diccionario vacío para almacenar fechas
    
    if not os.path.exists(log_file):            
        return push_dates                       # Si no existe el log, retorna diccionario vacío
    
    with open(                                  #Lee el archivo 
        log_file, 
        "r", 
        encoding="utf-8"
    ) as f:
        for line in f:
            sha, date = line.strip().split()    # Cada línea tiene SHA y fecha separados
            push_dates[sha] = date              # Guarda en el diccionario
    
    return push_dates                           # Devuelve el diccionario con fechas de push


def git_push_and_log(                           
        repo_path, 
        branch,                                            # Hace git push
        log_file                                           # Guarda registro en log
):
    try:
        subprocess.check_call([                            # Intenta ejecutar git push origin <branch> en el repo
            "git", 
            "-C", 
            repo_path, 
            "push", 
            "origin", 
            branch
        ])
        push_time = datetime.now().isoformat()             # Guarda la fecha y hora actual del push
        
        last_commit_sha = subprocess.check_output([        # Obtiene el hash del último commit en la rama actual después del push
            "git", 
            "-C", 
            repo_path, 
            "rev-parse", 
            "HEAD"
        ], 
            text=True
        ).strip()
        
        with open(                                         # Añade SHA y fecha al log
            log_file, 
            "a", 
            encoding="utf-8"
        ) as f:
            f.write(f"{last_commit_sha} {push_time}\n")
        
        return last_commit_sha, push_time                  # Devuelve SHA y fecha del push

    except subprocess.CalledProcessError:
        return None                                        # Si falla el git push, devuelve None
