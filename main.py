from git_utils.git_operations import get_local_commits, git_push_and_log, get_push_dates_from_log
from helpers.time_utils import map_task_duration, format_timedelta
from datetime import datetime

commits = get_local_commits()
push_dates = get_push_dates_from_log()

push_result = git_push_and_log()
if push_result:
    sha_push, push_time = push_result
    push_dates[sha_push] = push_time

task_duration_map = map_task_duration(commits)

print(f"{'SHA':<8} {'Commit Date':<20} {'Time':<15} {'Message'}")
print("-"*100)
for c in commits:
    sha_short = c['sha'][:7]
    commit_dt = datetime.fromisoformat(c['commit_date']).replace(tzinfo=None)
    commit_str = commit_dt.strftime("%Y-%m-%d %H:%M:%S")
    duracion_tarea = ""
    if sha_short in task_duration_map:
        duracion_tarea = format_timedelta(task_duration_map[sha_short]["duracion"])
    print(f"{sha_short:<8} {commit_str:<20} {duracion_tarea:<15} {c['message']}")
