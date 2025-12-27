import asyncio
import time
from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import Bot, ADMINS, get_logger
from .users import _get_users

log = get_logger(__name__)

# Global flag for cancellation
CANCEL_BROADCAST = False

def parse_time(time_str):
    """Parses 10s, 10m, 10h into seconds."""
    unit = time_str[-1].lower()
    try:
        value = int(time_str[:-1])
        if unit == 's': return value
        if unit == 'm': return value * 60
        if unit == 'h': return value * 3600
    except:
        return None

async def delete_after(chat_id, message_id, delay):
    """Background task to delete a message after a delay."""
    await asyncio.sleep(delay)
    try:
        await Bot.delete_messages(chat_id, message_id)
    except:
        pass

@Bot.on_callback_query(filters.regex("^cancel_broadcast$"))
async def cancel_broadcast_cb(_, query):
    global CANCEL_BROADCAST
    CANCEL_BROADCAST = True
    await query.answer("🛑 Stopping broadcast...", show_alert=True)

@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_handler(client, message):
    global CANCEL_BROADCAST
    CANCEL_BROADCAST = False

    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to a message to broadcast it.")

    args = message.text.split()
    do_pin = "pin" in args
    do_forward = "f" in args
    
    # Extract time delay if present
    deletion_delay = None
    for arg in args:
        if any(u in arg for u in ['s', 'm', 'h']) and arg[-1].lower() in ['s', 'm', 'h']:
            deletion_delay = parse_time(arg)

    users = _get_users()
    if not users:
        return await message.reply_text("❌ No users found in database.")

    status_msg = await message.reply_text("🚀 **Initializing Broadcast...**")
    
    count, blocked, deleted, failed = 0, 0, 0, 0
    total = len(users)
    cancel_markup = InlineKeyboardMarkup([[InlineKeyboardButton("✖️ Cancel Broadcast", callback_data="cancel_broadcast")]])

    for user_id in users:
        if CANCEL_BROADCAST:
            break

        try:
            # Send logic
            if do_forward:
                sent = await message.reply_to_message.forward(user_id)
            else:
                sent = await message.reply_to_message.copy(user_id)

            # Pin logic
            if do_pin:
                try: await sent.pin(both_sides=False)
                except: pass

            # Auto-delete logic
            if deletion_delay:
                asyncio.create_task(delete_after(user_id, sent.id, deletion_delay))

            count += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except UserIsBlocked:
            blocked += 1
        except InputUserDeactivated:
            deleted += 1
        except Exception:
            failed += 1

        # Progress update every 10 users
        if count % 10 == 0 or count == total:
            percentage = (count / total) * 100
            # Visual Progress Bar
            filled = int(percentage // 10)
            bar = "🟢" * filled + "⚪" * (10 - filled)
            
            progress_text = (
                f"<blockquote>📢 **Broadcasting...**\n"
                f"{bar} `{percentage:.1f}%`</blockquote>\n"
                f"✅ **Sent:** `{count}`\n"
                f"🚫 **Blocked:** `{blocked}`\n"
                f"⚠️ **Failed:** `{failed + deleted}`"
            )
            try: await status_msg.edit_text(progress_text, reply_markup=cancel_markup)
            except: pass

    final_status = "✅ **Completed**" if not CANCEL_BROADCAST else "🛑 **Cancelled**"
    await status_msg.edit_text(
        f"<blockquote>{final_status}</blockquote>\n"
        f"📊 **Total:** `{total}`\n"
        f"📤 **Sent:** `{count}`\n"
        f"🚫 **Blocked:** `{blocked}`\n"
        f"⚠️ **Failed:** `{failed + deleted}`"
    )
