import subprocess
from datetime import datetime
import os
from config.settings import LOCAL_REPO_PATH, BRANCH, LOG_FILE

def get_local_commits(local_repo_path=LOCAL_REPO_PATH):
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H|%cI|%s"],
        cwd=local_repo_path,
        capture_output=True, text=True
    )
    commits = []
    for line in result.stdout.splitlines():
        sha, commit_date, message = line.split("|", 2)
        commits.append({"sha": sha, "commit_date": commit_date, "message": message})
    return commits

def git_push_and_log(local_repo_path=LOCAL_REPO_PATH, branch=BRANCH, log_file=LOG_FILE):
    result = subprocess.run(
        ['git', '-C', local_repo_path, 'push', 'origin', branch],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("Error en git push:", result.stderr)
        return None
    sha = subprocess.run(
        ['git', '-C', local_repo_path, 'rev-parse', 'HEAD'],
        capture_output=True, text=True
    ).stdout.strip()[:7]
    push_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"{sha};{push_time}\n")
    print(f"Pushed {sha} at {push_time}")
    return sha, push_time

def get_push_dates_from_log(log_file=LOG_FILE):
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
