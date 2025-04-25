import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import chromadb
from chromadb.config import Settings

# Initialize persistent ChromaDB 
chroma_client = chromadb.Client(Settings(persist_directory="./chroma_db"))
collection = chroma_client.get_or_create_collection(name="web_content")

# Text cleaning
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

# Static scraping
def scrape_static(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return clean_text(soup.get_text())
    except Exception as e:
        print("Static scrape error:", e)
        return ""

#  Dynamic scraping
def scrape_dynamic(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            content = page.content()
            browser.close()
            soup = BeautifulSoup(content, "html.parser")
            return clean_text(soup.get_text())
    except Exception as e:
        print("Dynamic scrape error:", e)
        return ""

# Scrape and store in ChromaDB
def scrape_links(link_data):
    full_data = []
    for i, link in enumerate(link_data):
        url = link['link']
        print(f"Scraping: {url}")

        if any(x in url.lower() for x in ['youtube', 'js', 'javascript']):
            text = scrape_dynamic(url)
        else:
            text = scrape_static(url)

        cleaned_text = text[:3000]
        full_data.append({
            "title": link['title'],
            "link": url,
            "text": cleaned_text
        })

        # Add to ChromaDB
        collection.add(
            documents=[cleaned_text],
            metadatas=[{"title": link['title'], "link": url}],
            ids=[f"doc_{i}"]
        )

    return full_data
