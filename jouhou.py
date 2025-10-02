import os
import requests
from openai import OpenAI

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

DEFAULT_PROMPT = """バナナは何色？
"""

prompt = os.environ.get("PROMPT", DEFAULT_PROMPT)

client = OpenAI(api_key=OPENAI_API_KEY)

request_body = {
    "model": "gpt-5",
    "input": [
        {"role": "user", "content": [{"type": "input_text", "text": prompt}]}
    ],
}

resp = client.responses.create(**request_body)

# Responses API のテキスト抽出（最初の出力を取得）
gpt_text = (getattr(resp, "output_text", "") or "").strip()

# --- Discord Webhook 送信（2000字分割対応）---
MAX = 2000
chunks = [gpt_text[i:i+MAX] for i in range(0, len(gpt_text), MAX)] or ["（空）"]

ok = True
for i, ch in enumerate(chunks, 1):
    payload = {"content": ch if len(chunks) == 1 else f"({i}/{len(chunks)})\n{ch}"}
    r = requests.post(WEBHOOK_URL, json=payload, timeout=10)

r = requests.post(WEBHOOK_URL, json={"content": gpt_text})

if r.status_code == 204:
    print("送信成功！")
else:
    print(f"送信失敗: {r.status_code} / {r.text}")
