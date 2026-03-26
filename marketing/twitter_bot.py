"""
Twitter/X Marketing Bot for Rizz AI
Posts dating tips + product mentions.
Run 2-3x daily via cron or manually.

Setup:
1. Create X app: https://developer.x.com/
2. Get API keys (Free tier = 1,500 tweets/month)
3. Set env vars: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET
"""

import os
import random
import tweepy
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# X/Twitter API v2
x_client = tweepy.Client(
    consumer_key=os.getenv("X_API_KEY", ""),
    consumer_secret=os.getenv("X_API_SECRET", ""),
    access_token=os.getenv("X_ACCESS_TOKEN", ""),
    access_token_secret=os.getenv("X_ACCESS_SECRET", ""),
)

claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

TWEET_TYPES = [
    "tip",        # Dating texting tip
    "hook",       # Viral hook + product
    "thread",     # Mini thread (2 tweets)
    "relatable",  # Relatable dating moment
]


def generate_tweet(tweet_type: str) -> str:
    prompts = {
        "tip": """Write a viral tweet (under 280 chars) with a dating texting tip.
Format: short hook + tip + "askrizz.com" at end.
Example tone: "She said 'lol thanks' and you panicked? Here's what actually works: [tip]. Or just use askrizz.com and stop guessing."
Return ONLY the tweet text, nothing else.""",

        "hook": """Write a viral tweet (under 280 chars) about dating texting struggles.
Use a relatable hook that makes people stop scrolling.
End with: "askrizz.com — AI that texts better than you"
Return ONLY the tweet text.""",

        "relatable": """Write a funny/relatable tweet (under 280 chars) about overthinking texts to your crush.
Don't mention any product. Just be funny and relatable.
Return ONLY the tweet text.""",

        "thread": """Write a tweet (under 280 chars) that starts a conversation about dating texting.
Ask a question that gets engagement. Like "What's the worst text you've ever sent to a crush?"
Return ONLY the tweet text.""",
    }

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        system="You write viral tweets. Gen Z tone. Short, punchy, relatable. No hashtags unless truly viral ones.",
        messages=[{"role": "user", "content": prompts[tweet_type]}]
    )

    text = response.content[0].text.strip().strip('"')
    # Ensure under 280 chars
    if len(text) > 280:
        text = text[:277] + "..."
    return text


def post_tweet(text: str):
    try:
        result = x_client.create_tweet(text=text)
        tweet_id = result.data["id"]
        url = f"https://x.com/i/status/{tweet_id}"
        print(f"  Posted: {url}")
        print(f"  Text: {text}")
        return url
    except Exception as e:
        print(f"  Error: {e}")
        return None


def daily_run():
    print("Twitter Bot — Daily Run")
    print("=" * 40)

    tweet_type = random.choice(TWEET_TYPES)
    print(f"  Type: {tweet_type}")

    text = generate_tweet(tweet_type)
    print(f"  Generated: {text[:50]}...")

    url = post_tweet(text)

    # If relatable (no product mention), reply with product
    if tweet_type == "relatable" and url:
        import time
        time.sleep(60)
        reply = "ngl askrizz.com saved me from so many bad texts lol"
        try:
            tweet_id = url.split("/")[-1]
            x_client.create_tweet(text=reply, in_reply_to_tweet_id=tweet_id)
            print(f"  Added reply with product mention")
        except Exception as e:
            print(f"  Reply error: {e}")


if __name__ == "__main__":
    daily_run()
