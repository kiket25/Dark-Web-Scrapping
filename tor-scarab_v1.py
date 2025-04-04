import requests
from bs4 import BeautifulSoup

#Proxies to use tor
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

 # URL of a site .onionurl
url = input('Enter the url to scrap = ')
 # Make the tor request 
headers = {"User-Agent": "Mozilla/5.0"}

try:
    r = requests.get(url, proxies=proxies, headers=headers, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')

    titles = soup.find_all(["h1", "h2", "title"])

    for title in titles:
        print("Title founded:", title.get_text(strip=True))
except requests.exceptions.RequestException as e:
    print("Error:", e)
