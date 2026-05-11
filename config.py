"""
config.py — All environment variables in one place.
Copy sample.env → .env and fill in your values.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Required ──────────────────────────────────────────────────────────────────
API_ID          = int(os.environ["API_ID"])
API_HASH        = os.environ["API_HASH"]
BOT_TOKEN       = os.environ["BOT_TOKEN"]
STRING_SESSION  = os.environ["STRING_SESSION"]
MONGO_DB_URL    = os.environ["MONGO_DB_URL"]
OWNER_ID        = int(os.environ["OWNER_ID"])

# ── Optional ──────────────────────────────────────────────────────────────────
BOT_NAME         = os.getenv("BOT_NAME", "KRISH X STAR CODER MUSIC")
BOT_LINK         = os.getenv("BOT_LINK", "https://t.me/KRISHXSTAR_MUSIC_BOT")
UPDATES_CHANNEL  = os.getenv("UPDATES_CHANNEL", "https://t.me/KRISH_HACKER_OP")
SUPPORT_GROUP    = os.getenv("SUPPORT_GROUP", "https://t.me/KRISH_HACKER_OP")
LOGGER_ID        = int(os.getenv("LOGGER_ID", "0"))
START_ANIMATION  = os.getenv("START_ANIMATION", "https://telegra.ph/file/your_custom_animation.mp4")
PING_IMG_URL     = os.getenv("PING_IMG_URL", "https://telegra.ph/file/your_custom_ping.jpg")
SESSION_NAME     = os.getenv("SESSION_NAME", "KRISHXSTAR_MUSIC")
PORT             = int(os.getenv("PORT", 10000))

# ── Limits ────────────────────────────────────────────────────────────────────
MAX_DURATION_SECONDS = 1800   # 30 minutes
QUEUE_LIMIT          = 20
COOLDOWN             = 10     # seconds between /play per chat
