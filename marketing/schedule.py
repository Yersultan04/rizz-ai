"""
Rizz AI — Scheduled Marketing Runner
Runs Twitter bot every 12 hours.
Start: python schedule.py
Runs in background indefinitely.
"""

import time
import sys
import os
from datetime import datetime

# Run interval in seconds (12 hours)
INTERVAL = 12 * 60 * 60

def run_twitter():
    """Run twitter bot."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Running Twitter bot...")
    try:
        # Import and run from same directory
        sys.path.insert(0, os.path.dirname(__file__))
        from twitter_bot import daily_run
        daily_run()
    except Exception as e:
        print(f"  Error: {e}")


def run_video():
    """Generate video storyboard."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Generating video...")
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from video_generator import generate_video
        generate_video()
    except Exception as e:
        print(f"  Error: {e}")


def main():
    print("Rizz AI — Autonomous Marketing Scheduler")
    print(f"Posting every {INTERVAL // 3600} hours")
    print("=" * 40)

    # Run immediately on start
    run_twitter()
    run_video()

    # Then loop
    while True:
        print(f"\nNext run in {INTERVAL // 3600} hours... (Ctrl+C to stop)")
        time.sleep(INTERVAL)
        run_twitter()
        run_video()


if __name__ == "__main__":
    main()
