#!/usr/bin/env python3
"""
NTRLI' SUPERBOT - COMPLETE ECOSYSTEM ORCHESTRATOR
Integrates: Catalog + AI + NFT + Subscriptions + Self-Heal + Heartbeat
You are the algorithm. Everything is controlled by you.
"""

import asyncio, os
from threading import Thread
from queue import Queue
from telethon import TelegramClient, events
from dotenv import load_dotenv
from self_heal import self_heal, auto_retry
from heartbeat import run_flask

# IMPORT ECOSYSTEM LAYERS
from ai_ecosystem import EcosystemAI
from catalog import CatalogManager
from subscriptions import SubscriptionManager
from admin_panel import AdminPanel
from nft_ecosystem import NFTEcosystem

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

# ECOSYSTEM INITIALIZATION
print("[ECOSYSTEM] Initializing layers...")

ai_engine = EcosystemAI(memory_limit=MEMORY_LIMIT)
catalog = CatalogManager(ai_engine=ai_engine)
subscriptions = SubscriptionManager()
nft_layer = NFTEcosystem(catalog_manager=catalog)
admin = AdminPanel(catalog, subscriptions, nft_layer, ai_engine)

# QUEUES
mistral_queue = Queue()
nft_queue = Queue()

print("[ECOSYSTEM] All layers live. Bot ready.")

# AI WORKER THREAD
async def ai_worker():
    """Process AI requests from queue"""
    while True:
        try:
            event, prompt = mistral_queue.get()
            response = await ai_engine.generate(prompt, context_user_id=event.sender_id)
            await event.respond(response)
        except Exception as e:
            self_heal(f"AI worker error: {e}")
            try:
                await event.respond("⚠️ AI error. Self-heal activated.")
            except:
                pass
        finally:
            mistral_queue.task_done()
        await asyncio.sleep(0.01)

# NFT WORKER THREAD
async def nft_worker():
    """Process NFT conversion requests from queue"""
    while True:
        try:
            event, img_path, product_name, section_name = nft_queue.get()
            nft_id, nft_file = nft_layer.generate_product_nft(product_name, section_name, "product_specs")
            
            if nft_id and nft_file:
                # Assign to user if subscriber
                sub = subscriptions.get_subscription(event.sender_id)
                if sub:
                    nft_layer.assign_nft_ownership(nft_id, event.sender_id)
                
                await event.respond(f"✅ NFT Generated: {nft_id}\n🎨 Asset ready")
                if os.path.exists(nft_file):
                    await event.respond(file=nft_file)
            else:
                await event.respond("❌ NFT generation failed")
        except Exception as e:
            self_heal(f"NFT worker error: {e}")
            try:
                await event.respond("⚠️ NFT error. Self-heal activated.")
            except:
                pass
        finally:
            nft_queue.task_done()
        await asyncio.sleep(0.01)

def live_only(func):
    """Decorator: only run if bot is active"""
    async def wrapper(*args, **kwargs):
        if not BOT_IS_ACTIVE: return
        try: 
            return await func(*args, **kwargs)
        except Exception as e:
            self_heal(f"Live-only extension failed: {e}")
    return wrapper

# ============================================================================
# PUBLIC COMMANDS
# ============================================================================

@client.on(events.NewMessage(pattern="/start"))
@live_only
async def start(event):
    msg = """
🌒   N T R L I '   S E L E C T I O N
━━━━━━━━━━━━━━━━━━━━━━━━

**Det her er ikke bare noget du tilvælger, det er noget du genkender.**

📋 /menu - Overblik over menuen
💎 /premium - FÅ NTRLI' PREMIUM
💬 /ask - Spørg AI en ting
🎨 /nft - Generer NFT
❓ /info - Levering & åbningstider
📞 /contact - Find mig

━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await event.respond(msg)

@client.on(events.NewMessage(pattern="/menu"))
@live_only
async def menu(event):
    try:
        menu_text = catalog.render_menu()
        await event.respond(menu_text)
    except Exception as e:
        self_heal(f"Menu command failed: {e}")
        await event.respond("Fejl ved indlæsning af menu")

@client.on(events.NewMessage(pattern="/ask"))
@live_only
async def ask_ai(event):
    try:
        question = event.message.raw_text.replace("/ask", "").strip()
        if question:
            mistral_queue.put((event, question))
            await event.respond("⏳ AI thinking...")
        else:
            await event.respond("Usage: /ask dit_spørgsmål")
    except Exception as e:
        self_heal(f"Ask command failed: {e}")

@client.on(events.NewMessage(pattern="/nft"))
@live_only
async def nft_command(event):
    try:
        reply = await event.get_reply_message()
        if reply and reply.media:
            img_path = await reply.download_media()
            
            # Get product context from message
            product_name = "NTRLI' Product"
            section_name = "Premium Selection"
            
            nft_queue.put((event, img_path, product_name, section_name))
            await event.respond("⏳ Generating NFT...")
        else:
            await event.respond("Reply to an image with /nft to generate NFT")
    except Exception as e:
        self_heal(f"NFT command failed: {e}")
        await event.respond("NFT generation error")

@client.on(events.NewMessage(pattern="/premium"))
@live_only
async def premium(event):
    try:
        sub = subscriptions.get_subscription(event.sender_id)
        if sub:
            renewal = subscriptions.get_renewal_date(event.sender_id)
            msg = f"""
