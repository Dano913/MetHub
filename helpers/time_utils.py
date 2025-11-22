from datetime import datetime       # Importa la clase datetime para manejar fechas y horas

def format_timedelta(delta):
    days = delta.days                                                                       # Obtiene la cantidad de días completos en el timedelta
    hours, remainder = divmod(delta.seconds, 3600)                                          # Calcula horas y el resto en segundos
    minutes = remainder // 60                                                               # Convierte los segundos restantes a minutos
    return f"{days}d {hours:02}:{minutes:02}" if days > 0 else f"{hours:02}:{minutes:02}"   # Formatea la duración en "Xd HH:MM" si hay días, o "HH:MM" si no

def map_task_duration(commits):                                                      
    task_name = None                                                              # Guarda el nombre de la tarea
    duration_map = {}                                                             # Diccionario que almacenará duración por commit
    for c in reversed(commits):
        msg = c['message'].strip()                                                # Toma el mensaje del commit y elimina espacios
        if msg.startswith("+"):
            task_start = c                                                        # Si el mensaje empieza con "+", marca el inicio de una tarea
            task_name = msg[1:].strip()                                           # task_name guarda el nombre de la tarea
        elif msg.startswith("-") and task_start:                                  # Verifica si hay mensaje que empiece por "-" y si hay tarea iniciada
            commit_start_dt = datetime.fromisoformat(task_start['commit_date'])   # Convierte lasfechas ISO en objetos datetime
            commit_end_dt = datetime.fromisoformat(c['commit_date'])                         
            duration_map[c['sha'][:7]] = {                                        # Calcula la duración de la tarea
                "duracion": commit_end_dt - commit_start_dt,                      # Diferencia entre la hora final y la hora inicial
                "tarea": task_name                            
            }
            task_start = None                                                     # Resetea las variables para poder mapear nuevas tareas
            task_name = None
    return duration_map                                                           # Devuelve un diccionario con la duración de cada tarea detectada
