from together import Together
import logging
from .scraper import WebScraper
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self, api_key, model_name):
        self.client = Together()
        self.client.api_key = api_key
        self.model_name = model_name
        self.scraper = WebScraper()
        self.text_processor = TextProcessor()

    def prepare_content(self, website_content, url):
        """
        Prepare website content for chat
        """
        if url:
            logger.info(f"Scraping URL: {url}")
            content = self.scraper.scrape(url)
        else:
            content = website_content

        return self.text_processor.process(content)

    def generate_response(self, website_content, user_message):
        """
        Generate chat response using Together API
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions about website content."
                },
                {
                    "role": "user",
                    "content": f"""Context from website: {website_content}\n\nUser question: {user_message}\n\nPlease respond based on the website content:"""
                }
            ]

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=10000,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>", "<|eom_id|>"]
            )

            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise Exception("No response content from API")

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise