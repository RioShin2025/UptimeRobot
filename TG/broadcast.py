import os
import sqlite3
import asyncio
from contextlib import closing
from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid, ChatAdminRequired

# Import your Bot client + ADMINS from bot.py
from bot import Bot, ADMINS

DB = os.getenv("BROADCAST_DB", "broadcast.db")

def _con():
    con = sqlite3.connect(DB, check_same_thread=False)
    with closing(con.cursor()) as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
        con.commit()
    return con

CON = _con()

def add_user(user_id: int):
    with closing(CON.cursor()) as cur:
        cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        CON.commit()

def all_users():
    with closing(CON.cursor()) as cur:
        cur.execute("SELECT user_id FROM users")
        return [x[0] for x in cur.fetchall()]

def del_user(user_id: int):
    with closing(CON.cursor()) as cur:
        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        CON.commit()

@Bot.on_message(filters.private & ~filters.service)
async def _track(_, msg):
    if msg.from_user:
        add_user(msg.from_user.id)

async def _send_all(_, message, pin=False, forward=False):
    users = all_users()
    if not users:
        return await message.reply_text("❌ No users saved yet.")

    text = None
    if not message.reply_to_message:
        if len(message.command) > 1:
            text = message.text.split(None, 1)[1]
        else:
            return await message.reply_text(
                "❌ Reply to a message and use /pbroadcast\n"
                "OR use: `/broadcast your text`"
            )

    status = await message.reply_text(f"📣 Sending to **{len(users)}** users...")

    sent = failed = removed = pinned = 0

    for uid in users:
        try:
            if forward and message.reply_to_message:
                sent_msg = await message.reply_to_message.forward(chat_id=uid)
            elif message.reply_to_message:
                sent_msg = await message.reply_to_message.copy(chat_id=uid)
            else:
                sent_msg = await _.send_message(uid, text)

            sent += 1

            if pin and sent_msg:
                try:
                    await _.pin_chat_message(uid, sent_msg.id, disable_notification=True)
                    pinned += 1
                except (ChatAdminRequired, Exception):
                    pass

            await asyncio.sleep(0.05)

        except FloodWait as e:
            await asyncio.sleep(int(e.value) + 1)
        except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):
            failed += 1
            del_user(uid)
            removed += 1
        except Exception:
            failed += 1
            del_user(uid)
            removed += 1

    return await status.edit_text(
        f"✅ Done!\n\n"
        f"👥 Total: {len(users)}\n"
        f"✅ Sent: {sent}\n"
        f"📌 Pinned: {pinned}\n"
        f"❌ Failed: {failed}\n"
        f"🗑 Removed: {removed}"
    )

@Bot.on_message(filters.command(["broadcast", "b"]) & filters.user(ADMINS))
async def broadcast_cmd(_, msg):
    return await _send_all(_, msg)

@Bot.on_message(filters.command(["pbroadcast", "pb"]) & filters.user(ADMINS))
async def pbroadcast_cmd(_, msg):
    return await _send_all(_, msg, pin=True)

@Bot.on_message(filters.command(["forward", "fd"]) & filters.user(ADMINS))
async def forward_cmd(_, msg):
    return await _send_all(_, msg, forward=True)

@Bot.on_message(filters.command(["pforward", "pfd"]) & filters.user(ADMINS))
async def pforward_cmd(_, msg):
    return await _send_all(_, msg, pin=True, forward=True)
