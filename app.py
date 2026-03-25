from flask import Flask, request, jsonify, render_template
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are Rizz AI — the world's best dating conversation coach.

Your job: analyze a dating conversation and give 3 perfect reply options.

Each reply must be:
- Natural, not cringe, not try-hard
- Match the vibe of the conversation
- Actually work in real life

Always return a JSON object exactly like this:
{
  "analysis": "One sentence reading the vibe of this conversation",
  "replies": [
    {
      "style": "Playful",
      "emoji": "😏",
      "text": "the actual message to send",
      "why": "why this works (one short sentence)"
    },
    {
      "style": "Confident",
      "emoji": "🔥",
      "text": "the actual message to send",
      "why": "why this works (one short sentence)"
    },
    {
      "style": "Witty",
      "emoji": "😂",
      "text": "the actual message to send",
      "why": "why this works (one short sentence)"
    }
  ]
}

Rules:
- Replies must be short (1-2 sentences max), like real texts
- No emojis inside the reply text unless it genuinely fits
- Never be generic. Read the actual conversation.
- Return ONLY the JSON, no other text."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    conversation = data.get("conversation", "").strip()
    context = data.get("context", "").strip()

    if not conversation or len(conversation) < 10:
        return jsonify({"error": "Paste a real conversation first"}), 400

    user_msg = f"Conversation:\n{conversation}"
    if context:
        user_msg += f"\n\nContext: {context}"

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}]
        )
        import json, re
        raw = response.content[0].text.strip()
        # Strip markdown code blocks if present
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        result = json.loads(raw)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    app.run(debug=False, host="0.0.0.0", port=port)
