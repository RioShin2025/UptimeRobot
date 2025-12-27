# TG/users.py
import os
import sqlite3
from contextlib import closing
from io import BytesIO
from pyrogram import filters

from bot import Bot, ADMINS

DB = os.getenv("BROADCAST_DB", "broadcast.db")


def _get_users():
    if not os.path.exists(DB):
        return []
    con = sqlite3.connect(DB, check_same_thread=False)
    with closing(con.cursor()) as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
        con.commit()
        cur.execute("SELECT user_id FROM users ORDER BY user_id ASC")
        rows = cur.fetchall()
    con.close()
    return [r[0] for r in rows]


@Bot.on_message(filters.command(["users", "exportusers"]) & filters.user(ADMINS))
async def users_export_cmd(_, msg):
    users = _get_users()
    if not users:
        return await msg.reply_text("❌ No users found yet.\nTip: Users must /start the bot first.")

    text = "\n".join(str(u) for u in users)
    bio = BytesIO(text.encode("utf-8"))
    bio.name = f"users_{len(users)}.txt"

    await msg.reply_document(
        bio,
        caption=f"✅ Exported **{len(users)}** users."
    )
