# Election Scraper

Tento projekt slouží k zisku výsledků z parlamentních voleb konaných v roce 2017 ze stránek volby.cz.

### Instalace knihoven
Knihovny potřebné pro běh skriptu jsou uvedeny v souboru `requirements.txt`. Pro instalaci použijte:
`pip install -r requirements.txt`

### Spuštění skriptu
Skript se spouští ze systému příkazové řádky se dvěma argumenty:
1. URL adresu územního celku, který chcete scrapovat.
2. Název výstupního souboru (s příponou .csv).

Příklad spuštění:
`python main.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=10&xnumnuts=6102" "vysledky_jihlava.csv"`
