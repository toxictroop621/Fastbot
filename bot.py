
import asyncio
import re
import os
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread
import urllib.parse
import urllib.request
import json

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

print(f"Session string exists: {bool(SESSION_STRING)}")
print(f"Session length: {len(SESSION_STRING)}")

if not SESSION_STRING:
    print("❌ NO SESSION STRING! Check Render environment variables!")
    sys.exit(1)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ========== FAST WRITE GAME ==========
@client.on(events.NewMessage(pattern=r'🔤\s*Word:\s*(\w+)'))
async def word_game(event):
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

# ========== TEN THINGS - DETECT * PATTERN ==========
def search_answer(query):
    try:
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode('utf-8'))
        
        if data.get('AbstractText'):
            return data['AbstractText'].split('.')[0][:80]
        
        if data.get('RelatedTopics'):
            for topic in data['RelatedTopics']:
                if 'Text' in topic:
                    text = re.sub(r'<[^>]+>', '', topic['Text'])
                    answer = text.split(' - ')[0].strip()
                    if len(answer) > 2:
                        return answer[:80]
        
        return None
    except:
        return None

@client.on(events.NewMessage(from_users='TenThings_Bot'))
async def ten_things_answer(event):
    try:
        text = event.message.text
        
        if '*' not in text and '⁎' not in text:
            return
        
        print(f"\n🎮 GAME DETECTED!")
        print(f"📝 {text[:100]}")
        
        lines = text.strip().split('\n')
        topic = lines[0].strip()
        topic = re.sub(r'^\d+[\.\)]\s*', '', topic)
        
        hints = []
        for line in lines:
            if '*' in line or '⁎' in line:
                clean = re.sub(r'^\d+[\.:\)]\s*', '', line)
                hints.append(clean.strip())
        
        if not hints:
            return
        
        print(f"📌 Topic: {topic}")
        
        for hint in hints:
            clean_hint = hint.replace('*', '').replace('⁎', '').strip()
            
            if len(clean_hint) < 2:
                continue
            
            print(f"🔍 {clean_hint}")
            
            answer = search_answer(f"{topic} {clean_hint}")
            
            if answer:
                print(f"✅ {answer}")
                await event.respond(answer)
                await asyncio.sleep(0.3)
            else:
                print(f"❌ No answer")
    
    except Exception as e:
        print(f"Error: {e}")

async def main():
    try:
        print("Connecting to Telegram...")
        await client.start()
        print("\n✅ CONNECTED TO TELEGRAM!")
        print("🤖 Bot is ACTIVE!")
        print("="*50)
        print("⚡ FastWrite: AUTO")
        print("🎮 TenThings: AUTO")
        print("="*50 + "\n")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

asyncio.run(main())
