import urllib.request
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from .db import uts_, url_sync as db_sync

from TG.help import wait_flood
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import random 
from bot import PICS, get_logger

log = get_logger(__name__)

async def ultra_light_check(urls_data, max_workers=200, batch_size=500, print_progress=None, progress_args=None):
    """
    Ultimate lightweight URL checker - minimal RAM, maximum efficiency
    """
    total = len(urls_data)
    successful = 0
    processed = 0
    start_time = time.time()

    def quick_check(url_data):
        """Tiny check function - minimal memory footprint"""
        try:
            # Direct URL check - no fancy objects
            with urllib.request.urlopen(url_data['url'], timeout=3) as response:
                if response.getcode() == 200:
                    uts_[url_data['User_id']][url_data['url']]['response_status'] = response.getcode()
                    uts_[url_data['User_id']][url_data['url']]['status'] = True
                    uts_[url_data['User_id']][url_data['url']]['response_time'] = time.time()
                    db_sync()
                    
                    return True
                else:
                    uts_[url_data['User_id']][url_data['url']]['response_status'] = response.getcode()
                    uts_[url_data['User_id']][url_data['url']]['status'] = False
                    #uts_[url_data['User_id']][url_data['url']]['response_time'] = time.time()
                    #db_sync()
                    
                    return None
                    
        except Exception as err:
            #log.exception(err)
            uts_[url_data['User_id']][url_data['url']]['status'] = False
            uts_[url_data['User_id']][url_data['url']]['response_time'] = time.time()
            uts_[url_data['User_id']][url_data['url']]['response_status'] = 404
            db_sync()
        
        return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()

        # Process in small batches to avoid memory buildup
        for i in range(0, total, batch_size):
            batch = urls_data[i:i + batch_size]
            processed += len(batch)

            # Process current batch
            tasks = [
                loop.run_in_executor(executor, quick_check, url_data) 
                for url_data in batch
            ]

            results = await asyncio.gather(*tasks)

            # Update successful URLs immediately
            batch_successful = 0
            for result in results:
                if result:
                    batch_successful += 1

            successful += batch_successful

            # Progress update (minimal)
            if processed % 10000 == 0 or processed == total:
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0

                if print_progress:
                    await print_progress(progress_args, processed, total, successful, rate, elapsed)

            # Clear memory after each batch
            del batch, tasks, results

        # Single DB sync at the end for better performance
        db_sync()

    total_time = time.time() - start_time

    return {
        'total_urls': total,
        'successful': successful,
        'failed': total - successful,
        'total_time': total_time,
        'requests_per_second': total / total_time if total_time > 0 else 0
    }

# Even simpler version for lowest RAM usage
async def minimal_check(urls_data, workers=150, print_progress=None, progress_args=None):
    """
    Absolute minimal version - lowest memory footprint
    """
    total = len(urls_data)
    successful = 0
    start = time.time()
    processed = 0

    def micro_check(url_data):
        """Absolute minimum check"""
        try:
            urllib.request.urlopen(url_data['url'], timeout=2)
            return True
        except:
            return False

    loop = asyncio.get_event_loop()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Process all URLs in one go but with controlled concurrency
        tasks = [
            loop.run_in_executor(executor, micro_check, url_data)
            for url_data in urls_data
        ]

        results = await asyncio.gather(*tasks)

        # Process results
        for i, result in enumerate(results):
            processed = i + 1
            if result:
                # Update database for successful URLs
                user_id = str(urls_data[i]['User_id'])
                url = urls_data[i]['url']
                if user_id in uts_ and url in uts_[user_id]:
                    uts_[user_id][url]['status'] = True
                    uts_[user_id][url]['response_time'] = 200
                successful += 1

            # Progress every 10k URLs
            if processed % 10000 == 0 or processed == total:
                elapsed = time.time() - start
                rate = processed / elapsed if elapsed > 0 else 0
                if print_progress:
                    await print_progress(progress_args, processed, total, successful, rate, elapsed)

        # Single DB sync at the end
        db_sync()

    return successful, total



async def telegram_progress(progress_args, processed, total, successful, rate, elapsed):
    """
    Progress function for Telegram bot with message editing
    """
    if progress_args:
        msg, text = progress_args

        progress_percent = (processed / total) * 100
        remaining = total - processed
        eta = remaining / rate if rate > 0 else 0

        message = (
            f"<blockquote>🔍 **URL Check Progress**\n</blockquote>"
            f"<blockquote>📊 `{processed:,}/{total:,}` ({progress_percent:.1f}%)\n</blockquote>"
            f"<blockquote>✅ **Successful:** `{successful:,}`\n</blockquote>"
            f"<blockquote>⚡ **Speed:** `{rate:.1f}/sec`\n</blockquote>"
            f"<blockquote>⏱️ **ETA:** `{eta:.1f}s`</blockquote>"
        )

        try:
            await msg.edit_media(
                InputMediaPhoto(
                    media=random.choice(PICS),
                    caption=message
                )
            )
        except:
            await asyncio.sleep(5)
            pass  # Ignore flood errors


async def runs_checking(urls_data, message=None):
    """
    Run check with Telegram progress updates
    """
    return await ultra_light_check(
        urls_data,
        max_workers=200,
        batch_size=500,
        print_progress=telegram_progress,
        progress_args=(message, "URL Check")
    )
