import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8850549911:AAHqZIAtvGhsojpwjnA5he0icMp8MHhJzvI")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "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")  # Optional for higher rate limits

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")
