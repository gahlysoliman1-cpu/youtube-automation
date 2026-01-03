import os
import requests
import json

RESULTS = {}

def mark(name, status, reason, details=""):
    RESULTS[name] = {
        "status": status,
        "reason": reason,
        "details": details[:300]
    }

def safe_request(method, url, **kwargs):
    try:
        return requests.request(method, url, timeout=15, **kwargs)
    except Exception as e:
        return str(e)

def test_openai():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        mark("OPENAI_API_KEY", "FAIL", "Missing API Key")
        return

    r = safe_request(
        "GET",
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {key}"}
    )

    if isinstance(r, str):
        mark("OPENAI_API_KEY", "FAIL", "Network Error", r)
    elif r.status_code == 200:
        mark("OPENAI_API_KEY", "OK", "Key valid – models accessible")
    elif r.status_code == 401:
        mark("OPENAI_API_KEY", "FAIL", "Invalid API Key", r.text)
    elif r.status_code == 403:
        mark("OPENAI_API_KEY", "FAIL", "Billing or permission issue", r.text)
    else:
        mark("OPENAI_API_KEY", "FAIL", f"HTTP {r.status_code}", r.text)

def test_gemini():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        mark("GEMINI_API_KEY", "FAIL", "Missing API Key")
        return

    r = safe_request(
        "GET",
        f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    )

    if isinstance(r, str):
        mark("GEMINI_API_KEY", "FAIL", "Network Error", r)
    elif r.status_code == 200:
        mark("GEMINI_API_KEY", "OK", "API enabled & key valid")
    elif r.status_code == 403:
        mark("GEMINI_API_KEY", "FAIL", "API not enabled on project", r.text)
    else:
        mark("GEMINI_API_KEY", "FAIL", f"HTTP {r.status_code}", r.text)

def test_groq():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        mark("GROQ_API_KEY", "FAIL", "Missing API Key")
        return

    r = safe_request(
        "GET",
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {key}"}
    )

    if isinstance(r, str):
        mark("GROQ_API_KEY", "FAIL", "Network Error", r)
    elif r.status_code == 200:
        mark("GROQ_API_KEY", "OK", "Key valid")
    elif r.status_code == 401:
        mark("GROQ_API_KEY", "FAIL", "Invalid API Key", r.text)
    else:
        mark("GROQ_API_KEY", "FAIL", f"HTTP {r.status_code}", r.text)

def test_pixabay():
    r = safe_request(
        "GET",
        "https://pixabay.com/api/",
        params={"key": os.getenv("PIXABAY_API_KEY"), "q": "test", "per_page": 1}
    )

    if isinstance(r, str):
        mark("PIXABAY_API_KEY", "FAIL", "Network Error", r)
    elif r.status_code == 200:
        mark("PIXABAY_API_KEY", "OK", "Key valid")
    elif r.status_code == 403:
        mark("PIXABAY_API_KEY", "FAIL", "Invalid or blocked key", r.text)
    else:
        mark("PIXABAY_API_KEY", "FAIL", f"HTTP {r.status_code}", r.text)

def test_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat:
        mark("TELEGRAM", "FAIL", "Missing token or chat id")
        return

    r = safe_request(
        "POST",
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat, "text": "🧪 Verbose API Test OK"}
    )

    if isinstance(r, str):
        mark("TELEGRAM", "FAIL", "Network Error", r)
    elif r.status_code == 200:
        mark("TELEGRAM", "OK", "Message sent successfully")
    elif r.status_code == 403:
        mark("TELEGRAM", "FAIL", "Bot not allowed in chat", r.text)
    else:
        mark("TELEGRAM", "FAIL", f"HTTP {r.status_code}", r.text)

def test_youtube():
    r = safe_request(
        "GET",
        "https://www.googleapis.com/youtube/v3/channels",
        params={
            "part": "snippet",
            "id": os.getenv("YT_CHANNEL_ID"),
            "key": os.getenv("YOUTUBE_API_KEY")
        }
    )

    if isinstance(r, str):
        mark("YOUTUBE_API_KEY", "FAIL", "Network Error", r)
    elif r.status_code == 200:
        mark("YOUTUBE_API_KEY", "OK", "Read access OK")
    else:
        mark("YOUTUBE_API_KEY", "FAIL", f"HTTP {r.status_code}", r.text)

def main():
    print("🔍 Running VERBOSE API Tests\n")

    test_openai()
    test_gemini()
    test_groq()
    test_pixabay()
    test_telegram()
    test_youtube()

    print("RESULTS")
    print("=" * 40)
    for k, v in RESULTS.items():
        print(f"{k}: {v['status']} | {v['reason']}")

    with open("test_results_verbose.json", "w") as f:
        json.dump(RESULTS, f, indent=2)

if __name__ == "__main__":
    main()
