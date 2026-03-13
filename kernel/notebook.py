#!/usr/bin/env python3
"""
KAGGLE BOT - SAFE AUTOMATED RUNNER
Anti-Sleep | Anti-Disconnect | 6 Hour Runtime | Auto-Shutdown
"""

import os
import sys
import time
import signal
import threading
import subprocess
import re
import random
from datetime import datetime, timedelta

SCRIPT_FILE_ID      = "1xqp8vWaWqnIygHZUjjNmE7Umn-WP8g46"
MAX_RUNTIME_HOURS   = 6
MAX_RUNTIME_SECONDS = MAX_RUNTIME_HOURS * 60 * 60
START_TIME          = time.time()

print()
print("=" * 70)
print("  KAGGLE BOT - AUTOMATED RUNNER")
print("=" * 70)
print(f"  Start Time  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"  Max Runtime : {MAX_RUNTIME_HOURS} hours")
print(f"  Auto-Stop   : {(datetime.now() + timedelta(hours=MAX_RUNTIME_HOURS)).strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"  Platform    : Kaggle (4 vCPU 16GB RAM)")
print("=" * 70)
print()

class KeepAliveSystem:
    def __init__(self):
        self.running       = True
        self.thread        = None
        self.ping_count    = 0
        self.memory_anchor = []

    def _cpu_activity(self):
        _ = sum(range(random.randint(5000, 15000)))
        _ = [x**2 for x in range(1000)]
        _ = "".join([chr(random.randint(65, 90)) for _ in range(100)])

    def _memory_activity(self):
        self.memory_anchor.append(time.time())
        if len(self.memory_anchor) > 100:
            self.memory_anchor = self.memory_anchor[-50:]

    def _disk_activity(self):
        try:
            with open("/tmp/.kaggle_heartbeat", "w") as f:
                f.write(str(time.time()))
        except:
            pass

    def _keep_alive_loop(self):
        while self.running:
            elapsed   = time.time() - START_TIME
            remaining = MAX_RUNTIME_SECONDS - elapsed

            if remaining <= 0:
                print("\n" + "=" * 70)
                print("[TIME] 6 hours reached - Auto shutdown")
                print("=" * 70)
                self.running = False
                os._exit(0)
                break

            if remaining <= 300 and remaining > 240:
                print(f"\n[WARNING] {int(remaining//60)} minutes remaining!")

            self.ping_count += 1
            self._cpu_activity()
            self._memory_activity()

            if self.ping_count % 5  == 0: self._disk_activity()
            if self.ping_count % 15 == 0:
                eh = int(elapsed   // 3600)
                em = int((elapsed   % 3600) // 60)
                rh = int(remaining // 3600)
                rm = int((remaining % 3600) // 60)
                print(f"[ALIVE] Elapsed: {eh}h {em}m | Remaining: {rh}h {rm}m | Pings: {self.ping_count}")

            time.sleep(random.randint(45, 75))

    def start(self):
        self.thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.thread.start()
        print("[OK] Anti-Sleep      : ACTIVE")
        print("[OK] Anti-Disconnect : ACTIVE")
        print("[OK] Auto-Shutdown   : ACTIVE (6 hours)")
        print()

    def stop(self):
        self.running = False


class HeartbeatSystem:
    def __init__(self):
        self.running = True
        self.thread  = None

    def _loop(self):
        while self.running:
            if time.time() - START_TIME >= MAX_RUNTIME_SECONDS:
                break
            sys.stdout.flush()
            sys.stderr.flush()
            time.sleep(600)
            if self.running:
                print(".", end="", flush=True)

    def start(self):
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False


keep_alive = KeepAliveSystem()
keep_alive.start()
heartbeat  = HeartbeatSystem()
heartbeat.start()


def graceful_shutdown(signum, frame):
    print("\n[STOP] Shutdown signal - exiting...")
    keep_alive.stop()
    heartbeat.stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT,  graceful_shutdown)

# STEP 1
print("[1/4] Installing dependencies...")
os.system("pip install gdown requests --quiet 2>/dev/null")
print("[OK] Done")
print()

# STEP 2
print("[2/4] Downloading script from Google Drive...")
if os.path.exists("my_script.py"):
    os.remove("my_script.py")

download_ok = False
for attempt in range(3):
    result = subprocess.run(
        ["gdown", SCRIPT_FILE_ID, "-O", "my_script.py"],
        capture_output=True, text=True
    )
    if os.path.exists("my_script.py") and os.path.getsize("my_script.py") > 0:
        print(f"[OK] Downloaded: {os.path.getsize('my_script.py'):,} bytes")
        download_ok = True
        break
    print(f"[RETRY] Attempt {attempt+1}/3 failed...")
    time.sleep(5)

if not download_ok:
    print("[ERROR] Download failed after 3 attempts")
    sys.exit(1)
print()

# STEP 3
print("[3/4] Clearing Telegram conflicts...")
import requests
try:
    with open('my_script.py', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'TELEGRAM_BOT_TOKEN\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        token = match.group(1)
        try:
            requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=10)
            requests.get(f"https://api.telegram.org/bot{token}/getUpdates?offset=-1", timeout=10)
            time.sleep(2)
            print("[OK] Telegram cleared")
        except:
            print("[WARN] Could not clear Telegram")
    else:
        print("[INFO] No Telegram token found")
except Exception as e:
    print(f"[WARN] {e}")
print()

# STEP 4
print("=" * 70)
print("  [4/4] STARTING BOT")
print("=" * 70)
print()

MAX_RESTARTS  = 5
restart_count = 0

while restart_count < MAX_RESTARTS:
    elapsed   = time.time() - START_TIME
    remaining = MAX_RUNTIME_SECONDS - elapsed

    if remaining <= 60:
        print("\n[TIME] Time limit reached")
        break

    try:
        print(f"[RUN] Attempt {restart_count + 1}...")
        exec(open("my_script.py", encoding='utf-8').read())
        break

    except KeyboardInterrupt:
        print("\n[STOP] Interrupted")
        break

    except SystemExit as e:
        if e.code == 0:
            print("[OK] Script exited normally")
            break
        restart_count += 1
        print(f"[WARN] Exit code: {e.code}")

    except Exception as e:
        restart_count += 1
        print(f"[ERROR] {e}")
        print(f"[RESTART] {restart_count}/{MAX_RESTARTS} in 30s...")
        time.sleep(30)

total = time.time() - START_TIME
h = int(total // 3600)
m = int((total % 3600) // 60)
s = int(total % 60)

print()
print("=" * 70)
print("  SESSION COMPLETE")
print(f"  Runtime  : {h}h {m}m {s}s")
print(f"  Restarts : {restart_count}")
print("=" * 70)

keep_alive.stop()
heartbeat.stop()
