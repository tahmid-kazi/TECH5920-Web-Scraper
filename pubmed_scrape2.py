import requests
from bs4 import BeautifulSoup
import csv

def scrape_pubmed(keyword):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_url = f"{base_url}?term={keyword}"
    response = requests.get(search_url)
    articles_data = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('div', class_='docsum-wrap')
        for article in articles:
            title_tag = article.find('a', class_='docsum-title')
            title = title_tag.text.strip()
            link = base_url + title_tag['href'].strip('/')
            # Fetch the abstract page
            abstract_text = "No abstract available"
            abstract_response = requests.get(link)
            if abstract_response.status_code == 200:
                abstract_soup = BeautifulSoup(abstract_response.text, 'html.parser')
                abstract_tag = abstract_soup.find('div', class_='abstract-content')
                if abstract_tag:
                    abstract_text = abstract_tag.text.strip()
            articles_data.append([keyword, title, link, abstract_text])
    else:
        print(f"Failed to retrieve data for keyword '{keyword}'. HTTP Status Code: {response.status_code}")
    return articles_data

def read_keywords_from_file(filename):
    with open(filename, 'r') as file:
        keywords = [line.strip() for line in file.readlines()]
    return keywords

def write_to_csv(data, filename='pubmed_articles.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Title", "URL", "Abstract"])
        writer.writerows(data)

# Main script execution
if __name__ == "__main__":
    keywords = read_keywords_from_file('keywords.txt')
    all_articles_data = []
    for keyword in keywords:
        print(f"Scraping articles for keyword: {keyword}")
        articles_data = scrape_pubmed(keyword)
        all_articles_data.extend(articles_data)
    write_to_csv(all_articles_data)
