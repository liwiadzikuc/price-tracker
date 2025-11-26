import os
import re
import asyncio
import httpx
from openai import OpenAI

from app.selenium_scraper import scrape_price_selenium

API_KEY = os.getenv("OPENAI_API_KEY")

async def scrape_raw_html(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code == 200:
                return response.text
            return None
    except Exception as e:
        print("HTTPX ERROR:", e)
        return None

PRICE_KEYWORDS = [
    "price",
    "final-price",
    "sale",
    "sale-price",
    "discount",
    "discounted",
    "deal",
    "promo",
    "promotion",
    "old-price",
    "regular-price",
    "retail",
    "current-price",
    "low-price",
    "best-price",
    "value",
    "amount",
    "cost",
    "cena",
    "promocja",
]

def extract_price_fragments(html: str) -> str:
    if not html:
        return ""
    html_lower = html.lower()
    lines = html_lower.splitlines()
    matched = []
    for line in lines:
        if any(keyword in line for keyword in PRICE_KEYWORDS):
            matched.append(line.strip())
    fragment = "\n".join(matched)
    #fragment = "\n".join([line for line in html.splitlines() if "price" in line.lower()])
    return fragment[:5000]


def scrape_price_ai(fragment: str) -> float | None:
    if not fragment:
        return None

    try:
        client = client = OpenAI()


        prompt = (
            "Extract the price from the following HTML snippet. "
            "Return only the number (no currency):\n\n"
            f"{fragment}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15
        )

        content = response.choices[0].message.content
        content = content.replace(",", ".")
        match = re.search(r"\d{2,4}\.\d{2}", content)
        if match:
            return float(match.group(0))

        return None

    except Exception as e:
        print("AI SCRAPER ERROR:", e)
        return None

async def scrape_price_async(url: str) -> float | None:
    print("\n--- AI SCRAPER START ---")

    # 1 ai scraper
    html = await scrape_raw_html(url)
    if html:
        fragment = extract_price_fragments(html)
        price_ai = scrape_price_ai(fragment)

        print("AI SCRAPER RESULT:", price_ai)

        if price_ai is not None:
            print("--- AI SCRAPER SUCCESS ---")
            return price_ai

    print("--- AI SCRAPER FAILED, switching to SELENIUM ---")

    # 2 selenium
    price_browser = scrape_price_selenium(url)
    print("SELENIUM RESULT:", price_browser)
    return price_browser

def scrape_price(url: str) -> float | None:
    return asyncio.run(scrape_price_async(url))
