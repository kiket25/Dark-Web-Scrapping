import requests
import time
import random
import sqlite3
import re
import nltk
from bs4 import BeautifulSoup
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

# Configurar proxies para Tor
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Configurar cabeceras
headers = {"User-Agent": "Mozilla/5.0"}

# Lista de palabras clave sospechosas
keywords = ["exploit", "carding", "malware", "hack", "attack", "breach", "leak", "bitcoin", "drugs"]

# Inicializar análisis de sentimiento
sia = SentimentIntensityAnalyzer()

# Base de datos para almacenar datos
conn = sqlite3.connect('darknet_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS scraped_data (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT, 
                  title TEXT, 
                  content TEXT,
                  sentiment_score REAL,
                  detected_keywords TEXT)''')

conn.commit()

def extract_data(url):
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        titles = [title.get_text(strip=True) for title in soup.find_all(["h1", "h2", "title"])]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]

        content = " ".join(paragraphs)
        sentiment_score = sia.polarity_scores(content)['compound']
        detected_keywords = [word for word in keywords if re.search(r'\b' + word + r'\b', content, re.IGNORECASE)]
        
        cursor.execute("INSERT INTO scraped_data (url, title, content, sentiment_score, detected_keywords) VALUES (?, ?, ?, ?, ?)",
                       (url, ", ".join(titles), content, sentiment_score, ", ".join(detected_keywords)))
        conn.commit()

        print(f"Scraped: {url} | Sentiment: {sentiment_score} | Keywords: {detected_keywords}")
        
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return []


def crawl(url, depth=2):
    visited = set()
    queue = [(url, 0)]
    
    while queue:
        current_url, current_depth = queue.pop(0)
        if current_url in visited or current_depth > depth:
            continue
        
        visited.add(current_url)
        new_links = extract_data(current_url)
        time.sleep(random.uniform(3, 7))  # Evita detección
        
        for link in new_links:
            queue.append((link, current_depth + 1))


if __name__ == "__main__":
    start_url = input("Enter the .onion URL to crawl: ")
    crawl(start_url, depth=3)
    print("Scraping completed. Data stored in darknet_data.db")

