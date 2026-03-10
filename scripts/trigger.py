#!/usr/bin/env python3
"""
Kaggle Kernel Trigger Script
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.tracker import can_run, record_run, load_tracker, print_status

KAGGLE_USERNAME = os.environ.get("KAGGLE_USERNAME")
KAGGLE_KEY      = os.environ.get("KAGGLE_KEY")
KERNEL_NAME     = os.environ.get("KERNEL_NAME", "kaggle-auto-runner")

def setup_kaggle_auth():
    """Setup Kaggle API credentials"""
    os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
    creds = {
        "username": KAGGLE_USERNAME,
        "key"     : KAGGLE_KEY
    }
    creds_path = os.path.expanduser("~/.kaggle/kaggle.json")
    with open(creds_path, "w") as f:
        json.dump(creds, f)
    os.chmod(creds_path, 0o600)
    print("[✓] Kaggle credentials configured")

def push_kernel():
    """Push kernel to Kaggle"""
    print(f"\n[PUSH] Pushing kernel to Kaggle...")

    result = subprocess.run(
        ["kaggle", "kernels", "push", "-p", "./kernel"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"[ERROR] Push failed:\n{result.stderr}")
        return False

    print("[✓] Kernel pushed successfully!")
    return True

def wait_for_running():
    """Wait for kernel to start running"""
    kernel_id = f"{KAGGLE_USERNAME}/{KERNEL_NAME}"
    print(f"\n[WAIT] Waiting for kernel to start: {kernel_id}")

    for i in range(10):
        time.sleep(15)
        result = subprocess.run(
            ["kaggle", "kernels", "status", kernel_id],
            capture_output=True,
            text=True
        )
        output = result.stdout.lower()
        print(f"  Status check {i+1}: {result.stdout.strip()}")

        if "running" in output or "complete" in output:
            print("[✓] Kernel is running!")
            return True
        if "error" in output or "cancel" in output:
            print("[✗] Kernel failed to start!")
            return False

    return True

def main():
    print()
    print("=" * 60)
    print("  KAGGLE AUTO RUNNER - TRIGGER")
    print(f"  Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    # ── Step 1: Check limits ─────────────────────────────────────────────────
    print("\n[1/4] Checking usage limits...")
    allowed, data = can_run()

    if not allowed:
        print("\n[SKIP] Limits reached - skipping this run")
        sys.exit(0)

    # ── Step 2: Setup auth ───────────────────────────────────────────────────
    print("\n[2/4] Setting up Kaggle auth...")
    if not KAGGLE_USERNAME or not KAGGLE_KEY:
        print("[ERROR] Missing KAGGLE_USERNAME or KAGGLE_KEY secrets!")
        sys.exit(1)
    setup_kaggle_auth()

    # ── Step 3: Push kernel ──────────────────────────────────────────────────
    print("\n[3/4] Pushing kernel...")
    if not push_kernel():
        print("[ERROR] Failed to push kernel!")
        sys.exit(1)

    # ── Step 4: Record run ───────────────────────────────────────────────────
    print("\n[4/4] Recording run...")
    data = record_run(data)
    print_status(data)

    # ── Wait for start ───────────────────────────────────────────────────────
    wait_for_running()

    print("\n[✓] TRIGGER COMPLETE!")
    print(f"  Kernel    : {KAGGLE_USERNAME}/{KERNEL_NAME}")
    print(f"  Triggered : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()


if __name__ == "__main__":
    main()
