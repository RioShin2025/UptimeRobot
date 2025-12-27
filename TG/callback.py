import asyncio

from bot import Bot, get_logger, PICS
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from .help import split_list, wait_flood, iterable_to_list, load_fsb_vars, check_fsb
import random

import time, psutil, platform, shutil, os

from Tools.db import db_sync, uts_

log = get_logger(__name__)

@Bot.on_callback_query(filters.regex("^refresh$"))
async def refresh_handler(_, query):
  if not _.FSB or _.FSB == []:
    await wait_flood(query.answer
                         )(" <blockquote>✅ Thanks for joining! You can now use the bot. </blockquote>",
                           show_alert=True)
    return await wait_flood(query.message.delete)()

  channel_button, change_data = await check_fsb(_, query)
  if not channel_button:
    await wait_flood(query.answer
                         )(" <blockquote>✅ Thanks for joining! You can now use the bot.</blockquote> ",
                           show_alert=True)
    return await wait_flood(query.message.delete)()

  channel_button = split_list(channel_button)
  channel_button.append(
      [InlineKeyboardButton("ʀᴇғʀᴇsʜ ⟳", callback_data="refresh")])

  try:
    await wait_flood(query.edit_message_media)(
        media=InputMediaPhoto(random.choice(PICS),
                              caption=_.setting["FORCE_SUB_TEXT"]),
        reply_markup=InlineKeyboardMarkup(channel_button),
    )
  except:
    await wait_flood(query.answer)("You're still not in the channel.")

  if change_data:
    for change_ in change_data:
      _.FSB[change_[0]] = (change_[1], change_[2], change_[3])


