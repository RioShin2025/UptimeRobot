from pyrogram import Client, filters
import os
import time
import logging
import sys

from pyrogram.handlers import MessageHandler, CallbackQueryHandler
import asyncio

API_ID = int(os.environ.get("API_ID", "3"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

DB_URL = os.environ.get("DB_URL", "")
DB_NAME = os.environ.get("DB_NAME", "UptimeRobot")

OWNER = int(os.environ.get("OWNER", "7225682334"))
ADMINS = os.environ.get("ADMINS", "8385101318")
ADMINS = [int(admin) for admin in (ADMINS).split(" ")]
ADMINS.append(OWNER)

MAIN_CHANNEL = os.environ.get("MAIN_CHANNEL", "ShanksSupport")
FORCE_SUB_TEXT = os.environ.get(
    "FORCE_SUB_TEXT",
    """<b><i>❗️ You must join our channel before using this feature:</i></b>"""
)

FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "𝕸𝖆𝖎𝖓 𝕮𝖍𝖆𝖓𝖓𝖊𝖑: Wizard_Bots")

SETTINGS = {
    "ADMINS": ADMINS,
    "FORCE_SUB_TEXT": FORCE_SUB_TEXT,
    "FORCE_SUB_CHANNEL": FORCE_SUB_CHANNEL,
}


class StyledFormatter(logging.Formatter):
  FORMAT_BASE = "[%(asctime)s] 🛠️ [%(levelname)s] 📁 %(filename)s:%(lineno)d ➤ %(funcName)s() ▶ %(message)s"

  FORMATS = {
      logging.DEBUG: "\033[36m🔍 " + FORMAT_BASE + "\033[0m",  # Cyan
      logging.INFO: "\033[33mℹ️ " + FORMAT_BASE + "\033[0m",  # Yellow
      logging.WARNING: "\033[32m⚠️ " + FORMAT_BASE + "\033[0m",  # Green
      logging.ERROR: "\033[31m❌ " + FORMAT_BASE + "\033[0m",  # Red
      logging.CRITICAL: "\033[35m💀 " + FORMAT_BASE + "\033[0m"  # Magenta
  }

  def format(self, record):
    fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
    formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
    return formatter.format(record)


def get_logger(name: str = "app") -> logging.Logger:
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)

  if not logger.hasHandlers():
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(StyledFormatter())
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d - %(funcName)s()] ▶ %(message)s",
            "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(file_handler)

    logger.propagate = False

  return logger


log = get_logger(__name__)


class UpTimeRoBot(Client):

  def __init__(self):
    super().__init__("bot",
                     api_id=API_ID,
                     api_hash=API_HASH,
                     bot_token=BOT_TOKEN,
                     plugins=dict(root="TG"))

  async def start(self):
    await super().start()
    me = await self.get_me()
    self.username = me.username
    self.ping = time.time()
    self.setting = SETTINGS
    self.owner = OWNER
    self.FSB = []

    log.info("""
██╗    ██╗██╗███████╗ █████╗ ██████╗ ██████╗     ██████╗  ██████╗ ████████╗███████╗
██║    ██║██║╚══███╔╝██╔══██╗██╔══██╗██╔══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝
██║ █╗ ██║██║  ███╔╝ ███████║██████╔╝██║  ██║    ██████╔╝██║   ██║   ██║   ███████╗
██║███╗██║██║ ███╔╝  ██╔══██║██╔══██╗██║  ██║    ██╔══██╗██║   ██║   ██║   ╚════██║
╚███╔███╔╝██║███████╗██║  ██║██║  ██║██████╔╝    ██████╔╝╚██████╔╝   ██║   ███████║
 ╚══╝╚══╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝     ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝"""
             )
    log.info(f"🤖 Bot Started as {me.first_name} | @{me.username}")
    log.info(f"🆔 Bot ID: {me.id}")
    self.msg = await self.send_photo(
      MAIN_CHANNEL,
      photo=PICS[-1],
      caption="<b>🔄 Checking Uptime...</b>",
    )

  async def waits_for_both(self, user_id, msg_filter, cb_filter, timeout=80):
    """Fixed version with proper error handling"""

    message_task = None
    callback_task = None

    try:
      # Create tasks
      message_task = asyncio.create_task(
          self.listen(user_id=user_id, filters=msg_filter,
                                timeout=timeout))
      
      callback_task = asyncio.create_task(
          self.wait_for_callback_query(user_id, filters=cb_filter
                                       & filters.user(user_id),
                                       timeout=timeout))

      done, pending = await asyncio.wait([message_task, callback_task],
                                         timeout=timeout,
                                         return_when=asyncio.FIRST_COMPLETED)

      # Cancel pending tasks gracefully
      for task in pending:
        task.cancel()
        try:
          await task
        except (asyncio.CancelledError, Exception):
          pass

      return await next(iter(done)) if done else None

    except asyncio.CancelledError:
      return None
    except Exception as er:
      log.exception(er)
      return None
    finally:
      # Ensure all tasks are properly cancelled
      if message_task and not message_task.done():
        message_task.cancel()
      if callback_task and not callback_task.done():
        callback_task.cancel()

  async def stop(self, *args):
    await super().stop()
    log.info("🛑 Bot Stopped")


