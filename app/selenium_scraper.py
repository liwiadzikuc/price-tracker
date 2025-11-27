import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

def scrape_price_selenium(url: str) -> float | None:
    print("=== SELENIUM START ===")
    print("URL:", url)

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")


    random_user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"--user-agent={random_user_agent}")

    driver = uc.Chrome(options=options, headless=False)

    try:
        driver.get(url)
        time.sleep(5)  # JS / Cloudflare potrzebuje chwili

        # eobuwie inaczej dziala
        if "eobuwie" in url:
            try:
                final_price = driver.find_element(By.CSS_SELECTOR, "[data-test-id='final-price']").text
                final_price = final_price.replace("zł", "").replace(",", ".").strip()
                return float(re.findall(r"\d{2,4}\.\d{2}", final_price)[0])
            except:
                print("Eobuwie: price selector not found")

        # reszta
        full_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        match = re.search(r"\d{2,4}[.,]\d{2}", full_text)
        if match:
            return float(match.group(0).replace(",", "."))

        print("NO PRICE FOUND")
        return None

    except Exception as e:
        print("SELENIUM ERROR:", e)
        return None

    finally:
        try:
            driver.quit()
        except:
            pass