@Bot.on_callback_query(filters.regex("^start$"))
async def start_callback(client, query):
  txt_ = """
<b>Hello, I am a bot that can check the uptime of your website.</b>

<b>Ping: {}</b>"""
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
      [
          InlineKeyboardButton(" Close ", callback_data="close"),
      ],
  ]
  if query.from_user.id in Bot.setting["ADMINS"]:
    button.append(
        [InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")])

  return await wait_flood(query.edit_message_media)(
      media=InputMediaPhoto(random.choice(PICS), caption=txt_),
      reply_markup=InlineKeyboardMarkup(button),
  )


@Bot.on_callback_query(filters.regex("^help$"))
async def help_callback(client, query):
  txt_ = """
</blockquote><b>🛠️ UptimeRobot Help Section</b>

<i>Welcome to <b>UptimeRobot</b>, your personal uptime monitoring assistant!
We keep an eye on your website or server 24/7 and alert you the moment it goes down — so you can act fast and keep your users happy.</i>

**📋 What We Do:**

__➪ Monitor your website, API, or server uptime.__

__➪ Send instant alerts when your site is down or back online.__

__➪ Show uptime logs and status history.__

**🚀 How to Use:**

__➪ Add your website or API link for monitoring.__

__➪ Sit back — we’ll notify you if anything goes wrong!__

**💡 Tips:**

<i>Make sure your site link starts with <code>https://</code> or <code>http://.</code></i>

__➪ You can monitor multiple sites at once.__

__➪ Check logs anytime using the /status command.__

**👨‍💻 Developer: @Wizard_bots**</blockquote>"""
  button = [
      [
          InlineKeyboardButton("🌐 Check Uptime", callback_data="check_uptime"),
          InlineKeyboardButton("📊 Stats", callback_data="stats"),
      ],
      [
          InlineKeyboardButton("🏠 Home", callback_data="start"),
          InlineKeyboardButton("📢 Channel", url="https://t.me/Wizard_Bots"),
      ],
      [
          InlineKeyboardButton(" Close ", callback_data="close"),
      ],
  ]
  if query.from_user.id in Bot.setting["ADMINS"]:
    button.append(
        [InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")])

  return await wait_flood(query.edit_message_media
                          )(media=InputMediaPhoto(random.choice(PICS),
                                                  caption=txt_),
                            reply_markup=InlineKeyboardMarkup(button))


def humanbytes(size):
  if not size:
    return ""
  units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
  size = float(size)
  i = 0
  while size >= 1024.0 and i < len(units) - 1:
    i += 1
    size /= 1024.0
  return "%.2f %s" % (size, units[i])


@Bot.on_callback_query(filters.regex("^stats$"))
async def stats_callback(client, query):
  await query.answer("Fetching System Details...")
  total_disk, used_disk, free_disk = shutil.disk_usage(".")
  total_disk_h = humanbytes(total_disk)
  used_disk_h = humanbytes(used_disk)
  free_disk_h = humanbytes(free_disk)
  disk_usage_percent = psutil.disk_usage('/').percent

  net_start = psutil.net_io_counters()
  time.sleep(2)
  net_end = psutil.net_io_counters()

  bytes_sent = net_end.bytes_sent - net_start.bytes_sent
  bytes_recv = net_end.bytes_recv - net_start.bytes_recv

  cpu_cores = os.cpu_count()
  cpu_usage = psutil.cpu_percent()

  ram = psutil.virtual_memory()
  ram_total = humanbytes(ram.total)
  ram_used = humanbytes(ram.used)
  ram_free = humanbytes(ram.available)
  ram_usage_percent = ram.percent

  try:
    uptime_seconds = time.time() - client.ping
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))
  except:
    uptime = "0"

  start_time = time.time()
  status_msg = await query.message.reply('📊 **Accessing System Details...**')
  end_time = time.time()
  time_taken_ms = (end_time - start_time) * 1000

  os_name = platform.system()
  os_version = platform.release()
  python_version = platform.python_version()

  response_text = f"""
  <blockquote>🖥️ **System Statistics Dashboard**

  💾 **Disk Storage**
  ├ Total:  `{total_disk_h}`
  ├ Used:  `{used_disk_h}` ({disk_usage_percent}%)
  └ Free:  `{free_disk_h}`

  🧠 **RAM (Memory)**
  ├ Total:  `{ram_total}`
  ├ Used:  `{ram_used}` ({ram_usage_percent}%)
  └ Free:  `{ram_free}`

  ⚡ **CPU**
  ├ Cores:  `{cpu_cores}`
  └ Usage:  `{cpu_usage}%`

  🌐 **Network**
  ├ Upload Speed:  `{humanbytes(bytes_sent/2)}/s`
  ├ Download Speed:  `{humanbytes(bytes_recv/2)}/s`
  └ Total I/O:  `{humanbytes(net_end.bytes_sent + net_end.bytes_recv)}`

  📟 **System Info**
  ├ OS:  `{os_name}`
  ├ OS Version:  `{os_version}`
  ├ Python:  `{python_version}`
  └ Uptime:  `{uptime}`

  ⏱️ **Performance**
  └ Current Ping:  `{time_taken_ms:.3f} ms`</blockquote>"""

  button = [[
      InlineKeyboardButton("🌐 Check Uptime", callback_data="check_uptime"),
      InlineKeyboardButton("🏠 Home", callback_data="start"),
  ],
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("📢 Channel",
                                     url="https://t.me/Wizard_Bots"),
            ], [
                InlineKeyboardButton(" Close ", callback_data="close"),
            ]]
  if query.from_user.id in Bot.setting["ADMINS"]:
    button.append(
        [InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")])

  await status_msg.delete()
  return await wait_flood(query.edit_message_media
                          )(media=InputMediaPhoto(random.choice(PICS),
                                                  caption=response_text),
                            reply_markup=InlineKeyboardMarkup(button))


@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client, query):
  try:
    await query.answer()
  except:
    pass
  try:
    await wait_flood(query.message.reply_to_message.delete)()
  except:
    pass
  try:
    await wait_flood(query.message.delete)()
  except:
    pass


@Bot.on_callback_query(filters.regex("^check_uptime"))
async def check_uptime_callback__(client, query):
  return await check_uptime_callback(client, query)


async def check_uptime_callback(client, query):
  if str(query.from_user.id) not in uts_:
    uts_[str(query.from_user.id)] = {}
    await db_sync()
    return await wait_flood(
        query.edit_message_media
    )(media=InputMediaPhoto(
        random.choice(PICS),
        caption=
        "<i>You have not added any uptime yet. Please add one using below button</i>"
    ),
      reply_markup=InlineKeyboardMarkup([
          [InlineKeyboardButton("➕ Add Uptime ➕", callback_data="add_uptime")],
          [
              InlineKeyboardButton("🏠 Home", callback_data="start"),
              InlineKeyboardButton(" Close ", callback_data="close")
          ],
      ]))

  if not uts_[str(query.from_user.id)]:
    return await wait_flood(
        query.edit_message_media
    )(media=InputMediaPhoto(
        random.choice(PICS),
        caption=
        "<i>You have not added any uptime yet. Please add one using below button</i>"
    ),
      reply_markup=InlineKeyboardMarkup([
          [InlineKeyboardButton("➕ Add Uptime ➕", callback_data="add_uptime")],
          [
              InlineKeyboardButton("🏠 Home", callback_data="start"),
              InlineKeyboardButton(" Close ", callback_data="close")
          ],
      ]))

  try:
    page = int(query.data.split(":")[1])
  except:
    page = 1

  url_data = uts_.get(str(query.from_user.id), {})
  if not url_data or url_data is None:
    try: await query.answer("No more uptime to show")
    except: pass
  
  buttons = None
  try:
    txt_, buttons = await iterable_to_list(url_data, page)
  except:
    if (await iterable_to_list(url_data, page)) in [None, [], ()]:
      if (await iterable_to_list(url_data, page - 1)) not in [None, [], ()]:
        txt_, buttons = await iterable_to_list(url_data, page - 1)
        
      elif (await iterable_to_list(url_data, page + 1)) not in [None, [], ()]:
        txt_, buttons = await iterable_to_list(url_data, page + 1)
        
      elif (await iterable_to_list(url_data, 1)) not in [None, [], ()]:
        txt_, buttons = await iterable_to_list(url_data, 1)
        
      else:
        try:
          return await query.answer("No more uptime to show")
        except:
          return

  if not buttons:
    try:
      return await query.answer("No more uptime to show")
    except:
      return

  arrow_ = []
  if (await iterable_to_list(url_data, page - 1)) not in [None, [], ()]:
    arrow_.append(
        InlineKeyboardButton("<<", callback_data=f"check_uptime:{page - 1}"))
  if (await iterable_to_list(url_data, page + 1)) not in [None, [], ()]:
    arrow_.append(
        InlineKeyboardButton(">>", callback_data=f"check_uptime:{page + 1}"))

  if arrow_:
    buttons.append(arrow_)

  buttons.append(
      [InlineKeyboardButton("➕ Add New ➕", callback_data="add_uptime")])
  buttons.append([
      InlineKeyboardButton("➖ Remove All ➖",
                           callback_data="remove_uptime:all"),
      InlineKeyboardButton("🏠 Home", callback_data="start"),
  ])
  buttons.append([
      InlineKeyboardButton("♻️ Refresh ♻️",
                           callback_data=f"check_uptime:{page}"),
      InlineKeyboardButton(" Close ", callback_data="close")
  ])

  return await wait_flood(query.edit_message_media)(
      media=InputMediaPhoto(random.choice(PICS), caption=txt_),
      reply_markup=InlineKeyboardMarkup(buttons),
  )


#@Bot.on_callback_query(filters.regex("^process:cancel$"))
async def process_cancel_callback(client, query):
  await client.stop_listening(chat_id=query.from_user.id,
                              user_id=query.from_user.id)
  await query.answer(" Process Cancelled ")
  return await check_uptime_callback(client, query)


@Bot.on_callback_query(filters.regex("^add_uptime"))
async def add_uptime_callback(client, query):
  await wait_flood(
      query.edit_message_media
  )(media=InputMediaPhoto(
      random.choice(PICS),
      caption="<blockquote><i>Please send me the url of the website you want to add</i></blockquote>"),
    reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(" Cancel ", callback_data="process:cancel")],
    ]))
  try:
    call_ = await client.waits_for_both(
        query.from_user.id,
        msg_filter=None,
        cb_filter=filters.regex("^process:cancel$"),
        timeout=80,
    )
    if not call_:
      return await check_uptime_callback(client, query)

    elif hasattr(call_, 'data'):
      await call_.answer(" Process Cancelled ")
      return await process_cancel_callback(client, call_)

    if url := call_.text:
      if url in uts_[str(query.from_user.id)]:
        return await check_uptime_callback(client, query)

      uts_[str(query.from_user.id)][url] = {
          "status": False,
          "response_time": 0
      }
      await db_sync()
      try:
        await call_.delete()
      except:
        pass
      return await check_uptime_callback(client, query)

    else:
      await wait_flood(query.edit_message_media)(
          media=InputMediaPhoto(random.choice(PICS),
                                caption="<i>Please Give me a valid url</i>"),
          reply_markup=InlineKeyboardMarkup([
              [
                  InlineKeyboardButton("🌐 Check Uptime",
                                       callback_data="check_uptime")
              ],
              [
                  InlineKeyboardButton("🏠 Home", callback_data="start"),
                  InlineKeyboardButton(" Close ", callback_data="close")
              ],
          ]))
  except asyncio.TimeoutError:
    return await check_uptime_callback(client, query)

  except Exception as e:
    if "80" in str(e):
      return await check_uptime_callback(client, query)

    log.exception(e)
    return await check_uptime_callback(client, query)


