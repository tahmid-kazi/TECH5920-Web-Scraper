import requests
from bs4 import BeautifulSoup
import csv
import argparse

def scrape_pubmed(keyword, base_url, search_url):
    response = requests.get(search_url)
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
            link = base_url + title_tag['href'].strip('/')
            
            # Fetch the abstract page
            abstract_text = "No abstract available"
            abstract_response = requests.get(link)
            if abstract_response.status_code == 200:
                abstract_soup = BeautifulSoup(abstract_response.text, 'html.parser')
                abstract_tag = abstract_soup.find('div', class_='abstract-content')
                if abstract_tag:
                    abstract_text = abstract_tag.text.strip()
                
                # Extract authors, affiliations, keywords, and publication date
                authors_tags = abstract_soup.find_all('div', class_='authors-list')
                if authors_tags:
                    authors_list = [author.text.strip() for author in authors_tags]
                
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
                "authors": authors_list,
                "affiliations": affiliations_list,
                "keywords": keywords_list,
                "publication_date": publication_date
            })

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
        writer.writerow(["Keyword", "Title", "URL", "Abstract", "Authors", "Affiliations", "Keywords", "Publication Date"])
        for article in data:
            # Convert lists to strings
            authors = '; '.join(article['authors'])
            affiliations = '; '.join(article['affiliations'])
            keywords = '; '.join(article['keywords'])
            # Write as a row
            writer.writerow([article["keyword"], article["title"], article["link"], article["abstract"], authors, affiliations, keywords, article["publication_date"]])

# Main script execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PubMed Scraper')
    parser.add_argument('--year', type=int, default=2024, help='Specify start year for publication date range to scrape. Default = 2019')
    args = parser.parse_args()
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    keywords = read_keywords_from_file('keywords.txt')
    all_articles_data = []
    for keyword in keywords:
        print(f"Scraping articles for keyword: {keyword}")
        search_url = f"{base_url}?term={keyword}+{args.year}%5Bdp%5D&sort=date"
        articles_data = scrape_pubmed(keyword, base_url, search_url)
        all_articles_data.extend(articles_data)
    write_to_csv(all_articles_data)
