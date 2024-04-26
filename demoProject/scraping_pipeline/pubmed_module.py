import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import argparse
from typing import List, Dict
from pathlib import Path

class PubMedScraper:

    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://pubmed.ncbi.nlm.nih.gov/"

    def run_scheduler(self):
        # For now, this can just call the scrape process directly
        # Later on, we can implement more complex scheduling
        self.scrape_pipeline()

    def scrape_pipeline(self):
        year = 2024 # Hardcoded for now
        articles_data = [] # List to store all articles
        for keyword in self.config['keywords']:
            print(f"Scraping articles for keyword: {keyword} from PubMed")
            search_url = f"{self.base_url}?term={keyword}+{year}%5Bdp%5D&sort=date"
            articles_data = self.scrape_pubmed(keyword, search_url)
            articles_data.extend(articles_data)
        self.write_to_csv(articles_data, mode='w')  


    def scrape_pubmed(self, keyword: str, search_url: str):
        response = requests.get(search_url)
        time.sleep(0.5)  # Respectful delay between requests
        articles_data = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('div', class_='docsum-wrap')
            for article in articles:
                # Initialize the new fields as empty lists or strings
                authors_list = []
                affiliations_list = []
                keywords_list = []
                publication_date = ""

                title_tag = article.find('a', class_='docsum-title')
                title = title_tag.text.strip()
                link = self.base_url + title_tag['href'].strip('/')
                
                # Fetch the abstract page
                abstract_text = "No abstract available"
                abstract_response = requests.get(link)
                if abstract_response.status_code == 200:
                    abstract_soup = BeautifulSoup(abstract_response.text, 'html.parser')
                    abstract_tag = abstract_soup.find('div', class_='abstract-content')
                    if abstract_tag:
                        abstract_text = abstract_tag.text.strip()
                    
                    # Extract authors, affiliations, keywords, and publication date
                    # authors_tags = abstract_soup.find_all('div', class_='authors-list')
                    # if authors_tags:
                    #     authors_list = [author.text.strip() for author in authors_tags]
                    
                    affiliations_tags = abstract_soup.find_all('div', class_='affiliations')
                    if affiliations_tags:
                        affiliations_list = [affiliation.text.strip() for affiliation in affiliations_tags]
                    
                    keywords_tags = abstract_soup.find('div', class_='keywords')
                    if keywords_tags:
                        keywords_list = [keyword.text.strip() for keyword in keywords_tags.find_all('a')]
                    
                    date_tag = abstract_soup.find('span', class_='cit')
                    if date_tag:
                        publication_date = date_tag.text.strip()

                articles_data.append({
                    "keyword": keyword,
                    "title": title,
                    "link": link,
                    "abstract": abstract_text,
                    # "authors": authors_list,
                    "affiliations": affiliations_list,
                    "keywords": keywords_list,
                    "publication_date": publication_date
                })

        else:
            print(f"Failed to retrieve data for keyword '{keyword}'. HTTP Status Code: {response.status_code}")
        return articles_data

    def write_to_csv(self, data: List, filename='pubmed_articles.csv', mode='w'):
        script_dir = Path(__file__).parent.resolve()
    # Step out of the script directory and into the 'databases' directory
        database_dir = script_dir.parent / 'databases'
        filepath = database_dir / filename
        with open(filepath, mode=mode, newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["Keyword", "Title", "URL", "Abstract", "Affiliations", "Keywords", "Publication Date"])
            for article in data:
                # authors = '; '.join(article['authors'])
                affiliations = '; '.join(article['affiliations'])
                keywords = '; '.join(article['keywords'])
                # Write as a row
                writer.writerow([article["keyword"], article["title"], article["link"], article["abstract"], affiliations, keywords, article["publication_date"]])

def read_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# # Main script execution
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='PubMed Scraper')
#     parser.add_argument('--config', type=str, default='config.json', help='Path to configuration JSON file.')
#     args = parser.parse_args()
#     config = read_config(args.config)
    
#     scraper = PubMedScraper(config)
#     scraper.run_scheduler()