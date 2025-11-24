#!/usr/bin/env python3
import asyncio, os
from threading import Thread
from queue import Queue
from telethon import TelegramClient, events
from dotenv import load_dotenv
from ai import HybridAI
from self_heal import self_heal, auto_retry
from nft import convert_to_nft
from heartbeat import run_flask

# Live state
BOT_IS_ACTIVE = False

# ENVIRONMENT
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", 20))

# TELEGRAM CLIENT
try:
    client = TelegramClient("BotSession", API_ID, API_HASH)
except Exception as e:
    self_heal(f"TelegramClient init failed: {e}")
    raise e

# AI WORKER
mistral_queue = Queue()
ai_engine = HybridAI(memory_limit=MEMORY_LIMIT)

async def ai_worker():
    while True:
        event, prompt = mistral_queue.get()
        try:
            response = await ai_engine.generate(prompt)
            await event.respond(response)
        except Exception as e:
            self_heal(f"AI worker error: {e}")
            await event.respond("Fejl i AI. Self-heal aktiveret.")
        finally:
            mistral_queue.task_done()
        await asyncio.sleep(0.01)

# POST-PREPROMPTED LIVE-ONLY DECORATOR
def live_only(func):
    async def wrapper(*args, **kwargs):
        if not BOT_IS_ACTIVE: return
        try: return await func(*args, **kwargs)
        except Exception as e:
            self_heal(f"Live-only extension failed: {e}")
            return "(Fallback response)"
    return wrapper

# TELEGRAM COMMANDS
@client.on(events.NewMessage(pattern="/start"))
@live_only
async def start(event):
    await event.respond("/ask /nft /reset /ping /id - fully self-healed commands")

@client.on(events.NewMessage(pattern="/ask"))
@live_only
async def ask_ai(event):
    question = event.message.raw_text.replace("/ask", "").strip()
    if question: mistral_queue.put((event, question))
    else: await event.respond("Brug: /ask dit_spørgsmål")

@client.on(events.NewMessage(pattern="/nft"))
@live_only
async def nft_command(event):
    reply = await event.get_reply_message()
    if reply and reply.media:
        img_path = await reply.download_media()
        nft_file = convert_to_nft(img_path)
        if nft_file: await event.respond("NFT genereret", file=nft_file)
        else: await event.respond("Fejl ved NFT-konvertering")
    else: await event.respond("Svar på et billede")

@client.on(events.NewMessage(pattern="/reset"))
@live_only
async def reset_memory(event):
    ai_engine.reset_memory()
    await event.respond("Hukommelse nulstillet")

@client.on(events.NewMessage(pattern="/ping"))
@live_only
async def ping(event): await event.respond("Pong")

@client.on(events.NewMessage(pattern="/id"))
@live_only
async def user_id(event): await event.respond(f"{event.sender_id}")

# MAIN LOOP
async def main():
    global BOT_IS_ACTIVE
    BOT_IS_ACTIVE = True
    await client.start(bot_token=BOT_TOKEN)
    asyncio.create_task(ai_worker())
    await client.run_until_disconnected()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    asyncio.run(main())
