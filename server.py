import os
import threading
from flask import Flask
from bot import main  # tumhara bot.py ka main function import kiya

app = Flask(__name__)

# ✅ Dummy web route (Render ko port binding chahiye hota hai)
@app.route("/")
def home():
    return "Bot is running on Render!"

def run_bot():
    main()

if __name__ == "__main__":
    # Bot ek alag thread me run karega
    t = threading.Thread(target=run_bot)
    t.start()

    # Flask server port 10000 pe chalega
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
