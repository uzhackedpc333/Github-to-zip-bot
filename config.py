import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Optional for higher rate limits

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")
