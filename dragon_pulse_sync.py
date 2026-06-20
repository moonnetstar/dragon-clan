import os
import subprocess
from datetime import datetime

# Configuration
REPO_PATH = os.path.expanduser("~/Desktop/龍族報告")
COMMIT_PREFIX = "Heartbeat"

def run_cmd(command, cwd):
    """Helper to run shell commands and return output."""
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR: {e.stderr.strip()}"

def pulse_sync():
    print(f"--- 🐉 Dragon Clan Pulse Sync Started ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    
    if not os.path.exists(os.path.join(REPO_PATH, ".git")):
        print(f"❌ Error: {REPO_PATH} is not a Git repository!")
        return

    # 1. Check for changes (git status --porcelain)
    status = run_cmd("git status --porcelain", REPO_PATH)
    
    if not status:
        print("💓 [Steady] No changes detected. The heartbeat is steady.")
        return
    
    print(f"✨ Detected changes:\n{status}")

    # 2. git add .
    run_cmd("git add .", REPO_PATH)
    print("✅ All changes staged (git add).")

    # 3. git commit -m "Heartbeat: [Timestamp]"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"{COMMIT_PREFIX}: {timestamp}"
    commit_result = run_cmd(f'git commit -m "{commit_msg}"', REPO_PATH)
    
    if "ERROR" in commit_result:
        print(f"⚠️ Commit failed: {commit_result}")
    else:
        print(f"✅ Commit Successful! [{commit_msg}]")
        print(commit_result)

    # 4. Check if remote 'origin' exists, then try to push
    remotes = run_cmd("git remote", REPO_PATH)
    if "origin" in remotes:
        print("☁️ Detected remote 'origin'. Attempting push...")
        push_result = run_cmd("git push", REPO_PATH)
        if "ERROR" in push_result:
            print(f"ℹ️ Push skipped/failed (likely needs auth): {push_result}")
        else:
            print(f"🚀 Push Successful!\n{push_result}")
    else:
        print("ℹ️ No remote 'origin' detected. Pulse kept local.")

    print("--- ✅ Pulse Sync Completed ---")

if __name__ == "__main__":
    pulse_sync()
