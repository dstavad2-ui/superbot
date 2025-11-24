#!/usr/bin/env python3
import asyncio
import logging
from telethon import TelegramClient, events
from PIL import Image
from flask import Flask
from threading import Thread
from queue import Queue

# -------------------------
# KONSTANTER
# -------------------------
API_ID = 14915416750
API_HASH = "Production configuration HASH"
BOT_TOKEN = "8261354099:AAEewnT0GDcOl5-ARokNVuO5i3zMuLyeG7g"
MEMORY_LIMIT = 20

# -------------------------
# LOGGING / SELF-HEAL
# -------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Bot")

def self_heal(msg):
    log.warning(f"[SELF-HEAL] {msg}")

# -------------------------
# HEARTBEAT SERVER
# -------------------------
app = Flask(__name__)
@app.route("/")
def alive():
    return "Bot online", 200
def run_flask():
    app.run(host="0.0.0.0", port=10000)

# -------------------------
# TELEGRAM CLIENT
# -------------------------
client = TelegramClient("BotSession", API_ID, API_HASH)

# -------------------------
# MISTRAL AI QUEUE + MEMORY
# -------------------------
mistral_queue = Queue()
mistral_memory = []

async def mistral_worker():
    while True:
        try:
            event, prompt = mistral_queue.get()
            mistral_memory.append(f"User: {prompt}")
            if len(mistral_memory) > MEMORY_LIMIT:
                mistral_memory.pop(0)
            context = "\n".join(mistral_memory)
            
            # Din Mistral backend integration her
            response = f"(Mistral svar baseret på kontekst:\n{context})"
            mistral_memory.append(f"Mistral: {response}")
            
            await event.respond(response)
        except Exception as e:
            self_heal(f"Mistral worker fejl: {e}")
            await event.respond("Fejl i Mistral AI. Self-heal aktiveret.")
        finally:
            mistral_queue.task_done()
        await asyncio.sleep(0.01)

# -------------------------
# KOMMANDOER
# -------------------------
@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond("/ask — Mistral AI\n/id — Din ID\n/ping — System check\n/nft — Konverter billede")

@client.on(events.NewMessage(pattern="/ask"))
async def ask_ai(event):
    question = event.message.raw_text.replace("/ask", "").strip()
    if not question:
        await event.respond("Brug: /ask dit_spørgsmål")
        return
    mistral_queue.put((event, question))

@client.on(events.NewMessage(pattern="/id"))
async def user_id(event):
    await event.respond(f"{event.sender_id}")

@client.on(events.NewMessage(pattern="/ping"))
async def ping(event):
    await event.respond("Pong")

@client.on(events.NewMessage(pattern="/nft"))
async def nft_convert(event):
    try:
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.respond("Svar på et billede")
            return
        img_path = await reply.download_media()
        Image.open(img_path).convert("RGB").save("nft.png")
        await event.respond("NFT genereret", file="nft.png")
    except Exception as e:
        self_heal(f"NFT fejl: {e}")
        await event.respond("Fejl under NFT-konvertering")

# -------------------------
# MAIN
# -------------------------
async def main():
    try:
        await client.start(bot_token=BOT_TOKEN)
        self_heal("Telethon kører")
        asyncio.create_task(mistral_worker())
        await client.run_until_disconnected()
    except Exception as e:
        self_heal(f"Telethon loop fejl: {e}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(main())
