# TG/ping.py
import time
import platform
import psutil
from pyrogram import filters
from bot import Bot

def format_bytes(size):
    for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

@Bot.on_message(filters.command("ping"))
async def ping_cmd(_, msg):
    start = time.time()

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_cores = psutil.cpu_count()

    # RAM
    mem = psutil.virtual_memory()

    # Disk
    disk = psutil.disk_usage("/")

    # Network
    net = psutil.net_io_counters()

    # System uptime
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))

    end = time.time()
    ping_ms = (end - start) * 1000

    text = f"""
<blockquote>🖥️ **System Statistics Dashboard**

💾 **Disk Storage**
├ Total: {format_bytes(disk.total)}
├ Used: {format_bytes(disk.used)} ({disk.percent}%)
└ Free: {format_bytes(disk.free)}

🧠 **RAM (Memory)**
├ Total: {format_bytes(mem.total)}
├ Used: {format_bytes(mem.used)} ({mem.percent}%)
└ Free: {format_bytes(mem.available)}

⚡ **CPU**
├ Cores: {cpu_cores}
└ Usage: {cpu_percent}%

🌐 **Network**
├ Upload: {format_bytes(net.bytes_sent)}
├ Download: {format_bytes(net.bytes_recv)}
└ Total I/O: {format_bytes(net.bytes_sent + net.bytes_recv)}

📟 **System Info**
├ OS: {platform.system()}
├ OS Version: {platform.release()}
├ Python: {platform.python_version()}
└ Uptime: {uptime}

⏱️ **Performance**
└ Current Ping: {ping_ms:.3f} ms  </blockquote>
"""

    await msg.reply_text(text)