@Bot.on_callback_query(filters.regex("^remove_uptime"))
async def remove_uptime_callback(client, query):
  if query.data == "remove_uptime:all":
    uts_[str(query.from_user.id)] = {}
    await db_sync()
  else:
    try:
      index_ = query.data.split(":")[1]
      url = list(uts_[str(query.from_user.id)].keys())[int(index_)]
      
      del uts_[str(query.from_user.id)][url]
      await db_sync()
    except IndexError:
      pass

  return await check_uptime_callback(client, query)


@Bot.on_callback_query(filters.regex("^info"))
async def info_callback(client, query):
  index_ = query.data.split("_")[1]
  url = list(uts_[str(query.from_user.id)].keys())[int(index_)]
  info = uts_[str(query.from_user.id)].get(url, {})
  if not info:
    try: await query.answer("No more uptime to show")
    except: pass
    return await check_uptime_callback(client, query)

  if info.get("response_time", None) not in [None, 0]:
    xt = ((time.time()) - info["response_time"])
    check_time_ = time.strftime("%Mm %Ss", time.gmtime(xt))
  else:
    check_time_ = 0
  
  txt_ = f"""
<b>URL:</b> <code>{url}</code>
<b>Status:</b> <code>{'Online' if info['status'] else 'Offline'}</code>
<b>Response Status:</b> <code>{info.get('response_status', '0')} </code>
<b>Check Time:</b> <code>{check_time_} sec</code>

<blockquote><b>Make By: @Wizard_Bots</b></blockquote>"""
  try:
    await query.answer()
  except:
    pass

  await wait_flood(query.edit_message_media)(
      media=InputMediaPhoto(random.choice(PICS), caption=txt_),
      reply_markup=InlineKeyboardMarkup([
          [
              InlineKeyboardButton("➖ Remove ➖",
                                   callback_data=f"remove_uptime:{index_}")
          ],
          [
              InlineKeyboardButton("🌐 Check Uptime",
                                   callback_data="check_uptime"),
              InlineKeyboardButton(" Close ", callback_data="close")
          ],
      ]))


