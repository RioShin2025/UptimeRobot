import pyrogram
from pyrogram.errors import FloodWait
import asyncio
from pyrogram.types import InlineKeyboardButton
import pyrogram.errors


def wait_flood(func):

    async def wrapper(*args, **kwargs):
        while True:
            try:
                await asyncio.sleep(0.5)
                return await func(*args, **kwargs)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                return await func(*args, **kwargs)

    return wrapper


def split_list(li, lens: int = 2):
    return [li[x:x + lens] for x in range(0, len(li), lens)]


async def iterable_to_list(data: dict, page: int = 1):
    """Simple paginated uptime display"""

    items = list(data.items())
    start = (page - 1) * 10
    page_data = items[start:start + 10]
    if not page_data:
        return None
    
    buttons = []
    txt_ = f"**UPTIME INFO (Page {page})**\n\n"
    txt_ += "<blockquote expandable>"
    for i, (url, info) in enumerate(page_data, 1):
        icon = "🟢" if info.get('status') else "🔴"
        txt_ += f"{i}. {icon} {url}\n"

        original_idx = items.index((url, info))
        buttons.append(
            InlineKeyboardButton(str(i), callback_data=f"info_{original_idx}"))
    txt_ += "</blockquote>"

    return txt_, split_list(buttons, 4) if buttons else None


def load_fsb_vars(self):
  channel = self.setting["FORCE_SUB_CHANNEL"]
  try:
    if "," in channel:
      for channel_line in channel.split(","):
        self.FSB.append(
          (channel_line.split(":")[0], channel_line.split(":")[1])
        )
    else:
      self.FSB.append((channel.split(":")[0], channel.split(":")[1]))
  except:
    pass

async def check_fsb(client, message):
    channel_button = []
    change_data = []

    for index, channel_information in enumerate(client.FSB):
        try:
            channel = int(channel_information[1])
        except:
            channel = str(channel_information[1])

        try:
            await client.get_chat_member(channel, message.from_user.id)
        except pyrogram.errors.UsernameNotOccupied:
            pass
        except pyrogram.errors.ChatAdminRequired:
            pass

        except pyrogram.errors.UserNotParticipant:
            try:
                channel_link = channel_information[2]
            except:
                if isinstance(channel, int):
                    channel_link = await client.export_chat_invite_link(channel
                                                                        )
                else:
                    channel_link = f"https://telegram.me/{channel.strip()}"

            channel_button.append(
                InlineKeyboardButton(channel_information[0], url=channel_link))
            if len(channel_information) == 2:
                change_data.append((index, channel_information[0],
                                    channel_information[1], channel_link))

        except pyrogram.ContinuePropagation:
            raise
        except pyrogram.StopPropagation:
            raise
        except BaseException as e:
            pass

    return channel_button, change_data