import os
import requests
from datetime import datetime
from openai import OpenAI

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

DEFAULT_PROMPT = """
---

# Role

You are a **strict markets reporter**. **Use web browsing** to fact-check everything. **Cover only items that occurred today in Japan time (JST)**: `{{date_yyyy-mm-dd}}` (00:00–23:59 JST).

# Scope

Summarize **Japan and global equity-related news and price moves**, plus a small **other-assets** section.

# Must-Have Angles

1. **Japan equities overview:** Closing performance of **Nikkei / TOPIX / TSE Growth**, total **TSE turnover**, and **key drivers** (top sector contributors, **USD/JPY**, domestic & global rates, **US/China** markets, catalysts such as earnings/policy).
2. **Notable moves:** **5–10 Japan single names** (+/−5%+, YTD high/low, unusual volume, etc.) with **ticker**, **close-to-close %**, and a **50–100 Japanese-character reason** (company news, media report, analyst action, flow/technicals). Plus **2–3 other assets** (gold, WTI, FX, rates, major ETFs/crypto) with % change and brief basis.
3. **Today’s key events:** Up to **5** (macro data, policy, earnings, IPO/offerings), include time and figures vs. consensus when available.
4. **Tomorrow watch:** **1–2** items (only if space allows).

# Verification & Style Rules

* **Facts only**. Keep searching until confirmed; **no “unknown/unconfirmed.”** If an approximation is unavoidable, mark **(推定)**.
* **JST only** for “today.” Ignore items outside `{{date_yyyy-mm-dd}}` JST.
* **Citations:** End **each line** with `[Outlet/Time JST]` (e.g., `[Nikkei/15:10]`).
  For single-name stocks, prioritize **Kabutan** and **Nikkei**.
* **Numbers:** Half-width digits; **percent with 1 decimal** (e.g., `+1.2%`). Close-to-close unless specified.
* **Tone:** Concise, newsroom bullet style. No extra commentary beyond the template.
* **Length:** **≤ 2,000 characters** total.
* If sources conflict, prefer exchange/official or most reputable; be consistent.

# Output Template (fill in **Japanese** exactly in this shape)

```
【{{date_yyyy-mm-dd}} 市況まとめ】
・日本株：日経{{±x.x%}}/TOPIX{{±x.x%}}/グロース{{±x.x%}}。主因：{{要因1・要因2}}。［媒体/時刻］
・個別：{{銘柄}} {{±x.x%}}（{{50–100字の理由}}）。{{銘柄}} {{±x.x%}}（{{理由}}）。［媒体/時刻］
・他資産：金{{±x.x%}}、WTI{{±x.x%}}、USD/JPY {{xxx.x}}、米10年{{x.xx%}}。［媒体/時刻］
・イベント：{{イベント1}}、{{イベント2}}、{{イベント3}}。［媒体/時刻］
・明日：{{注目1}}、{{注目2}}。［媒体/時刻］
```

# Data Sources (examples)

* **Indices/turnover:** JPX, Nikkei Markets, QUICK
* **Individual stocks:** Kabutan, Nikkei
* **FX/rates/commodities:** Reuters, Bloomberg, CME/ICE, U.S. Treasury
* **Crypto/ETFs:** CoinDesk, Coinbase, issuer sites

# Reminders for the Model

* Use browsing for **all** figures and headlines.
* Keep every figure **traceable** to a cited source and **timestamped in JST**.
* Reasons for single-name moves must be **50–100 Japanese characters**.

"""

prompt = os.environ.get("PROMPT", DEFAULT_PROMPT)

client = OpenAI(api_key=OPENAI_API_KEY, timeout=60)

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
