#!/usr/bin/env python3
"""
Usage Tracker - Tracks weekly and monthly limits
"""

import json
import os
from datetime import datetime, timedelta

TRACKER_FILE = "tracker/usage.json"

# ── LIMITS ──────────────────────────────────────────────────────────────────
LIMITS = {
    "weekly_runs"   : 4,
    "weekly_hours"  : 24,
    "monthly_runs"  : 15,
    "monthly_hours" : 90,
    "session_hours" : 6,
    "interval_days" : 2
}

def load_tracker():
    """Load usage tracker"""
    if not os.path.exists(TRACKER_FILE):
        return reset_tracker()

    with open(TRACKER_FILE, "r") as f:
        return json.load(f)

def save_tracker(data):
    """Save usage tracker"""
    os.makedirs("tracker", exist_ok=True)
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def reset_tracker():
    """Reset tracker to defaults"""
    now = datetime.utcnow()
    data = {
        "weekly": {
            "runs"       : 0,
            "hours"      : 0,
            "week_start" : now.strftime("%Y-%m-%d"),
            "max_runs"   : LIMITS["weekly_runs"],
            "max_hours"  : LIMITS["weekly_hours"]
        },
        "monthly": {
            "runs"        : 0,
            "hours"       : 0,
            "month_start" : now.strftime("%Y-%m-%d"),
            "max_runs"    : LIMITS["monthly_runs"],
            "max_hours"   : LIMITS["monthly_hours"]
        },
        "last_run"   : "",
        "total_runs" : 0,
        "history"    : []
    }
    save_tracker(data)
    return data

def check_week_reset(data):
    """Reset weekly counter if new week"""
    if not data["weekly"]["week_start"]:
        data["weekly"]["week_start"] = datetime.utcnow().strftime("%Y-%m-%d")
        return data

    week_start = datetime.strptime(data["weekly"]["week_start"], "%Y-%m-%d")
    if datetime.utcnow() >= week_start + timedelta(days=7):
        print("[RESET] New week detected - resetting weekly counters")
        data["weekly"]["runs"]       = 0
        data["weekly"]["hours"]      = 0
        data["weekly"]["week_start"] = datetime.utcnow().strftime("%Y-%m-%d")

    return data

def check_month_reset(data):
    """Reset monthly counter if new month"""
    if not data["monthly"]["month_start"]:
        data["monthly"]["month_start"] = datetime.utcnow().strftime("%Y-%m-%d")
        return data

    month_start = datetime.strptime(data["monthly"]["month_start"], "%Y-%m-%d")
    if datetime.utcnow() >= month_start + timedelta(days=30):
        print("[RESET] New month detected - resetting monthly counters")
        data["monthly"]["runs"]        = 0
        data["monthly"]["hours"]       = 0
        data["monthly"]["month_start"] = datetime.utcnow().strftime("%Y-%m-%d")

    return data

