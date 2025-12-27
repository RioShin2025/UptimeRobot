from bot import Bot

from TG.broadcast import load_broadcast_cmds
from bot import ADMINS  # or wherever ADMINS is defined

load_broadcast_cmds(Bot, ADMINS)
from Tools.db import get_all_urls, remove_expired_urls
from Tools.requets_handler import runs_checking
import asyncio
from fastapi import FastAPI
from uvicorn import Config, Server

async def worker():
  while True:
    try:
      await runs_checking([i for i in get_all_urls()], Bot.msg)
      async for info in remove_expired_urls():
        try:
          await Bot.send_message(
              int(info['user_id']),
              f"<b>❌ URL: {info['url']} is removed from database because it is expired</b>"
          )
        except:
          pass
    except:
      pass
    await asyncio.sleep(3)



app = FastAPI()

@app.head("/")
@app.get("/")
async def hello():
    return {"message": "Hello, World!", "status": "success"}

async def main_web():
    config = Config(app, host="0.0.0.0", port=3000, reload=False)
    server = Server(config)
    await server.serve()


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.create_task(main_web())
  loop.create_task(worker())
  Bot.run()
