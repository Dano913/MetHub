from datetime import datetime

def format_timedelta(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    return f"{days}d {hours:02}:{minutes:02}" if days > 0 else f"{hours:02}:{minutes:02}"

def map_task_duration(commits):
    task_start = None
    task_name = None
    duration_map = {}
    for c in reversed(commits):
        msg = c['message'].strip()
        if msg.startswith("+"):
            task_start = c
            task_name = msg[1:].strip()
        elif msg.startswith("-") and task_start:
            commit_start_dt = datetime.fromisoformat(task_start['commit_date'])
            commit_end_dt = datetime.fromisoformat(c['commit_date'])
            duration_map[c['sha'][:7]] = {"duracion": commit_end_dt - commit_start_dt, "tarea": task_name}
            task_start = None
            task_name = None
    return duration_map