def can_run():
    """Check if safe to trigger new session"""
    data = load_tracker()
    data = check_week_reset(data)
    data = check_month_reset(data)
    save_tracker(data)

    now = datetime.utcnow()
    reasons = []

    # ── Check interval ───────────────────────────────────────────────────────
    if data["last_run"]:
        last = datetime.strptime(data["last_run"], "%Y-%m-%d %H:%M:%S")
        next_run = last + timedelta(days=LIMITS["interval_days"])
        if now < next_run:
            wait = next_run - now
            hours = int(wait.total_seconds() // 3600)
            mins  = int((wait.total_seconds() % 3600) // 60)
            reasons.append(f"Too soon - Next run in {hours}h {mins}m")

    # ── Check weekly runs ────────────────────────────────────────────────────
    if data["weekly"]["runs"] >= LIMITS["weekly_runs"]:
        reasons.append(
            f"Weekly run limit reached: {data['weekly']['runs']}/{LIMITS['weekly_runs']}"
        )

    # ── Check weekly hours ───────────────────────────────────────────────────
    projected_weekly = data["weekly"]["hours"] + LIMITS["session_hours"]
    if projected_weekly > LIMITS["weekly_hours"]:
        reasons.append(
            f"Weekly hour limit: {data['weekly']['hours']}/{LIMITS['weekly_hours']}hrs"
        )

    # ── Check monthly runs ───────────────────────────────────────────────────
    if data["monthly"]["runs"] >= LIMITS["monthly_runs"]:
        reasons.append(
            f"Monthly run limit reached: {data['monthly']['runs']}/{LIMITS['monthly_runs']}"
        )

    # ── Check monthly hours ──────────────────────────────────────────────────
    projected_monthly = data["monthly"]["hours"] + LIMITS["session_hours"]
    if projected_monthly > LIMITS["monthly_hours"]:
        reasons.append(
            f"Monthly hour limit: {data['monthly']['hours']}/{LIMITS['monthly_hours']}hrs"
        )

    if reasons:
        print("\n[BLOCKED] Cannot run:")
        for r in reasons:
            print(f"  ❌ {r}")
        return False, data

    print("\n[ALLOWED] Safe to run!")
    print_status(data)
    return True, data

def record_run(data):
    """Record a successful run"""
    now = datetime.utcnow()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    data["weekly"]["runs"]   += 1
    data["weekly"]["hours"]  += LIMITS["session_hours"]
    data["monthly"]["runs"]  += 1
    data["monthly"]["hours"] += LIMITS["session_hours"]
    data["last_run"]          = now_str
    data["total_runs"]       += 1

    data["history"].append({
        "run_number" : data["total_runs"],
        "timestamp"  : now_str,
        "hours"      : LIMITS["session_hours"]
    })

    # Keep last 100 history entries
    if len(data["history"]) > 100:
        data["history"] = data["history"][-100:]

    save_tracker(data)
    print(f"\n[RECORDED] Run #{data['total_runs']} logged!")
    return data

def print_status(data):
    """Print current usage status"""
    print()
    print("=" * 55)
    print("  USAGE STATUS")
    print("=" * 55)
    print(f"  Weekly  Runs  : {data['weekly']['runs']}/{LIMITS['weekly_runs']}")
    print(f"  Weekly  Hours : {data['weekly']['hours']}/{LIMITS['weekly_hours']} hrs")
    print(f"  Monthly Runs  : {data['monthly']['runs']}/{LIMITS['monthly_runs']}")
    print(f"  Monthly Hours : {data['monthly']['hours']}/{LIMITS['monthly_hours']} hrs")
    print(f"  Last Run      : {data['last_run'] or 'Never'}")
    print(f"  Total Runs    : {data['total_runs']}")
    print("=" * 55)

    # Visual bars
    w_run_pct  = int((data['weekly']['runs']   / LIMITS['weekly_runs'])   * 20)
    w_hr_pct   = int((data['weekly']['hours']  / LIMITS['weekly_hours'])  * 20)
    m_run_pct  = int((data['monthly']['runs']  / LIMITS['monthly_runs'])  * 20)
    m_hr_pct   = int((data['monthly']['hours'] / LIMITS['monthly_hours']) * 20)

    print(f"\n  Weekly Runs  : [{'#'*w_run_pct}{'-'*(20-w_run_pct)}] {data['weekly']['runs']}/{LIMITS['weekly_runs']}")
    print(f"  Weekly Hours : [{'#'*w_hr_pct}{'-'*(20-w_hr_pct)}] {data['weekly']['hours']}/{LIMITS['weekly_hours']}hrs")
    print(f"  Monthly Runs : [{'#'*m_run_pct}{'-'*(20-m_run_pct)}] {data['monthly']['runs']}/{LIMITS['monthly_runs']}")
    print(f"  Monthly Hours: [{'#'*m_hr_pct}{'-'*(20-m_hr_pct)}] {data['monthly']['hours']}/{LIMITS['monthly_hours']}hrs")
    print()


if __name__ == "__main__":
    ok, data = can_run()
    print_status(data)
    exit(0 if ok else 1)
