"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Markéta Zemková
"""

import sys
import csv
import time
import requests
from bs4 import BeautifulSoup

def ziskej_soup(url: str) -> BeautifulSoup:
    """Stáhne HTML obsah s maskováním prohlížeče a ošetřením chyb."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "cs-CZ,cs;q=0.9",
        "Referer": "https://www.volby.cz/",
        "Connection": "keep-alive"
    }
    
    try:
        # Malá pauza, abychom nebyli pro server příliš agresivní
        time.sleep(0.5)
        odpoved = requests.get(url, headers=headers, timeout=10)
        
        if odpoved.status_code == 571:
            print("CHYBA 571: Server nás blokuje. Zkus se připojit přes mobilní hotspot.")
            sys.exit(1)
            
        odpoved.raise_for_status()
        return BeautifulSoup(odpoved.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"CHYBA: Nepodařilo se načíst stránku: {e}")
        sys.exit(1)

def ziskej_seznam_obci(soup: BeautifulSoup) -> list:
    """Vytáhne kód, název a URL všech obcí z tabulky okresu."""
    seznam_obci = []
    radky = soup.find_all("tr")
    # Základ URL pro relativní odkazy
    base_url = "https://www.volby.cz/pls/ps2017nss/"

    for radek in radky:
        td_kod = radek.find("td", {"class": "cislo"})
        if td_kod and td_kod.text != "-":
            a_tag = td_kod.find("a")
            if a_tag:
                seznam_obci.append({
                    "code": td_kod.text,
                    "location": radek.find_all("td")[1].text,
                    "url": base_url + a_tag["href"]
                })
    return seznam_obci

def ziskej_data_obce(url_obce: str) -> dict:
    """Stáhne podrobná data o hlasování z detailu obce."""
    soup = ziskej_soup(url_obce)
    
    def cisti(text):
        return text.replace('\xa0', '').replace(' ', '').strip()

    vysledky = {
        "registered": cisti(soup.find("td", {"headers": "sa2"}).text),
        "envelopes": cisti(soup.find("td", {"headers": "sa3"}).text),
        "valid": cisti(soup.find("td", {"headers": "sa6"}).text)
    }

    # Hledání politických stran a jejich hlasů
    radky = soup.find_all("tr")
    for radek in radky:
        nazev_td = radek.find("td", {"class": "overflow_name"})
        if nazev_td:
            # Hlasy jsou v předposledním td (index -2)
            hlasy = cisti(radek.find_all("td")[-2].text)
            vysledky[nazev_td.text] = hlasy

    return vysledky

def zapis_do_csv(nazev_souboru: str, data: list):
    """Uloží kompletní seznam dat do CSV souboru."""
    if not data:
        return
    hlavicka = data[0].keys()
    with open(nazev_souboru, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=hlavicka)
        writer.writeheader()
        writer.writerows(data)

def main():
    if len(sys.argv) != 3:
        print("POUŽITÍ: python3 main.py <URL> <vysledek.csv>")
        sys.exit(1)

    url, soubor = sys.argv[1], sys.argv[2]
    
    if "volby.cz" not in url:
        print("CHYBA: Neplatná adresa webu volby.cz")
        sys.exit(1)

    print(f"NAČÍTÁM SEZNAM OBCÍ Z URL...")
    hlavni_soup = ziskej_soup(url)
    obce = ziskej_seznam_obci(hlavni_soup)
    
    if not obce:
        print("CHYBA: Nepodařilo se najít žádné obce. Zkontroluj správnost URL.")
        sys.exit(1)

    print(f"NALEZENO {len(obce)} OBCÍ. ZAČÍNÁM STAHOVAT DATA...")

    finalni_seznam = []
    for index, obec in enumerate(obce, 1):
        print(f"[{index}/{len(obce)}] Zpracovávám: {obec['location']}")
        detaily = ziskej_data_obce(obec["url"])
        
        # Spojení informací do jednoho řádku
        finalni_seznam.append({
            "code": obec["code"],
            "location": obec["location"],
            **detaily
        })

    print(f"UKLÁDÁM DATA DO SOUBORU: {soubor}")
    zapis_do_csv(soubor, finalni_seznam)
    print("VŠE HOTOVO!")

if __name__ == "__main__":
    main()
