# TG/users.py
import os
import sqlite3
from contextlib import closing
from io import BytesIO
from pyrogram import filters

from bot import Bot, ADMINS

DB = os.getenv("BROADCAST_DB", "broadcast.db")

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    con = sqlite3.connect(DB, check_same_thread=False)
    with closing(con.cursor()) as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
        con.commit()
    con.close()

# Initialize on module load
init_db()

def add_user(user_id: int):
    """Adds a new user to the broadcast database."""
    with sqlite3.connect(DB) as con:
        with closing(con.cursor()) as cur:
            cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            con.commit()

def _get_users():
    """Retrieves all user IDs from the database."""
    if not os.path.exists(DB):
        return []
    with sqlite3.connect(DB) as con:
        with closing(con.cursor()) as cur:
            cur.execute("SELECT user_id FROM users ORDER BY user_id ASC")
            rows = cur.fetchall()
    return [r[0] for r in rows]

@Bot.on_message(filters.command(["users", "exportusers"]) & filters.user(ADMINS))
async def users_export_cmd(_, msg):
    users = _get_users()
    if not users:
        return await msg.reply_text("❌ No users found yet.\nTip: Users must /start the bot first.")

    # Creating the export file in memory
    text = "\n".join(str(u) for u in users)
    bio = BytesIO(text.encode("utf-8"))
    bio.name = f"users_{len(users)}.txt"

    await msg.reply_document(
        bio,
        caption=f"✅ Exported **{len(users)}** unique users."
    )

