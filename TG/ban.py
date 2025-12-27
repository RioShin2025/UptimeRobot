# TG/ban.py
import os
import sqlite3
from contextlib import closing
from pyrogram import filters
from pyrogram.errors import RPCError
from pyrogram import StopPropagation

from bot import Bot, ADMINS

BAN_DB = os.getenv("BAN_DB", "ban.db")


def _con():
    con = sqlite3.connect(BAN_DB, check_same_thread=False)
    with closing(con.cursor()) as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS banned (user_id INTEGER PRIMARY KEY)")
        con.commit()
    return con

CON = _con()


def ban_user(user_id: int):
    with closing(CON.cursor()) as cur:
        cur.execute("INSERT OR IGNORE INTO banned (user_id) VALUES (?)", (user_id,))
        CON.commit()


def unban_user(user_id: int):
    with closing(CON.cursor()) as cur:
        cur.execute("DELETE FROM banned WHERE user_id=?", (user_id,))
        CON.commit()


def is_banned(user_id: int) -> bool:
    with closing(CON.cursor()) as cur:
        cur.execute("SELECT 1 FROM banned WHERE user_id=? LIMIT 1", (user_id,))
        return cur.fetchone() is not None


def _extract_user_id(msg):
    # 1) reply ban
    if msg.reply_to_message and msg.reply_to_message.from_user:
        return msg.reply_to_message.from_user.id

    # 2) /ban 123456
    if len(msg.command) > 1 and msg.command[1].lstrip("-").isdigit():
        return int(msg.command[1])

    return None


# 🔒 BLOCK banned users BEFORE other handlers
@Bot.on_message(filters.private & ~filters.service, group=-1)
async def ban_gate(_, msg):
    if msg.from_user and is_banned(msg.from_user.id):
        try:
            await msg.reply_text("🚫 sᴏʀʀʏ ᴍᴀɴ,ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.")
        except RPCError:
            pass
        raise StopPropagation


@Bot.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_cmd(_, msg):
    uid = _extract_user_id(msg)
    if not uid:
        return await msg.reply_text("Usage:\n• Reply to a user: `/ban`\n• Or: `/ban <user_id>`")

    if uid in ADMINS:
        return await msg.reply_text("❌ Can't ban an admin.")

    ban_user(uid)
    await msg.reply_text(f"✅ ʙᴀɴɴᴇᴅ: `{uid}`")


@Bot.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_cmd(_, msg):
    uid = _extract_user_id(msg)
    if not uid:
        return await msg.reply_text("Usage:\n• Reply to a user: `/unban`\n• Or: `/unban <user_id>`")

    unban_user(uid)
    await msg.reply_text(f"✅ ᴜɴʙᴀɴɴᴇᴅ: `{uid}`")


@Bot.on_message(filters.command(["banned", "banlist"]) & filters.user(ADMINS))
async def banlist_cmd(_, msg):
    with closing(CON.cursor()) as cur:
        cur.execute("SELECT user_id FROM banned ORDER BY user_id ASC")
        rows = cur.fetchall()

    if not rows:
        return await msg.reply_text("✅ Ban list is empty.")

    text = "\n".join(str(r[0]) for r in rows[:2000])
    await msg.reply_text(f"🚫 **Banned users:**\n\n`{text}`")
