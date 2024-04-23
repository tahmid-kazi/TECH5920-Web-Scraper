import json
from pubmed_module import PubMedScraper
from nature_module import NatureScraper


# A mapping from configuration names to scraper classes
SCRAPER_CLASSES = {
    "PubMed": PubMedScraper,
    "Nature": NatureScraper
}

class ParentScraper:

    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = json.load(file)
        self.scrapers = []

    def initialize_scrapers(self):

        for scraper_key, keywords in self.config.items():
            if scraper_key.startswith("Scraper "):
                scraper_name = self.config[scraper_key]
                scraper_class = SCRAPER_CLASSES.get(scraper_name)
                if scraper_class: 
                    keyword_list_key = "keyword list " + scraper_key.split()[-1]  # Split and use the last part of the scraper key
                    config_inp = {'keywords':self.config[keyword_list_key]} # dict to hold parameter vals --> need to modify when adding more parameters
                    scraper_instance = scraper_class(config_inp)
                    self.scrapers.append(scraper_instance)
                else:
                    print(f"Scraper class for {scraper_name} not found.")

    def run_scrapers(self):
        for scraper in self.scrapers:
            scraper.run_scheduler()

# Main script execution
if __name__ == "__main__":
    parent_scraper = ParentScraper('config.json')
    parent_scraper.initialize_scrapers()
    parent_scraper.run_scrapers()