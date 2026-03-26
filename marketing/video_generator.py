"""
Rizz AI — AI Video Generator
Creates TikTok/Reels marketing videos.

Pipeline:
1. Claude writes a hook script
2. Generate screen recording simulation (HTML → screenshot sequence)
3. FFmpeg assembles into video with text overlays

Requirements: pip install Pillow
Optional: ffmpeg installed for video assembly

Output: marketing/videos/rizz_video_YYYY-MM-DD_N.mp4
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
VIDEO_DIR = os.path.join(os.path.dirname(__file__), "videos")
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

HOOKS = [
    "She left you on read? Watch this.",
    "He said 'lol thanks' and you froze? Here's what to say.",
    "Stuck on what to text back? AI has your answer.",
    "This AI writes better texts than you. Sorry.",
    "3 replies for any conversation. In 2 seconds.",
    "When you've been typing for 10 minutes... just use AI.",
    "Your crush texted. You panicked. AI didn't.",
    "POV: AI writes your texts and she actually replies.",
    "Stop overthinking. Start rizzing.",
    "The text that got her to say yes to a date.",
]

SAMPLE_CONVERSATIONS = [
    {
        "messages": [
            {"from": "her", "text": "omg I literally just got back from the worst day ever"},
            {"from": "you", "text": "lol what happened"},
            {"from": "her", "text": "don't even ask 😭"},
        ],
        "context": "Hinge match, 3 days talking"
    },
    {
        "messages": [
            {"from": "her", "text": "thanks for dinner last night!"},
            {"from": "you", "text": "of course! I had a great time"},
            {"from": "her", "text": "me too 😊"},
        ],
        "context": "Second date, going well"
    },
    {
        "messages": [
            {"from": "her", "text": "so what do you do for fun"},
            {"from": "you", "text": "hmm a lot of things actually"},
            {"from": "her", "text": "like what lol"},
        ],
        "context": "Bumble match, first conversation"
    },
    {
        "messages": [
            {"from": "her", "text": "I'm so bored rn"},
            {"from": "you", "text": "same honestly"},
            {"from": "her", "text": "entertain me then"},
        ],
        "context": "Tinder match, she's testing you"
    },
    {
        "messages": [
            {"from": "him", "text": "hey what are you up to this weekend"},
            {"from": "you", "text": "not sure yet, why?"},
            {"from": "him", "text": "was thinking we could grab coffee or something"},
        ],
        "context": "Guy from class asked you out"
    },
]


def generate_script() -> dict:
    """Generate a TikTok video script."""
    import random
    hook = random.choice(HOOKS)
    convo = random.choice(SAMPLE_CONVERSATIONS)

    # Get AI replies for this conversation
    convo_text = "\n".join(f"{'Her' if m['from']=='her' else 'Him' if m['from']=='him' else 'You'}: {m['text']}" for m in convo["messages"])

    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system="""You are Rizz AI. Analyze this conversation and give 3 reply options.
Return JSON: {"analysis": "...", "replies": [{"style": "Playful", "text": "..."}, {"style": "Confident", "text": "..."}, {"style": "Witty", "text": "..."}]}""",
        messages=[{"role": "user", "content": f"Conversation:\n{convo_text}\nContext: {convo['context']}"}]
    )

    import re
    raw = response.content[0].text.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    ai_result = json.loads(raw)

    script = {
        "hook": hook,
        "conversation": convo,
        "ai_replies": ai_result,
        "cta": "askrizz.com — 3 free tries",
        "generated_at": datetime.now().isoformat(),
    }

    # Save script
    filename = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(SCRIPTS_DIR, filename), "w") as f:
        json.dump(script, f, indent=2)

    print(f"  Script generated: {filename}")
    print(f"  Hook: {hook}")
    print(f"  Replies: {[r['text'][:40] for r in ai_result.get('replies', [])]}")

    return script


def generate_video() -> str:
    """Generate a complete video script + storyboard."""
    print("Generating video content...")
    script = generate_script()

    # Create storyboard (text-based for now)
    storyboard = f"""
RIZZ AI — TikTok Video Storyboard
===================================

HOOK (0-3 sec):
  Text on screen: "{script['hook']}"
  Background: Dark, phone mockup

CONVERSATION (3-10 sec):
  Show chat bubbles appearing one by one:
"""
    for m in script["conversation"]["messages"]:
        side = "RIGHT (blue)" if m["from"] == "you" else "LEFT (gray)"
        storyboard += f"    [{side}] {m['text']}\n"

    storyboard += f"""
PASTE INTO RIZZ AI (10-15 sec):
  Screen: askrizz.com
  Action: Paste conversation, click "Get My Rizz"
  Loading animation...

AI REPLIES (15-22 sec):
  Show 3 cards appearing:
"""
    for r in script["ai_replies"].get("replies", []):
        storyboard += f"    {r.get('style', '?')}: \"{r['text']}\"\n"

    storyboard += f"""
CTA (22-25 sec):
  Text: "{script['cta']}"
  Big text: "Link in bio"

CAPTION:
  {script['hook']} #rizz #datingadvice #texting #ai #rizzai
"""

    # Save storyboard
    filename = f"storyboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(VIDEO_DIR, filename)
    with open(filepath, "w") as f:
        f.write(storyboard)

    print(f"  Storyboard saved: {filepath}")
    return filepath


if __name__ == "__main__":
    generate_video()
