
import requests
from bs4 import BeautifulSoup

def scrape_pubmed(query):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_url = f"{base_url}?term={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.find_all('a', class_='docsum-title', href=True)
    for article in articles:
        print(article.text.strip())

# Use the function
scrape_pubmed("cancer")