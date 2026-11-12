import os, requests

key = ""
for line in open(".env", encoding="utf-8-sig").read().splitlines():
    if line.strip().startswith("GEMINI_API_KEY"):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")

print("prefix:", repr(key[:4]), "| length:", len(key))

for model in ["gemini-3.8-flash", "gemini-3.5-flash-lite"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"role": "user", "parts": [{"text": "Say hello in one word"}]}]}
    try:
        r = requests.post(url, json=body, timeout=25,
                          headers={"x-goog-api-key": key, "Content-Type": "application/json"})
        print(model, "->", r.status_code)
        print(r.text[:400])
    except Exception as e:
        print(model, "-> EXCEPTION:", type(e).__name__, e)
    print("-" * 40)