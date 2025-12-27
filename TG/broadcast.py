# TG/broadcast.py


import os
import sqlite3
import asyncio
from contextlib import closing
from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid

from bot import Bot, ADMINS

DB = os.getenv("BROADCAST_DB", "broadcast.db")
SLEEP_BETWEEN = float(os.getenv("BROADCAST_SLEEP", "0.05"))


# ------------------ Database ------------------
def _init_db():
    con = sqlite3.connect(DB, check_same_thread=False)
    with closing(con.cursor()) as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
        con.commit()
    return con

CON = _init_db()


def add_user(uid: int):
    with closing(CON.cursor()) as cur:
        cur.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (uid,))
        CON.commit()


def get_users():
    with closing(CON.cursor()) as cur:
        cur.execute("SELECT user_id FROM users")
        return [r[0] for r in cur.fetchall()]


def del_user(uid: int):
    with closing(CON.cursor()) as cur:
        cur.execute("DELETE FROM users WHERE user_id=?", (uid,))
        CON.commit()


# ------------------ Auto-save users ------------------
@Bot.on_message(filters.private & ~filters.service)
async def save_users(_, msg):
    if msg.from_user:
        add_user(msg.from_user.id)


# ------------------ Helpers ------------------
def strip_outer_quotes(s: str) -> str:
    s = (s or "").strip()
    if len(s) >= 2:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1].strip()
    return s


def ui_header(total: int) -> str:
    return (
        f"📣 ᴮʀᴏᴀᴅᴄᴀsᴛ ᴘᴀɴᴇʟ\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 Targets: `{total}`\n"
        f"🧾 Mode: Copy reply / Send text\n"
        f"━━━━━━━━━━━━━━━━━━"
    )


def ui_progress(total: int, sent: int, failed: int, removed: int) -> str:
    return (
        f"📣 ᴮʀᴏᴀᴅᴄᴀsᴛɪɴɢ...\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total: `{total}`\n"
        f"✅ Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`\n"
        f"🗑 Removed: `{removed}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⏳ Please wait..."
    )


def ui_done(total: int, sent: int, failed: int, removed: int) -> str:
    return (
        f"✅ ᴮʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total: `{total}`\n"
        f"✅ Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`\n"
        f"🗑 Removed: `{removed}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✨ Done!"
    )


# ------------------ Command: /broadcast ------------------
@Bot.on_message(filters.command(["broadcast", "b"]) & filters.user(ADMINS))
async def broadcast_cmd(client, msg):
    users = get_users()
    total = len(users)

    if total == 0:
        return await msg.reply_text("❌ No users found.\n\nTip: Users must /start the bot first.")

    text_payload = None
    if not msg.reply_to_message:
        if len(msg.command) == 1:
            return await msg.reply_text(
                "❌ Usage:\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "• `/broadcast Hello`\n"
                "• `/broadcast \"Hello\"`\n"
                "• Or reply to any message/media and use `/broadcast`\n"
                "━━━━━━━━━━━━━━━━━━"
            )
        raw = msg.text.split(None, 1)[1]
        text_payload = strip_outer_quotes(raw)

        if not text_payload:
            return await msg.reply_text("❌ Empty text not allowed.")

    status = await msg.reply_text(ui_header(total))

    sent = failed = removed = 0
    last_edit = 0.0

    for uid in users:
        try:
            if msg.reply_to_message:
                await msg.reply_to_message.copy(uid)
            else:
                await client.send_message(uid, text_payload)

            sent += 1
            await asyncio.sleep(SLEEP_BETWEEN)

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

        now = asyncio.get_event_loop().time()
        if now - last_edit >= 3:
            last_edit = now
            try:
                await status.edit_text(ui_progress(total, sent, failed, removed))
            except Exception:
                pass

    try:
        await status.edit_text(ui_done(total, sent, failed, removed))
    except Exception:
        await msg.reply_text(ui_done(total, sent, failed, removed))
