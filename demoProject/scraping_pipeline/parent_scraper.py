import json
import argparse
from pubmed_module import PubMedScraper
from nature_module import NatureScraper

# A mapping from configuration names to scraper classes
SCRAPER_CLASSES = {
    "PubMed": PubMedScraper,
    "Nature": NatureScraper
}

class ParentScraper:
    def __init__(self, config):
        self.config = config
        self.scrapers = []

    def load_config_from_json(self, json_path):
        with open(json_path, 'r') as file:
            self.config = json.load(file)

    def initialize_scrapers(self):
        for scraper_key, keywords in self.config.items():
            if scraper_key.startswith("Scraper "):
                scraper_name = self.config[scraper_key]
                scraper_class = SCRAPER_CLASSES.get(scraper_name)
                if scraper_class: 
                    keyword_list_key = "keyword list " + scraper_key.split()[-1]
                    config_inp = {'keywords': self.config[keyword_list_key]}
                    scraper_instance = scraper_class(config_inp)
                    self.scrapers.append(scraper_instance)
                else:
                    print(f"Scraper class for {scraper_name} not found.")

    def run_scrapers(self):
        for scraper in self.scrapers:
            scraper.run_scheduler()

def parse_config(text_file):
    config = {}
    with open(text_file, 'r') as file:
        lines = file.readlines()

    current_scraper = None
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("Scraper"):
            parts = stripped_line.split(':')
            current_scraper = parts[0].strip()
            scraper_name = parts[1].strip()
            config[current_scraper] = scraper_name
            config[f"keyword list {current_scraper.split()[-1]}"] = []
        elif stripped_line.startswith('-'):
            keyword = stripped_line[1:].strip()
            config[f"keyword list {current_scraper.split()[-1]}"].append(keyword)

    return config

def save_config_to_json(config, json_path):
    with open(json_path, 'w') as file:
        json.dump(config, file, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Run scrapers based on a human-readable text config")
    parser.add_argument('text_file', help="Path to the text file containing scraper configurations")
    args = parser.parse_args()

    # Parse the human-readable text file to a config dictionary
    config = parse_config(args.text_file)

    # Optionally save to a JSON file (for verification or reuse)
    json_path = 'config.json'
    save_config_to_json(config, json_path)

    # Initialize and run scrapers
    parent_scraper = ParentScraper(config)
    parent_scraper.initialize_scrapers()
    parent_scraper.run_scrapers()

if __name__ == "__main__":
    main()