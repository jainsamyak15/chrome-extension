from bs4 import BeautifulSoup
import requests


def scrape_website(url):
    """
    Scrape website content using BeautifulSoup
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'header', 'footer', 'nav']):
            element.decompose()

        # Extract text content
        text = soup.get_text(separator=' ', strip=True)
        return process_website_content(text)
    except Exception as e:
        return f"Error scraping website: {str(e)}"


def process_website_content(content):
    """
    Process and clean website content for better context understanding
    """
    # Remove excess whitespace and newlines
    content = ' '.join(content.split())

    # Remove multiple spaces
    while '  ' in content:
        content = content.replace('  ', ' ')

    # Limit content length to prevent token overflow
    max_length = 10000
    if len(content) > max_length:
        content = content[:max_length] + "..."

    return content