import os
import re
import httpx
from openai import OpenAI

#pobieranie htmla jako prawdziwa przegladarka
async def scrape_raw_html(url: str) -> str | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pl,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            return resp.text
    except Exception as e:
        print("HTTPX ERROR:", e)
        return None



#wycinanie tylko fragmentow z cena
def extract_price_fragments(html: str) -> str:
    if not html:
        return ""

    price_related = []
    keywords = ["price", "amount", "pln", "zł", "eur", "usd", "discount"]

    lines = html.split("\n")
    for line in lines:
        l = line.lower()
        if any(k in l for k in keywords):
            price_related.append(line.strip())

    #jak nie ma to html max 4000znakow wyslij do ai
    if not price_related:
        return html[:4000]

    #laczenie fragmentow i przzekazanie do ai
    fragment = "\n".join(price_related)
    return fragment[:5000]



#ai wyciaga cene z oczyszczonego htmla
def scrape_price_ai(fragment: str) -> float | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("NO OPENAI KEY FOUND")
        return None

    client = OpenAI(api_key=api_key)

    prompt = f"""
    You extract product prices from HTML fragments.

    Rules:
    - Return ONLY the numeric price (e.g. 129.99)
    - Use dot as decimal separator
    - Do NOT include currency symbols
    - If no valid price exists, reply ONLY "NONE"

    HTML fragment:
    {fragment}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
        )

        text = response.choices[0].message.content.strip()

        if text.upper() == "NONE":
            return None


        cleaned = re.findall(r"\d+[.,]?\d*", text)
        if not cleaned:
            return None

        val = cleaned[0].replace(",", ".")
        return float(val)

    except Exception as e:
        print("AI SCRAPER ERROR:", e)
        return None

import asyncio

def scrape_price(url: str) -> float | None:
    try:
        html = asyncio.run(scrape_raw_html(url))
    except RuntimeError:
        # # jak fastapi ma event loop uzyj nowy
        html = asyncio.new_event_loop().run_until_complete(scrape_raw_html(url))

    if not html:
        return None

    fragment = extract_price_fragments(html)
    return scrape_price_ai(fragment)
