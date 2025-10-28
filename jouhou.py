import os
import requests
import httpx
from datetime import datetime
from openai import OpenAI
from zoneinfo import ZoneInfo

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
prompt = os.environ["PROMPT"]

# JSTの今日
JST = ZoneInfo("Asia/Tokyo")
now = datetime.now(JST)
today_str = now.strftime("%Y-%m-%d")

# 日本の営業日判定（jpholiday があれば祝日も考慮、無ければ土日だけ）
def is_jp_holiday(date_obj):
    try:
        jpholiday = import_module("jpholiday")
        return jpholiday.is_holiday(date_obj)
    except Exception:
        return False

is_weekday = now.weekday() < 5            # Mon=0 ... Sun=6
is_holiday = is_jp_holiday(now.date())    # 祝日（jpholidayが無ければ常にFalse）
is_business_day = is_weekday and not is_holiday

if not is_business_day:
    print(f"本日は休日のためスキップ: {today_str} JST (weekday={now.weekday()}, jp_holiday={is_holiday})")
    sys.exit(0)

client = OpenAI(api_key=OPENAI_API_KEY, timeout=httpx.Timeout(15.0, read=5.0, write=10.0, connect=3.0))

request_body = {
    "model": "gpt-5",
    "tools": [{"type": "web_search"}],
    "reasoning": {"effort": "high"}, 
    "input": [
        {"role": "user", "content": [{"type": "input_text", "text": prompt}]}
    ],
}

resp = client.responses.create(**request_body)

# Responses API のテキスト抽出（最初の出力を取得）
gpt_text = (getattr(resp, "output_text", "") or "").strip()

r = requests.post(WEBHOOK_URL, json={"content": gpt_text})

if r.status_code == 204:
    print("送信成功！")
else:
    print(f"送信失敗: {r.status_code} / {r.text}")
