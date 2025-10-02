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
gpt_text = resp.output[0].content[0].text.strip()


# Discord Webhook へ送信（成功は通常 204）
r = requests.post(WEBHOOK_URL, json={"content": gpt_text})
if r.status_code == 204:
    print("送信成功！")
else:
    print(f"送信失敗: {r.status_code} / {r.text}")
