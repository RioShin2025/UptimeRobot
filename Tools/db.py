from pymongo import MongoClient
from bot import get_logger, DB_NAME, DB_URL

import asyncio
import time
from datetime import datetime, timedelta

db_client = MongoClient(DB_URL)
db = db_client[DB_NAME]
db_data = db[DB_NAME]

uts_ = db_data.find_one({"_id": DB_NAME})
if not uts_:
  uts_ = {"_id": DB_NAME}
  db_data.insert_one(uts_)


async def db_sync():

  def sync_replace():
    db_data.replace_one({'_id': DB_NAME}, uts_)

  return await asyncio.get_event_loop().run_in_executor(None, sync_replace)


def url_sync():
  db_data.replace_one({'_id': DB_NAME}, uts_)


def get_all_urls():
  for user_id, urls in uts_.items():
    if user_id == "_id":
      continue

    for url, info in urls.items():
      info['url'] = url
      info['User_id'] = user_id
      yield info


async def remove_expired_urls():
  """Remove URLs that expired 2 or more days ago using datetime"""
  expired_count = 0
  current_time = time.time()
  two_days_ago = current_time - (2 * 24 * 60 * 60)  # 2 days in seconds

  # Collect items to remove first
  to_remove = []

  for user_id, urls in uts_.items():
    if user_id == "_id":
      continue

    for url, info in urls.items():
      if info.get('status') in [False, None]:
        response_time = info.get("response_time")

        if response_time and response_time != 0:
          # Check if response_time is older than 2 days
          if response_time <= two_days_ago:
            to_remove.append((user_id, url, info))

  # Remove collected items and yield
  for user_id, url, info in to_remove:
    if user_id in uts_ and url in uts_[user_id]:
      del uts_[user_id][url]
      await db_sync()

      info['url'] = url
      info['user_id'] = user_id
      expired_count += 1
      yield info

  # Sync to database if any URLs were removed
  if expired_count > 0:
    await db_sync()
