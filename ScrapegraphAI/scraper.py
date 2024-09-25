import logging
from scrapegraphai.graphs import SmartScraperGraph
from config import create_scraper_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_company_info(url: str, prompt: str) -> dict:
    try:
        smart_scraper_graph = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=create_scraper_config()
        )
        return smart_scraper_graph.run()
    except Exception as e:
        logging.error(f"Error scraping {url}: {str(e)}")
        return {"error": str(e)}