@Bot.on_callback_query(filters.regex("^admin_panel$"))
async def admin_panel_callback(client, query):
  if query.from_user.id not in Bot.setting["ADMINS"]:
    return await wait_flood(query.answer)("You are not allowed to use this")

  txt_ = "**Admin Panel** \n"
  button = []
  for admins_cmds in client.setting.items():
    txt_ += f"\n<b>{admins_cmds[0]}:</b> <code>{admins_cmds[1]}</code>"
    button.append(
      InlineKeyboardButton(admins_cmds[0], callback_data=f"zpt:{admins_cmds[0]}")
    )
  
  button = split_list(button)
  button.append([
    InlineKeyboardButton("🏠 Home", callback_data="start"),
    InlineKeyboardButton(" Close ", callback_data="close")
  ])
  return await wait_flood(query.edit_message_media)(
    InputMediaPhoto(random.choice(PICS), caption=txt_),
    reply_markup=InlineKeyboardMarkup(button)
  )

@Bot.on_callback_query(filters.regex("^zpt"))
async def zpt_callback(client, query):
  if query.from_user.id not in Bot.setting["ADMINS"]:
    return await wait_flood(query.answer)("You are not allowed to use this")
  
  data = query.data.split(":")[1]
  if not data:
    try: await wait_flood(query.answer)("Invalid Data")
    except: pass
    return await admin_panel_callback(client, query)
  
  return await wait_flood(query.edit_message_media)(
    InputMediaPhoto(
      random.choice(PICS), 
      caption=f"<b>{data}:</b> <code>{client.setting[data]}</code>"
    ),
    reply_markup=InlineKeyboardMarkup([
      [
        InlineKeyboardButton("➕ Add ➕", callback_data=f"zadd:{data}"),
        InlineKeyboardButton("➖ Remove ➖", callback_data=f"zrem:{data}")
      ],
      [
        InlineKeyboardButton("🏠 Home", callback_data="start"),
        InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")
      ],
      [
        InlineKeyboardButton(" Close ", callback_data="close")
      ]
    ])
  )


