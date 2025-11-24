from flask import Flask
from self_heal import self_heal

app = Flask(__name__)

@app.route("/")
def alive(): return "Bot online", 200

def run_flask():
    try: app.run(host="0.0.0.0", port=10000)
    except Exception as e: self_heal(f"Heartbeat crashed: {e}")
