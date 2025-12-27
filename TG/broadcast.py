# TG/broadcast.py
import asyncio
from pyrogram import filters
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
    PeerIdInvalid,
    ChatAdminRequired
)

# This file expects:
# Bot  -> Pyrogram Client
# Vars.ADMINS -> list of admin IDs
# uts -> dict of users {"123456": True}
# sync() -> function that saves uts

async def borad_cast_(_, message, pin=False, forward=False):

    def del_users(user_id):
        try:
            user_id = str(user_id)
            if user_id in uts:
                del uts[user_id]
                sync()
        except Exception:
            pass

    user_ids = list(uts.keys())
    if not user_ids:
        return await message.reply_text("❌ No users in DB.")

    text = None
    if not message.reply_to_message:
        if len(message.command) > 1:
            text = message.text.split(None, 1)[1]
        else:
            return await message.reply_text(
                "❌ Reply to a message and use /pbroadcast\n"
                "OR use: `/broadcast your text`"
            )

    status = await message.reply_text(f"📣 Sending to **{len(user_ids)}** users...")

    sent, failed, removed, pinned = 0, 0, 0, 0

    for uid_str in user_ids:
        uid = int(uid_str)
        try:
            sent_msg = None

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
                except ChatAdminRequired:
                    pass
                except Exception:
                    pass

            await asyncio.sleep(0.05)

        except FloodWait as e:
            await asyncio.sleep(int(e.value) + 1)

        except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):
            failed += 1
            del_users(uid_str)
            removed += 1

        except Exception:
            failed += 1
            del_users(uid_str)
            removed += 1

    return await status.edit_text(
        f"✅ Broadcast Done!\n\n"
        f"👥 Total: {len(user_ids)}\n"
        f"✅ Sent: {sent}\n"
        f"📌 Pinned: {pinned}\n"
        f"❌ Failed: {failed}\n"
        f"🗑 Removed: {removed}"
    )


def load_broadcast_cmds(Bot, Vars, uts, sync):

    @Bot.on_message(filters.command(["broadcast", "b"]) & filters.user(Vars.ADMINS))
    async def b_handler(_, msg):
        return await borad_cast_(_, msg)

    @Bot.on_message(filters.command(["pbroadcast", "pb"]) & filters.user(Vars.ADMINS))
    async def pb_handler(_, msg):
        return await borad_cast_(_, msg, pin=True)

    @Bot.on_message(filters.command(["forward", "fd"]) & filters.user(Vars.ADMINS))
    async def fb_handler(_, msg):
        return await borad_cast_(_, msg, forward=True)

    @Bot.on_message(filters.command(["pforward", "pfd"]) & filters.user(Vars.ADMINS))
    async def pfb_handler(_, msg):
        return await borad_cast_(_, msg, pin=True, forward=True)
