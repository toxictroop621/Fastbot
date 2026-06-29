import asyncio
import re
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

keep_alive()

API_ID = 28300452
API_HASH = '7ad116378499f0ad2278dce2b28fbd28'
SESSION_STRING = os.environ.get('SESSION_STRING', '')

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r'🔤\s*Word:\s*(\w+)'))
async def instant_respond(event):
    try:
        if event.out:
            return
        word = event.pattern_match.group(1)
        if word.lower() == 'new':
            return
        await event.respond(word)
        print(f"⚡ {word}")
    except:
        pass

async def main():
    await client.start()
    print("\n✅ Bot running!\n")
    await client.run_until_disconnected()

asyncio.run(main())
