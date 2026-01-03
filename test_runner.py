import os
import requests
import json
import time

RESULTS = {}

def mark(name, ok, info=""):
    RESULTS[name] = {
        "status": "OK" if ok else "FAIL",
        "info": info
    }

def test_openai():
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say OK"}]
            },
            timeout=10
        )
        mark("OPENAI_API_KEY", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("OPENAI_API_KEY", False, str(e))

def test_gemini():
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={os.environ['GEMINI_API_KEY']}",
            json={"contents":[{"parts":[{"text":"Say OK"}]}]},
            timeout=10
        )
        mark("GEMINI_API_KEY", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("GEMINI_API_KEY", False, str(e))

def test_groq():
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": "Say OK"}]
            },
            timeout=10
        )
        mark("GROQ_API_KEY", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("GROQ_API_KEY", False, str(e))

def test_pexels():
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search?query=nature&per_page=1",
            headers={"Authorization": os.environ["PEXELS_API_KEY"]},
            timeout=10
        )
        mark("PEXELS_API_KEY", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("PEXELS_API_KEY", False, str(e))

def test_pixabay():
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={
                "key": os.environ["PIXABAY_API_KEY"],
                "q": "nature",
                "per_page": 1
            },
            timeout=10
        )
        mark("PIXABAY_API_KEY", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("PIXABAY_API_KEY", False, str(e))

def test_unsplash():
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos?query=nature&per_page=1",
            headers={"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"},
            timeout=10
        )
        mark("UNSPLASH_ACCESS_KEY", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("UNSPLASH_ACCESS_KEY", False, str(e))

def test_news():
    try:
        r = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "apiKey": os.environ["NEWS_API"],
                "country": "us",
                "pageSize": 1
            },
            timeout=10
        )
        mark("NEWS_API", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("NEWS_API", False, str(e))

def test_telegram():
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage",
            json={
                "chat_id": os.environ["TELEGRAM_CHAT_ID"],
                "text": "✅ API Test Runner: Telegram OK"
            },
            timeout=10
        )
        mark("TELEGRAM", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("TELEGRAM", False, str(e))

def test_youtube_api_key():
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "part": "snippet",
                "id": os.environ["YT_CHANNEL_ID"],
                "key": os.environ["YOUTUBE_API_KEY"]
            },
            timeout=10
        )
        mark("YOUTUBE_API_KEY", r.status_code == 200, r.text[:200])
    except Exception as e:
        mark("YOUTUBE_API_KEY", False, str(e))

def main():
    print("🚀 Running API Tests...\n")
    test_openai()
    test_gemini()
    test_groq()
    test_pexels()
    test_pixabay()
    test_unsplash()
    test_news()
    test_telegram()
    test_youtube_api_key()

    print("\n📊 RESULTS\n" + "="*40)
    for k, v in RESULTS.items():
        print(f"{k}: {v['status']}")

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2)

    print("\n📁 Saved: test_results.json")

if __name__ == "__main__":
    main()
