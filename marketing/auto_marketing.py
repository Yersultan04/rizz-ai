"""
Rizz AI — Autonomous Marketing Engine
Runs all marketing channels on schedule.
Deploy as cron job or run manually.

Usage:
  python auto_marketing.py           # Run all channels once
  python auto_marketing.py reddit    # Reddit only
  python auto_marketing.py twitter   # Twitter only
  python auto_marketing.py video     # Generate video only
"""

import sys
import os
import json
import random
from datetime import datetime
from pathlib import Path

# Add parent dir for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

LOG_FILE = os.path.join(os.path.dirname(__file__), "marketing_log.json")


def log_action(channel: str, action: str, url: str = "", status: str = "success"):
    """Log marketing action."""
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)

    logs.append({
        "timestamp": datetime.now().isoformat(),
        "channel": channel,
        "action": action,
        "url": url,
        "status": status,
    })

    # Keep last 100 entries
    logs = logs[-100:]
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def run_reddit():
    """Post to Reddit."""
    print("\n[REDDIT]")
    try:
        from reddit_bot import daily_run
        daily_run()
        log_action("reddit", "daily_post")
    except Exception as e:
        print(f"  Error: {e}")
        log_action("reddit", "daily_post", status=f"error: {e}")


def run_twitter():
    """Post to Twitter/X."""
    print("\n[TWITTER]")
    try:
        from twitter_bot import daily_run
        daily_run()
        log_action("twitter", "daily_tweet")
    except Exception as e:
        print(f"  Error: {e}")
        log_action("twitter", "daily_tweet", status=f"error: {e}")


def run_video():
    """Generate marketing video."""
    print("\n[VIDEO]")
    try:
        from video_generator import generate_video
        path = generate_video()
        log_action("video", "generated", path)
    except Exception as e:
        print(f"  Error: {e}")
        log_action("video", "generate", status=f"error: {e}")


def show_stats():
    """Show marketing stats."""
    if not os.path.exists(LOG_FILE):
        print("No marketing activity yet.")
        return

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    print(f"\n{'='*40}")
    print(f"Marketing Stats — Last 7 days")
    print(f"{'='*40}")

    from collections import Counter
    channels = Counter(l["channel"] for l in logs)
    for ch, count in channels.most_common():
        print(f"  {ch}: {count} actions")

    successes = sum(1 for l in logs if l["status"] == "success")
    print(f"\n  Total: {len(logs)} actions, {successes} successful")
    print(f"  Last: {logs[-1]['timestamp'][:16]} — {logs[-1]['channel']}")


def main():
    print(f"Rizz AI — Autonomous Marketing Engine")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*40}")

    args = sys.argv[1:] if len(sys.argv) > 1 else ["all"]

    if "reddit" in args or "all" in args:
        run_reddit()

    if "twitter" in args or "all" in args:
        run_twitter()

    if "video" in args or "all" in args:
        run_video()

    if "stats" in args:
        show_stats()

    print(f"\nDone.")


if __name__ == "__main__":
    main()
