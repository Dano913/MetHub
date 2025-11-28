from datetime import datetime, timedelta

def format_timedelta(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    return f"{days}d {hours:02}:{minutes:02}" if days > 0 else f"{hours:02}:{minutes:02}"


def calcular_duracion_tareas(commits):
    """
    Detecta tareas usando commits con + (inicio) y - (fin).
    Retorna un dict:
        { sha_fin: { tarea, inicio, fin, duracion } }
    """

    tareas = {}
    tarea_actual = None
    inicio_commit = None

    # IMPORTANTE: recorrer commits en orden ASCENDENTE (del más antiguo al más nuevo)
    commits_ordenados = list(reversed(commits))

    for c in commits_ordenados:
        msg = c.get("message", "").strip()

        # ------------------------------------------
        # INICIO DE TAREA  (+nombre)
        # ------------------------------------------
        if msg.startswith("+"):
            tarea_actual = msg[1:].strip()
            inicio_commit = c
            continue

        # ------------------------------------------
        # FIN DE TAREA  (-nombre)
        # ------------------------------------------
        if msg.startswith("-") and tarea_actual and inicio_commit:

            try:
                inicio_dt = datetime.fromisoformat(
                    inicio_commit["commit_date"].replace("Z", "+00:00")
                )
                fin_dt = datetime.fromisoformat(
                    c["commit_date"].replace("Z", "+00:00")
                )
            except Exception:
                continue

            tareas[c["sha"][:7]] = {
                "tarea": tarea_actual,
                "inicio": inicio_dt,
                "fin": fin_dt,
                "duracion": fin_dt - inicio_dt,
            }

            # reset
            tarea_actual = None
            inicio_commit = None

    return tareas
