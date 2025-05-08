import psutil
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# activate read from .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TITLE = os.getenv("TITLE") or "Server"
CPU_THRESHOLD = os.getenv("CPU_THRESHOLD") or 80
MEMORY_THRESHOLD = os.getenv("MEMORY_THRESHOLD") or 80


def monitor_resources():
    msg = f"*{TITLE}*\n\n"

    # Warm-up call to set a baseline
    for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent"]):
        pass

    # Checking CPU, Memory, Disk Usage
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    msg += f"CPU Usage: {cpu_usage}%\n"
    msg += f"Memory Usage: {memory_usage}%\n"
    msg += f"Disk Usage: {disk_usage}%\n\n"

    # Top 5 CPU Processing
    processes = []
    for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent"]):
        processes.append(proc.info)

    cpu_sorted = sorted(processes, key=lambda p: p["cpu_percent"] or 0.0, reverse=True)

    msg += "*Top 5 CPU consuming processes:*\n"
    for process in cpu_sorted[:5]:
        cpu_percent = process["cpu_percent"] or 0.0
        msg += f"PID: {process['pid']}, Name: {process['name']},  CPU: {cpu_percent:.2f}%\n"
    msg += "\n"

    # Top 5 Memory Processing
    processes = []
    for proc in psutil.process_iter(["pid", "name", "username", "memory_percent"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    mem_sorted = sorted(
        processes, key=lambda p: p["memory_percent"] or 0.0, reverse=True
    )

    msg += "*Top 5 memory-consuming processes:\n*"
    for process in mem_sorted[:5]:
        mem_percent = process["memory_percent"] or 0.0
        msg += f"PID: {process['pid']}, Name: {process['name']}, Memory: {mem_percent:.2f}%\n"

    if cpu_usage > float(CPU_THRESHOLD) or memory_usage > float(MEMORY_THRESHOLD):
        success = send_to_telegram(msg)
        print("Sent to Telegram:", success, datetime.now())


def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    r = requests.post(url, data=payload)
    return r.ok


if __name__ == "__main__":
    monitor_resources()
