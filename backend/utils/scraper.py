import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape(self, url):
        """
        Scrape website content with proper error handling
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'header', 'footer', 'nav']):
                element.decompose()

            # Extract text content
            text = soup.get_text(separator=' ', strip=True)
            return text

        except requests.RequestException as e:
            logger.error(f"Error scraping website: {str(e)}")
            return f"Error accessing website: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error while scraping: {str(e)}")
            return f"Unexpected error: {str(e)}"