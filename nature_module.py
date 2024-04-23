import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import time
import csv

class NatureScraper:
    def __init__(self, config):
        self.base_url = 'https://www.nature.com'
        self.config = config

    def run_scheduler(self):
        # This is where scheduling logic would be placed. 
        # For the moment, it will directly call the scrape function.
        all_articles = []
        for keyword in self.config['keywords']:
            articles = self.extract_nature_articles(
                '2024-01-01', 
                '2024-12-31', 
                keyword
            )
            all_articles.extend(articles)
            time.sleep(1)  # Respectful delay between requests
        self.save_to_csv(all_articles, 'nature_articles.csv')
        return all_articles

    def extract_nature_articles(self, start_date, end_date, title_keyword: str) -> List[Dict]:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        search_url = f'{self.base_url}/search?q={title_keyword}&order=date_asc&date_range={start_dt.year}-{end_dt.year}&journal=nature&article_type=research'
        soup = self.retrieve_url(search_url)
        if not soup:
            return []

        all_atags = soup.find_all('a', {'data-track-action': 'view article'})
        if len(all_atags) == 0:
            print('No articles found')
            return []

        articles = []
        for atag in all_atags:
            article_url = self.base_url + atag['href']
            article_soup = self.retrieve_url(article_url)
            if article_soup:
                article_data = self.parse_page(article_soup)
                if article_data['Published Date']:
                    pub_date = datetime.strptime(article_data['Published Date'], '%Y-%m-%d')
                    if start_dt <= pub_date <= end_dt:
                        articles.append(article_data)

        # Sort articles by date and title
        articles_sorted = sorted(articles, key=lambda a: (a['Published Date'], a['Title']))

        return articles_sorted

    def retrieve_url(self, url: str) -> BeautifulSoup:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving URL {url}: {e}")
            return None

    def parse_page(self, soup: BeautifulSoup) -> Dict:
        time_element = soup.find('ul', {'data-test': 'article-identifier'}).find('time')
        if time_element:
            dt = datetime.strptime(time_element['datetime'], '%Y-%m-%d')
            date_str = dt.strftime('%Y-%m-%d')
        else:
            date_str = 'N/A'

        title_tag = soup.find('h1', {'data-test': 'article-title'})
        title = title_tag.get_text().strip() if title_tag else 'N/A'

        author_tags = soup.find_all('a', {'data-test': 'author-name'})
        authors = [tag.get_text().strip() for tag in author_tags]

         # Locate the abstract using the section ID
        abstract_section = soup.find('section', {'aria-labelledby': 'Abs1'})
        abstract = ''
        if abstract_section:
            abstract_content = abstract_section.find('div', class_='c-article-section__content')
            if abstract_content:
                abstract = abstract_content.get_text().strip()

        article_div = soup.find('div', {'class', 'c-article-body'})
        for related_content in article_div.find_all(attrs={'data-label': 'Related'}):
            related_content.decompose()  # Remove related content sections

        # content_texts = [tag.get_text().strip() for tag in article_div.find_all('p') if tag.get_text().strip()]

        return {
            'Title': title,
            'Author': ', '.join(authors),
            'Published Date': date_str,
            'Url': soup.base_url,
            'Abstract': abstract
        }

    def save_to_csv(self, articles, filename):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Author', 'Published Date', 'Url', 'Abstract']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for article in articles:
                writer.writerow(article)
        
        print(f"Articles saved to {filename}")

# # Example usage as a module
# if __name__ == "__main__":
#     # Configuration would typically be read from a file or passed by the parent scraper
#     config = {
#         'start_date': '2022-01-01',
#         'end_date': '2022-12-31',
#         'title_keyword': 'climate change'
#     }
#     nature_scraper = NatureScraper(config)
#     articles = nature_scraper.run_scheduler()
#     nature_scraper.save_to_csv(articles, 'nature_articles.csv')