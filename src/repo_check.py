import os
import subprocess

current_dir = os.environ.get('CURRENT_DIR')

def check_uncommitted_changes(repo_path):
    try:
        output = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=repo_path, text=True
        )
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False


print(f"Checking for uncommitted changes in {current_dir}")
for root, dirs, files in os.walk(current_dir):
    if ".git" in dirs:
        repo_path = os.path.abspath(root)
        if check_uncommitted_changes(repo_path):
            print(f"Uncommitted changes in {repo_path}")