@Bot.on_callback_query(filters.regex("^zadd"))
async def zadd_callback(client, query):
  if query.from_user.id not in Bot.setting["ADMINS"]:
    return await wait_flood(query.answer)("You are not allowed to use this")
  
  data = query.data.split(":")[1]
  if not data:
    try: await wait_flood(query.answer)("Invalid Data")
    except: pass
    return await admin_panel_callback(client, query)
  
  try:
    await wait_flood(query.edit_message_media)(
      InputMediaPhoto(
        random.choice(PICS),
        caption=f"<b>{data}:</b> <code>{client.setting[data]}</code>"
      ),
      reply_markup=InlineKeyboardMarkup([
        [
          InlineKeyboardButton(" Cancel ", callback_data=f"aprocess:{data}")
        ]
      ])
    )
    call_ = await client.waits_for_both(
      query.from_user.id,
      msg_filter=None,
      cb_filter=filters.regex("^aprocess:cancel$"),
      timeout=80,
    )
    if not call_:
      return await zpt_callback(client, query)
    elif hasattr(call_, 'data'):
      await call_.answer(" Process Cancelled ")
      return await zpt_callback(client, query)
    
    elif call_.text:
      if isinstance(client.setting[data], list):
        try: client.setting[data].append(int(call_.text))
        except: client.setting[data].append(call_.text)
      else:
        client.setting[data] = call_.text
        if data == "FORCE_SUB_CHANNEL":
          load_fsb_vars(client)
      
      try: await call_.delete()
      except: pass
    
    return await zpt_callback(client, query)
  except asyncio.TimeoutError:
    return await zpt_callback(client, query)
  except Exception as e:
    if "80" in str(e):
      return await zpt_callback(client, query)
    log.exception(e)
    return await zpt_callback(client, query)



@Bot.on_callback_query(filters.regex("^zrem"))
async def zrem_callback(client, query):
  if query.from_user.id not in Bot.setting["ADMINS"]:
    return await wait_flood(query.answer)("You are not allowed to use this")
  
  data = query.data.split(":")[1]
  if not data:
    try: await wait_flood(query.answer)("Invalid Data")
    except: pass
    return await admin_panel_callback(client, query)
  
  if isinstance(client.setting[data], list):
    try:
      await wait_flood(query.edit_message_media)(
        InputMediaPhoto(
          random.choice(PICS),
          caption=f"<b>{data}:</b> <code>{client.setting[data]}</code> \n<i>Send the value, u want to remove, for all send <code>all</code></i>"
        ),
        reply_markup=InlineKeyboardMarkup([
          [
            InlineKeyboardButton(" Cancel ", callback_data=f"aprocess:{data}")
          ]
        ])
      )
      call_ = await client.waits_for_both(
        query.from_user.id,
        msg_filter=None,
        cb_filter=filters.regex("^aprocess:cancel$"),
        timeout=80,
      )
      if not call_:
        return await zpt_callback(client, query)
      elif hasattr(call_, 'data'):
        await call_.answer(" Process Cancelled ")
        return await zpt_callback(client, query)
      
      elif call_.text:
        if call_.text == "all":
          client.setting[data] = []
        else:
          try: client.setting[data].remove(int(call_.text))
          except: client.setting[data].remove(call_.text)
        try: await call_.delete()
        except: pass
      return await zpt_callback(client, query)
    except asyncio.TimeoutError:
      return await zpt_callback(client, query)
    except Exception as e:
      if "80" in str(e):
        return await zpt_callback(client, query)
      log.exception(e)
      return await zpt_callback(client, query)
  else:
    client.setting[data] = None
    return await zpt_callback(client, query)
