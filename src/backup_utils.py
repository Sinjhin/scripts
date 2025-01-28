import os
import subprocess

def check_uncommitted_changes(repo_path):
    try:
        output = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=repo_path, text=True
        )
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

for root, dirs, files in os.walk("."):
    if ".git" in dirs:
        repo_path = os.path.abspath(root)
        if check_uncommitted_changes(repo_path):
            print(f"Uncommitted changes in {repo_path}")
