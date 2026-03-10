#!/usr/bin/env python3
"""
Check current usage status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.tracker import load_tracker, print_status, check_week_reset, check_month_reset, save_tracker

def main():
    data = load_tracker()
    data = check_week_reset(data)
    data = check_month_reset(data)
    save_tracker(data)
    print_status(data)

if __name__ == "__main__":
    main()
