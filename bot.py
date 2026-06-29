import asyncio
import re
import os
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

# ========== TEN THINGS - DUCKDUCKGO SEARCH ==========
def search_answer(topic, hint):
    try:
        clean_hint = hint.replace('⁎', '').strip()
        query = f"{topic} {clean_hint}"
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
        
        if data.get('Answer'):
            return data['Answer'][:80]
        
        return None
    except:
        return None

@client.on(events.NewMessage(from_users='TenThings_Bot'))
async def auto_answer(event):
    try:
        text = event.message.text
        lines = text.strip().split('\n')
        topic = lines[0].strip()
        
        hints = re.findall(r'\d+:\s*([^\n]+)', text)
        
        if not hints:
            return
        
        print(f"\n🎯 {topic}")
        
        for hint in hints:
            clean = hint.strip()
            
            if len(clean) < 5:
                continue
            
            print(f"❓ {clean}")
            
            answer = search_answer(topic, clean)
            
            if answer:
                print(f"✅ {answer}")
                await event.respond(answer)
                await asyncio.sleep(0.5)
            else:
                print(f"❌ No result")
    
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await client.start()
    print("\n🤖 BOT RUNNING!")
    print("⚡ FastWrite: AUTO")
    print("🔍 TenThings: DuckDuckGo Search")
    print("📱 Works anywhere, Phone OFF = OK!\n")
    await client.run_until_disconnected()

asyncio.run(main())
