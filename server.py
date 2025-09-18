# server.py
import os
import threading
from bot import main as run_bot  # your bot.main (blocking) function
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running on Render!"

# Start the bot in a daemon thread as soon as this module is imported.
# This ensures the web server (gunicorn) binds the port immediately,
# while the bot runs in background.
def _start_bot_thread():
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

# Start the bot thread right away (when gunicorn imports this module).
_start_bot_thread()
