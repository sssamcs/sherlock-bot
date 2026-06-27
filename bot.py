import asyncio
import os
import subprocess
import requests

BOT_TOKEN = "8570033777:AAGOC-Py-Zm1U9L82wP9TpLyyvp_i8j_qAk"
BASE_URL = f"https://telegram.org{BOT_TOKEN}/"

def make_telegram_request(method, payload):
    try:
        url = BASE_URL + method
        response = requests.post(url, data=payload, timeout=25)
        return response.json()
    except Exception as e:
        print(f"Request error: {e}")
        return None

async def run_sherlock(username):
    try:
        process = await asyncio.create_subprocess_exec(
            "python", "-m", "sherlock", username,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await process.communicate()
    except Exception as e:
        print(f"Sherlock execution error: {e}")

async def main():
    print("Sherlock Bot successfully started on Render...")
    offset = 0
    
    while True:
        try:
            res_data = make_telegram_request("getUpdates", {"offset": offset, "timeout": 20})
            
            if res_data and "result" in res_data:
                for update in res_data["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"].strip()
                        
                        if text == "/start":
                            make_telegram_request("sendMessage", {
                                "chat_id": chat_id,
                                "text": "🕵️‍♂️ **Welcome to Sherlock Bot!**\n\nSend me any username (without @), and I will check its existence on hundreds of websites.",
                                "parse_mode": "Markdown",
                                "disable_web_page_preview": "true"
                            })
                            continue
                            
                        username = text.replace("@", "").strip()
                        if " " in username or len(username) < 2:
                            make_telegram_request("sendMessage", {
                                "chat_id": chat_id,
                                "text": "❌ Please enter a valid username (one word)."
                            })
                            continue
                            
                        status = make_telegram_request("sendMessage", {
                            "chat_id": chat_id,
                            "text": f"🔍 Searching accounts for `{username}`. Please wait...",
                            "parse_mode": "Markdown"
                        })
                        
                        if not status or "result" not in status:
                            continue
                            
                        msg_id = status["result"]["message_id"]
                        result_file = f"{username}.txt"
                        
                        await run_sherlock(username)
                        
                        if os.path.exists(result_file):
                            with open(result_file, "r", encoding="utf-8") as file:
                                found_links = file.readlines()
                            os.remove(result_file)
                            
                            if found_links:
                                reply = f"🕵️‍♂️ **Found profiles for `{username}`:**\n\n" + "".join(found_links[:25])
                                make_telegram_request("editMessageText", {
                                    "chat_id": chat_id,
                                    "message_id": msg_id,
                                    "text": reply,
                                    "parse_mode": "Markdown",
                                    "disable_web_page_preview": "true"
                                })
                            else:
                                make_telegram_request("editMessageText", {
                                    "chat_id": chat_id,
                                    "message_id": msg_id,
                                    "text": "🤷‍♂️ No matches found."
                                })
                        else:
                            make_telegram_request("editMessageText", {
                                    "chat_id": chat_id,
                                    "message_id": msg_id,
                                    "text": "🤷‍♂️ No profiles discovered."
                                })
                                
        except Exception as e:
            print(f"Loop error: {e}")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