✨ **DU ER PREMIUM**

Tier: {sub['tier']}
Fornyer om: {renewal} dage

🌀 /pause_sub - Sæt på pause
🌀 /cancel_sub - Opsig når som helst

━━━━━━━━━━━━━━━━━━━━━━━━
Ingen gebyrer. Hurtigt og uden gebyr.
            """
            await event.respond(msg)
        else:
            msg = """
💎 **FÅ NTRLI' PREMIUM**
━━━━━━━━━━━━━━━━━━━━━━━━

🔒 **Premium Standard**
200 kr/måned · 1500 kr/år

✅ Eksklusive tilbud 💰
✅ Early access til weed 🍂
✅ Billigere røg fra dag 1 💵
✅ Forum adgang 🏛
✅ 1500 stjerner / måned

━━━━━━━━━━━━━━━━━━━━━━━━

⭐ **Premium Advanced**
400 kr/måned · 1500 kr/år

✅ Unlimited early access 📛
✅ Eksklusive micro-batches ❤️‍🔥
✅ Extended forum access ⚡️
✅ 3000 stjerner / måned

━━━━━━━━━━━━━━━━━━━━━━━━

📧 PM for subscription detaljer
            """
            await event.respond(msg)
    except Exception as e:
        self_heal(f"Premium command failed: {e}")

@client.on(events.NewMessage(pattern="/info"))
@live_only
async def info(event):
    msg = """
🚚   L E V E R I N G   &   I N F O
━━━━━━━━━━━━━━━━━━━━━━━━

📦 Levering fra 500 kr
🏠 Selvhent i Lindholm
📞 Skriv, vi finder ud af det

🕜   Å B N I N G S T I D E R
━━━━━━━━━━━━━━━━━━━━━━━━

Man – Tor · 13:30 – 21:00
Fre – Lør · 15:30 – 01:00
Søndag · Lukket

🛡️ **Fokus på sikkerhed & harm reduction**

Alle produkter udvælges med omtanke.
Intet overflødigt intet tilfældigt.
    """
    await event.respond(msg)

@client.on(events.NewMessage(pattern="/contact"))
@live_only
async def contact(event):
    msg = """
📞   K O N T A K T
━━━━━━━━━━━━━━━━━━━━━━━━

💬 PM mig: @Sir_NTRLI_II
🔗 Premium: https://t.me/+z7AO7r1c16BiODZk
🔗 Advanced: https://t.me/+gnx2ZsLT-epmY2U0
    """
    await event.respond(msg)

@client.on(events.NewMessage(pattern="/pause_sub"))
@live_only
async def pause_sub(event):
    if subscriptions.pause_subscription(event.sender_id):
        await event.respond("✅ Subscription sat på pause\n🌀 /resume_sub")
    else:
        await event.respond("❌ Ingen aktiv subscription")

@client.on(events.NewMessage(pattern="/resume_sub"))
@live_only
async def resume_sub(event):
    if subscriptions.resume_subscription(event.sender_id):
        await event.respond("✅ Subscription genoptaget")
    else:
        await event.respond("❌ Ingen paused subscription")

@client.on(events.NewMessage(pattern="/cancel_sub"))
@live_only
async def cancel_sub(event):
    if subscriptions.cancel_subscription(event.sender_id):
        await event.respond("✅ Subscription opsagt")
    else:
        await event.respond("❌ Ingen aktiv subscription")

# ============================================================================
# ADMIN COMMANDS
# ============================================================================

@client.on(events.NewMessage(pattern="/admin"))
@live_only
async def admin_command(event):
    try:
        command_text = event.message.raw_text
        await admin.handle_admin_command(event, command_text)
    except Exception as e:
        self_heal(f"Admin command error: {e}")

# ============================================================================
# MAIN LOOP
# ============================================================================

async def main():
    global BOT_IS_ACTIVE
    BOT_IS_ACTIVE = True
    print("[ECOSYSTEM] Bot starting...")
    await client.start(bot_token=BOT_TOKEN)
    print("[ECOSYSTEM] Bot online. All systems live.")
    asyncio.create_task(ai_worker())
    asyncio.create_task(nft_worker())
    await client.run_until_disconnected()

if __name__ == "__main__":
    print("[ECOSYSTEM] Starting NTRLI' Superbot Ecosystem...")
    Thread(target=run_flask).start()
    asyncio.run(main())
