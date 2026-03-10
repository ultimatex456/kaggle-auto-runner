#!/usr/bin/env python3
"""
Kaggle Kernel Trigger Script
Checks limits then pushes kernel
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.tracker import can_run, record_run, load_tracker, print_status

KAGGLE_USERNAME = os.environ.get("KAGGLE_USERNAME", "")
KAGGLE_KEY      = os.environ.get("KAGGLE_KEY",      "")
KERNEL_NAME     = os.environ.get("KERNEL_NAME",     "kaggle-auto-runner")

def setup_kaggle_auth():
    os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
    creds      = {"username": KAGGLE_USERNAME, "key": KAGGLE_KEY}
    creds_path = os.path.expanduser("~/.kaggle/kaggle.json")
    with open(creds_path, "w") as f:
        json.dump(creds, f)
    os.chmod(creds_path, 0o600)
    print("[✓] Kaggle credentials configured")

def push_kernel():
    print(f"\n[PUSH] Pushing kernel...")
    result = subprocess.run(
        ["kaggle", "kernels", "push", "-p", "./kernel"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}")
        return False
    print("[✓] Kernel pushed!")
    return True

def main():
    print()
    print("=" * 60)
    print("  KAGGLE AUTO RUNNER - TRIGGER SCRIPT")
    print(f"  Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    # Check limits
    print("\n[1/3] Checking usage limits...")
    allowed, data = can_run()

    if not allowed:
        print("\n[SKIP] Limits reached - skipping run")
        sys.exit(0)

    # Setup auth
    print("\n[2/3] Setting up Kaggle auth...")
    if not KAGGLE_USERNAME or not KAGGLE_KEY:
        print("[ERROR] Missing KAGGLE_USERNAME or KAGGLE_KEY!")
        sys.exit(1)
    setup_kaggle_auth()

    # Push kernel
    print("\n[3/3] Pushing kernel to Kaggle...")
    if not push_kernel():
        print("[ERROR] Failed to push kernel!")
        sys.exit(1)

    # Record run
    data = record_run(data)
    print_status(data)
    print("\n[✓] TRIGGER COMPLETE!")

if __name__ == "__main__":
    main()
