# ================================ #
# ⏱️ UTILIDAD: FORMATEO DE TIEMPO #
# =============================== #
from datetime import datetime, timedelta


def format_timedelta(delta):
    """
    Convierte un timedelta en formato legible:
    - Si hay días → "Xd HH:MM"
    - Si no → "HH:MM"
    """

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60

    if days > 0:
        return f"{days}d {hours:02}:{minutes:02}"

    return f"{hours:02}:{minutes:02}"


# =================================================== #
# 📊 LÓGICA PRINCIPAL: CÁLCULO DE DURACIÓN DE TAREAS #
# ================================================== #
def calcular_duracion_tareas(commits):
    """
    Detecta tareas a partir de commits:

    FORMATO ESPERADO:
        +nombre  → inicio de tarea
        -nombre  → fin de tarea

    RETORNA:
        dict {
            sha_fin: {
                tarea,
                inicio,
                fin,
                duracion
            }
        }
    """

    # ------------------ #
    # 📦 ESTADO INTERNO #
    # ----------------- #
    tareas = {}
    tarea_actual = None
    inicio_commit = None

    # ------------------------- #
    # 🔄 ORDENACIÓN DE COMMITS #
    # ------------------------ #
    # Se procesan de más antiguo → más reciente
    commits_ordenados = list(reversed(commits))

    # ----------------------- #
    # 🔍 RECORRIDO PRINCIPAL #
    # ---------------------- #
    for c in commits_ordenados:

        msg = c.get("message", "").strip()

        # ------------------- #
        # 🚀 INICIO DE TAREA #
        # ------------------ #
        if msg.startswith("+"):
            tarea_actual = msg[1:].strip()
            inicio_commit = c
            continue

        # ---------------- #
        # 🏁 FIN DE TAREA #
        # --------------- #
        if msg.startswith("-") and tarea_actual and inicio_commit:

            try:
                inicio_dt = datetime.fromisoformat(
                    inicio_commit["commit_date"].replace("Z", "+00:00")
                )

                fin_dt = datetime.fromisoformat(
                    c["commit_date"].replace("Z", "+00:00")
                )

            except Exception:
                # Si hay error de fecha, ignorar este bloque
                continue

            tareas[c["sha"][:7]] = {
                "tarea": tarea_actual,
                "inicio": inicio_dt,
                "fin": fin_dt,
                "duracion": fin_dt - inicio_dt,
            }

            # reset del estado
            tarea_actual = None
            inicio_commit = None

    # ------------------- #
    # 📤 RESULTADO FINAL #
    # ------------------ #
    return tareas