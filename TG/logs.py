# TG/logs.py
import os
from io import BytesIO
from pyrogram import filters

from bot import Bot, ADMINS

LOG_FILE = "app.log"


def tail_lines(path: str, lines: int = 200) -> str:
    """Read last N lines from a text file safely."""
    if not os.path.exists(path):
        return ""

    # Simple + safe (file is not huge usually). Good for Render.
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.readlines()
    return "".join(data[-lines:])


@Bot.on_message(filters.command(["logs", "log"]) & filters.user(ADMINS))
async def logs_cmd(_, msg):
    # usage:
    # /logs            -> last 200 lines
    # /logs 500        -> last 500 lines
    n = 200
    if len(msg.command) > 1 and msg.command[1].isdigit():
        n = max(50, min(2000, int(msg.command[1])))

    text = tail_lines(LOG_FILE, n)

    if not text:
        return await msg.reply_text(
            f"❌ `{LOG_FILE}` not found or empty.\n"
            f"Tip: make sure FileHandler writes to `{LOG_FILE}`."
        )

    # If small, send as message. If large, send as file.
    if len(text) <= 3800:
        return await msg.reply_text(f"**📄 Last {n} lines from {LOG_FILE}:**\n\n`{text}`")

    bio = BytesIO(text.encode("utf-8", errors="ignore"))
    bio.name = f"logs_last_{n}.txt"
    await msg.reply_document(bio, caption=f"📄 Last {n} lines from {LOG_FILE}")
