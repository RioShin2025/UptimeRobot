# TG/restart.py
import os
import sys
import asyncio
from pyrogram import filters

from bot import Bot, ADMINS


@Bot.on_message(filters.command(["restart", "reboot"]) & filters.user(ADMINS))
async def restart_cmd(_, msg):
    m = await msg.reply_text("<blockquote>♻️ ʀᴇsᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ... 👾<blockquote>")

    # Give Telegram time to send the message
    await asyncio.sleep(1.5)

    # Try graceful stop (optional)
    try:
        await Bot.stop()
    except Exception:
        pass

    # On Render, exiting makes the service start again automatically
    os._exit(0)
