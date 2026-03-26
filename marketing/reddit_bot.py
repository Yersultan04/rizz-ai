"""
Reddit Marketing Bot for Rizz AI
Posts helpful dating advice with subtle product mentions.
Run daily via cron or manually.

Setup:
1. Create Reddit app: https://www.reddit.com/prefs/apps/
2. Choose "script" type
3. Set env vars: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
"""

import os
import random
import time
import praw
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID", ""),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
    username=os.getenv("REDDIT_USERNAME", ""),
    password=os.getenv("REDDIT_PASSWORD", ""),
    user_agent="RizzAI-Helper/1.0"
)

# Claude for generating content
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

# Subreddits to post in (rotate)
SUBREDDITS = [
    "dating_advice",
    "dating",
    "Bumble",
    "hingeapp",
    "Tinder",
    "OnlineDating",
    "seduction",
    "socialskills",
    "relationship_advice",
]

# Post types
POST_TYPES = [
    "tip",      # Dating tip with subtle mention
    "story",    # Success story format
    "question", # Ask community, mention tool in comments
]


def generate_post(post_type: str) -> dict:
    """Use Claude to generate a Reddit post."""
    prompts = {
        "tip": """Write a helpful Reddit post for r/dating_advice.
Give genuine, specific dating texting advice. At the end, casually mention:
"I've also been using this AI tool called askrizz.com that suggests replies -
surprisingly helpful for when you're overthinking what to text."
Keep it natural, not salesy. 200-300 words. Return JSON: {"title": "...", "body": "..."}""",

        "story": """Write a Reddit post for r/dating about a positive texting experience.
The story: person was stuck on what to reply, used an AI tool (askrizz.com),
got a great suggestion, conversation went well, got a date.
Make it feel real and relatable, not an ad. Include specific details.
200-300 words. Return JSON: {"title": "...", "body": "..."}""",

        "question": """Write a Reddit post for r/OnlineDating asking for texting advice.
Include a realistic conversation snippet where you're stuck.
Make it genuine - people should want to help.
150-200 words. Return JSON: {"title": "...", "body": "..."}
Note: Do NOT mention askrizz.com in the post - we'll mention it in a comment later.""",
    }

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system="You write authentic Reddit posts. No marketing speak. Sound like a real person.",
        messages=[{"role": "user", "content": prompts[post_type]}]
    )

    import json, re
    raw = response.content[0].text.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def post_to_reddit(subreddit_name: str, title: str, body: str, add_comment: bool = False):
    """Post to a subreddit."""
    try:
        sub = reddit.subreddit(subreddit_name)
        post = sub.submit(title=title, selftext=body)
        print(f"  Posted to r/{subreddit_name}: {post.url}")

        if add_comment:
            time.sleep(30)  # Wait before commenting
            comment_text = (
                "Update: I actually tried this AI tool called askrizz.com "
                "that suggests replies based on the conversation. "
                "Got some surprisingly good suggestions. Worth a try if you're stuck like me."
            )
            post.reply(comment_text)
            print(f"  Added comment with product mention")

        return post.url
    except Exception as e:
        print(f"  Error posting to r/{subreddit_name}: {e}")
        return None


def daily_run():
    """Run daily posting routine."""
    print(f"Reddit Bot — Daily Run")
    print(f"=" * 40)

    # Pick random subreddit and post type
    subreddit = random.choice(SUBREDDITS)
    post_type = random.choice(POST_TYPES)

    print(f"  Subreddit: r/{subreddit}")
    print(f"  Post type: {post_type}")

    # Generate post
    print(f"  Generating post...")
    post_data = generate_post(post_type)
    print(f"  Title: {post_data['title']}")

    # Post it
    add_comment = (post_type == "question")
    url = post_to_reddit(subreddit, post_data["title"], post_data["body"], add_comment)

    if url:
        print(f"\n  SUCCESS: {url}")
    else:
        print(f"\n  FAILED")


if __name__ == "__main__":
    daily_run()
