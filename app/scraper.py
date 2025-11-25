import requests
from bs4 import BeautifulSoup
import re
#dla enrage html
def scrape_price(url: str)-> float | None:
    html=requests.get(url).text
    soup=BeautifulSoup(html,"html.parser")
    price=soup.find("span",class_="money") #enrage
    #price = soup.find("span", attrs={"data-qa-anchor": "productItemPrice"}) #bershka

    if price is None:
        return None
    price_txt=price.text

    match = re.search(r"\d+(\.\d+)?", price_txt)
    if not match:
        return None
    return float(match.group(0))
