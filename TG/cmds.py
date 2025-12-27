from bot import Bot, get_logger, PICS
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .help import wait_flood, load_fsb_vars, check_fsb, split_list
import random
import time 


log = get_logger(__name__)


  
@Bot.on_message(filters.private)
async def on_private_message(client, message):
  channel = client.setting["FORCE_SUB_CHANNEL"]
  if channel in ["None", None, "none", "OFF", False, "False", ""]:
    return message.continue_propagation()
  
  if not client.FSB or client.FSB == []:
    load_fsb_vars(client)
    return message.continue_propagation()

  channel_button, change_data = await check_fsb(client, message)
  if not channel_button:
    return message.continue_propagation()

  channel_button = split_list(channel_button)
  channel_button.append(
      [InlineKeyboardButton("𝗥𝗘𝗙𝗥𝗘𝗦𝗛 ⟳", callback_data="refresh")])

  await wait_flood(message.reply_photo)(
      caption=client.setting["FORCE_SUB_TEXT"],
      photo=random.choice(PICS),
      reply_markup=InlineKeyboardMarkup(channel_button),
      quote=True,
  )
  
  if change_data:
    for change_ in change_data:
      client.FSB[change_[0]] = (change_[1], change_[2], change_[3])


@Bot.on_message(filters.command("start"))
async def start(client, message):
  txt_ = """
<blockquote>**Hello, I am a bot that can check the uptime of your website.
like an unseen guardian in the background.
I stay awake — watching your website.**
<b>Ping: {}</b></blockquote>"""
  try:
    xt_ = time.time() - client.ping
    check_time_ = time.strftime("%Hh %Mm %Ss", time.gmtime(xt_))
    txt_ = txt_.format(check_time_)
  except:
    txt_ = txt_.format("0")
  
  button = [
      [
          InlineKeyboardButton("🌐 Check Uptime", callback_data="check_uptime"),
          InlineKeyboardButton("📊 Stats", callback_data="stats"),
      ],
      [
          InlineKeyboardButton("📚 Help", callback_data="help"),
          InlineKeyboardButton("📢 Channel", url="https://t.me/Wizard_Bots"),
      ],
  ]
  if message.from_user.id in Bot.setting["ADMINS"]:
    button.append([InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")])
  
  return await wait_flood(message.reply_photo)(
    random.choice(PICS),
    caption=txt_, 
    reply_markup=InlineKeyboardMarkup(button), 
    quote=True
  )

@Bot.on_message(filters.command("status"))
async def status(client, message):
  return await wait_flood(message.reply_photo)(
    random.choice(PICS),
    caption="<blockquote><b><i>Check Through Below Buttons</i></b></blockquote>",
    reply_markup=InlineKeyboardMarkup([
      [InlineKeyboardButton("🌐 Check Uptime", url=client.msg.link)],
      [
        InlineKeyboardButton("🏠 Home", callback_data="start"),
        InlineKeyboardButton(" Close ", callback_data="close")
      ]
    ])
  )