Bot = UpTimeRoBot()

PICS = (
    "https://img3.teletype.in/files/67/73/67735f4f-933a-41d9-86b9-609fa03b6614.jpeg",
    "https://img3.teletype.in/files/a6/b6/a6b666ef-afa0-4793-bd6b-235265258840.jpeg",
    "https://img3.teletype.in/files/e8/01/e8013193-9299-4cdc-8222-f4e3801a05e8.jpeg",
    "https://img4.teletype.in/files/77/7f/777f2c2d-fa53-4298-9dee-ab39d9bddf81.jpeg",
    "https://img3.teletype.in/files/a1/9e/a19e9352-dfee-471a-ae3f-14eb2e1b975b.jpeg",
    "https://img1.teletype.in/files/84/84/8484934a-a247-4b1a-8f1f-74aac621bea6.jpeg",
    "https://img4.teletype.in/files/b2/89/b289d67c-2299-4cf6-91c3-b84c83c57caa.jpeg",
    "https://img3.teletype.in/files/a0/49/a049a7b1-2924-41c1-95d4-8c466c1a80ad.jpeg",
    "https://img2.teletype.in/files/59/b3/59b3a62e-e2ce-4f00-847d-9910f0498884.jpeg",
    "https://img2.teletype.in/files/91/d8/91d8838b-85ec-45ff-868f-24d66126ce55.jpeg",
    "https://img4.teletype.in/files/71/a5/71a5481f-2398-4520-8229-222d1cf733e7.jpeg",
    "https://img4.teletype.in/files/f4/b0/f4b007ec-fc8c-49fd-a1fb-b0d02985120a.jpeg",
    "https://img4.teletype.in/files/f6/3c/f63cee0d-10ff-4b8d-9ccc-943fa80a1344.jpeg",
    "https://img4.teletype.in/files/77/ff/77ff451d-0c8a-4aeb-aa9a-a1ae7ca74069.jpeg",
    "https://img4.teletype.in/files/bb/e9/bbe9e4f6-6226-4764-8169-b7d368e29e8c.jpeg",
    "https://img2.teletype.in/files/d4/b8/d4b806a2-c534-466f-85cb-f05a9e31dc92.jpeg",
    "https://img4.teletype.in/files/b6/aa/b6aab772-1d39-4b7e-bfe5-8d04b57ac31e.jpeg",
    "https://img4.teletype.in/files/f5/c3/f5c3a05e-ecfb-4a8e-b921-2b264d40d0ce.jpeg",
    "https://img4.teletype.in/files/3f/01/3f0102af-352a-4a0a-abbd-f18919c56dc9.jpeg",
    "https://img4.teletype.in/files/7f/f2/7ff228ef-6e74-4baf-a877-b35c016d6c7b.jpeg",
    "https://img1.teletype.in/files/8b/02/8b02924e-4f24-4ace-8b3f-be2f8044b8ec.jpeg",
    "https://img2.teletype.in/files/dc/16/dc1625b2-410c-48da-98c1-1956b87768e1.jpeg",
    "https://img2.teletype.in/files/97/f3/97f31df6-2cca-4f58-8269-97aebb6d9ea7.jpeg",
    "https://img2.teletype.in/files/97/65/9765707e-1855-429b-89ba-03401b734827.jpeg",
    "https://img4.teletype.in/files/f4/53/f45390f3-e1eb-4570-9d67-c4114db18589.jpeg",
    "https://img1.teletype.in/files/81/26/81265a94-68ff-47ed-b409-fad382e7a627.jpeg",
    "https://img1.teletype.in/files/0a/1b/0a1b5f17-095c-4826-84c8-39a8b9b9deef.jpeg",
    "https://img4.teletype.in/files/f5/94/f594fbe2-b52d-489a-86c9-23b2f2dbe4d7.jpeg",
    "https://img3.teletype.in/files/e3/76/e376be29-065b-4c1a-986d-aba69d08208f.jpeg",
    "https://img1.teletype.in/files/8f/e6/8fe67878-43a3-4b3d-851f-63727a6a2b0b.jpeg",
    "https://img2.teletype.in/files/1a/d3/1ad3fa24-c3bf-4ca8-a7ef-a79286b1e37c.jpeg",
    "https://img1.teletype.in/files/80/1a/801a77ad-bf05-4d7a-96c9-2b1cde09d04f.jpeg",
    "https://img4.teletype.in/files/f4/b0/f4b007ec-fc8c-49fd-a1fb-b0d02985120a.jpeg",
    "https://img4.teletype.in/files/f6/3c/f63cee0d-10ff-4b8d-9ccc-943fa80a1344.jpeg",
    "https://ik.imagekit.io/jbxs2z512/naruto_GxcPgSeOy.jpg?updatedAt=1748486799631",
    "https://ik.imagekit.io/jbxs2z512/hd-anime-prr1y1k5gqxfcgpv.jpg?updatedAt=1748487947183",
    "https://ik.imagekit.io/jbxs2z512/dazai-osamu-sunset-rooftop-anime-wallpaper-cover.jpg?updatedAt=1748488276069",
    "https://ik.imagekit.io/jbxs2z512/thumb-1920-736461.png?updatedAt=1748488419323",
    "https://ik.imagekit.io/jbxs2z512/116847-3840x2160-desktop-4k-bleach-background-photo.jpg?updatedAt=1748488510841",
    "https://ik.imagekit.io/jbxs2z512/thumb-1920-1361035.jpeg?updatedAt=1748488911202",
    "https://ik.imagekit.io/jbxs2z512/thumb-1920-777955.jpg?updatedAt=1748488978230",
    "https://ik.imagekit.io/jbxs2z512/akali-wallpaper-960x540_43.jpg?updatedAt=1748489275125",
    "https://ik.imagekit.io/jbxs2z512/robin-honkai-star-rail-497@1@o?updatedAt=1748490140360",
    "https://ik.imagekit.io/jbxs2z512/wallpapersden.com_tian-guan-ci-fu_1920x1080.jpg?updatedAt=1748490255277",
    "https://ik.imagekit.io/jbxs2z512/1129176.jpg?updatedAt=1748491905419",
    "https://ik.imagekit.io/jbxs2z512/wp14288215.jpg?updatedAt=1748492348766",
    "https://ik.imagekit.io/jbxs2z512/8k-anime-girl-and-flowers-t4bj6u55nmgfdrhe.jpg?updatedAt=1748493169919",
    "https://ik.imagekit.io/jbxs2z512/anime_Fuji_Choko_princess_anime_girls_Sakura_Sakura_Woman_in_Red_mask_palace-52030.png!d?updatedAt=1748493259665",
    "https://ik.imagekit.io/jbxs2z512/1187037bb1d8aaf14a631f7b813296f1.jpg?updatedAt=1748493396756",
    "https://ik.imagekit.io/jbxs2z512/yor_forger_by_senku_07_dgifqh7-fullview.jpg_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9ODAzIiwicGF0aCI6IlwvZlwvNDAxZDdlYTYtOGEyZi00ZTFiLTkxYTAtNjA3YmRlYTgzZmE4XC9kZ2lmcWg3LWNlMjY3Mzc2LWQ4NWYtNGMzZS1iNWY1LWU0OTZhYWM3ZmUyNC5wbmciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.FVwtt0HGKv6UQqWHkEbxmE1qkI5CFNNS5SzAYj4EVUs?updatedAt=1748493490929",
    "https://ik.imagekit.io/jbxs2z512/attack-on-titan-mikasa-cover-image-ybt96t1e1041qdt3.jpg?updatedAt=1748493720903",
    "https://ik.imagekit.io/jbxs2z512/tsunade-at-her-desk-bakoh4jeg42sjn3c.jpg?updatedAt=1748493962363",
    "https://ik.imagekit.io/jbxs2z512/1b3025cb9fc1a3cd43fdff42167d0dea.jpg?updatedAt=1748498508575",
    "https://ik.imagekit.io/jbxs2z512/Fight-Break-Sphere.png?updatedAt=1750042299023",
    "https://ik.imagekit.io/jbxs2z512/doupocangqiong-medusa-queen-hd-wallpaper-preview.jpg?updatedAt=1750042397343",
    "https://ik.imagekit.io/jbxs2z512/wp5890248.jpg?updatedAt=1750042498187",
    "https://ik.imagekit.io/jbxs2z512/sacffc_uu-T1F5AC?updatedAt=1750042873876",
    "https://ik.imagekit.io/jbxs2z512/1345216.jpeg?updatedAt=1750042982858",
    "https://ik.imagekit.io/jbxs2z512/shanks-divine-departure-attack-in-one-piece-sn.jpg?updatedAt=1750043121252",
    "https://ik.imagekit.io/jbxs2z512/1a74aff1d81a1af5f3e25b9b30282e06.jpg?updatedAt=1750043251516",
    "https://ik.imagekit.io/jbxs2z512/22219.jpg?updatedAt=1751107408410",
    "https://ik.imagekit.io/jbxs2z512/21418.jpg?updatedAt=1751107452919",
    "https://ik.imagekit.io/jbxs2z512/mythical-dragon-beast-anime-style_23-2151112835.jpg?updatedAt=1751107574210",
    "https://ik.imagekit.io/jbxs2z512/halloween-scene-illustration-anime-style_23-2151794288.jpg?updatedAt=1751107676806",
    "https://ik.imagekit.io/jbxs2z512/5823589-2920x1640-desktop-hd-boy-programmer-wallpaper-image.jpg_id=1726666227?updatedAt=1751107911063",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-1345576.webp?updatedAt=1751108065802",
    "https://ik.imagekit.io/jbxs2z512/thumb-440-1340473.webp?updatedAt=1751108159970",
    "https://ik.imagekit.io/jbxs2z512/wp3084738.jpg?updatedAt=1751108326075",
    "https://ik.imagekit.io/jbxs2z512/wp12362449.png?updatedAt=1751108554882",
    "https://ik.imagekit.io/jbxs2z512/wp7627005.jpg?updatedAt=1751108634878",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-1335194.webp?updatedAt=1751108710765",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-1373976.webp?updatedAt=1751108748746",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-1065277.webp?updatedAt=1751108877871",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-877141.webp?updatedAt=1751108916209",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-856517.webp?updatedAt=1751108984376",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-722181.webp?updatedAt=1751109016670",
    "https://ik.imagekit.io/jbxs2z512/thumbbig-1337392.webp?updatedAt=1751109084903",
    "https://ik.imagekit.io/jbxs2z512/anime-4k-pc-hd-download-wallpaper-preview%20(1).jpg?updatedAt=1751109522060",
    "https://ik.imagekit.io/jbxs2z512/876145-3840x2160-desktop-4k-konan-naruto-background-image%20(1).jpg?updatedAt=1751109523353",
    "https://ik.imagekit.io/jbxs2z512/tumblr_9663cff78634f174f81b41b64fc450df_66ebd999_1280%20(1).png?updatedAt=1751109523759",
    "https://ik.imagekit.io/jbxs2z512/anime-girl-demon-horn-art-4k-wallpaper-uhdpaper.com-714@2@b%20(1).jpg?updatedAt=1751109524369",
    "https://ik.imagekit.io/jbxs2z512/dbbb586df338d55d340ec650bcdd74fe.jpg?updatedAt=1751110984735",
    "https://ik.imagekit.io/jbxs2z512/c02aecb70c3c6a5b1f51ba09e4d2cc70.jpg?updatedAt=1751111979586",
    "https://ik.imagekit.io/jbxs2z512/6c2618a1eea58d22e2d1a5ba99c95a1c.jpg?updatedAt=1751112051082",
    "https://ik.imagekit.io/jbxs2z512/7a82750e26bf451ab1775993279e2c64.jpg?updatedAt=1751112189297",
    "https://ik.imagekit.io/jbxs2z512/a469262476f60456dd4aceb8a75deed5.jpg?updatedAt=1751112263336",
    "https://ik.imagekit.io/jbxs2z512/ad05ea75da4e9dd28f0e71c398d16a70.jpg?updatedAt=1751616664015",
    "https://ik.imagekit.io/jbxs2z512/ca525e543c2719891612c737a269d50d.jpg?updatedAt=1751616762244",
    "https://ik.imagekit.io/jbxs2z512/515329f5fb6449cd5c5742e8118912c8.jpg?updatedAt=1751616576915",
    "https://ik.imagekit.io/jbxs2z512/7d405472605913d0b1ace935591510ef.jpg?updatedAt=1751617338294",
    "https://ik.imagekit.io/jbxs2z512/e0ec0f65320e6930cfdb00a41979408c.jpg?updatedAt=1751617427686",
    "https://ik.imagekit.io/jbxs2z512/cf39f75ba7aa8391d7c32929feadaaffd7d76.jpg?updatedAt=1751617579813",
    "https://ik.imagekit.io/jbxs2z512/5f6ca554415a9626ea709f803727a267.jpg?updatedAt=1751617791661",
    "https://ik.imagekit.io/jbxs2z512/107895c50cd55d1b0bf77cc814e-00671f4.jpg?updatedAt=1751617893009",
    "https://ik.imagekit.io/jbxs2z512/4555abb8a92ccec7a37b5e3621281c77.jpg?updatedAt=1751618816270",
    "https://ik.imagekit.io/jbxs2z512/3d4aa530c4e8ef17d6098fad44728ee5.jpg?updatedAt=1751620240035",
    "https://ik.imagekit.io/jbxs2z512/2f6b6cfcd929bf97e639515a1f187f6d.jpg?updatedAt=1751620404536",
    "https://ik.imagekit.io/jbxs2z512/4f0076085b8aea935a30b9eb1c8e9867.jpg?updatedAt=1751623894659",
    "https://ik.imagekit.io/jbxs2z512/631f6026e50d6644b87bc20bca2ec12a.jpg?updatedAt=1751628298231",
    "https://ik.imagekit.io/jbxs2z512/wp15082614.jpg?updatedAt=1751628541804",
    "https://ik.imagekit.io/jbxs2z512/wp15082622.webp?updatedAt=1751628578344",
    "https://ik.imagekit.io/jbxs2z512/e618b0d2a9518326722d6483569a94c6.jpg?updatedAt=1757316947948",
    "https://ik.imagekit.io/jbxs2z512/6222c23f673d9d6b86cf759a440935d9.jpg?updatedAt=1757317031249",
    "https://ik.imagekit.io/jbxs2z512/b322fad3ae2e550b5e9a0cb1d2c78311.jpg?updatedAt=1757317116796",
    "https://ik.imagekit.io/jbxs2z512/0a7f44752689424fd901b220aa5c5516.jpg?updatedAt=1757317197691",
    "https://ik.imagekit.io/jbxs2z512/c4567ce2326aa09a4b33b0ff21e9d1ef.jpg?updatedAt=1757317301147",
    "https://ik.imagekit.io/jbxs2z512/a6a2b0fe748ec78ead3c3ac85b1472a8.jpg?updatedAt=1757317366150",
    "https://ik.imagekit.io/jbxs2z512/5763d2e3681540671e85066a5f600cf5.jpg?updatedAt=1757317432437",
    "https://ik.imagekit.io/jbxs2z512/57b6e9637bd6cf48649b4576baf72f72.jpg?updatedAt=1757317509952",
    "https://ik.imagekit.io/jbxs2z512/42e36ef6930669ea1a1696f6e2e9084c.jpg?updatedAt=1757317644096",
    "https://ik.imagekit.io/jbxs2z512/a1a4cf3066e20b9699a987e1b0379565.jpg?updatedAt=1757318914589",
    "https://ik.imagekit.io/jbxs2z512/3f36f010cb6acb9468951d561fc01464.jpg?updatedAt=1757318940586",
    "https://ik.imagekit.io/jbxs2z512/0248823b46df5e7f74b7101c305de13d.jpg?updatedAt=1757318960094",
    "https://ik.imagekit.io/jbxs2z512/62d47644f5f720b9108c0ff448dad10e.jpg?updatedAt=1757321226076",
)
