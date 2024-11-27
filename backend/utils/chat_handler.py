from together import Together
import logging
from .scraper import WebScraper
from .text_processor import TextProcessor
from .analysis import ContentAnalyzer

logger = logging.getLogger(__name__)


class ChatHandler:
    def __init__(self, api_key, model_name):
        self.client = Together()
        self.client.api_key = api_key
        self.model_name = model_name
        self.scraper = WebScraper()
        self.text_processor = TextProcessor()
        self.analyzer = ContentAnalyzer()

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

    def analyze_content(self, content):
        """
        Perform comprehensive content analysis
        """
        try:
            summary = self.analyzer.summarize(content)
            sentiment = self.analyzer.analyze_sentiment(content)
            keywords = self.analyzer.extract_keywords(content)

            return {
                "summary": summary,
                "sentiment": sentiment,
                "keywords": keywords
            }
        except Exception as e:
            logger.error(f"Error in analyze_content: {str(e)}")
            return None

    def generate_response(self, website_content, user_message):
        """
        Generate chat response using Together API
        """
        try:
            # Perform content analysis
            analysis = self.analyze_content(website_content)

            # Prepare enhanced context
            context = f"""
Website Content Summary: {analysis['summary'] if analysis else 'Not available'}

Key Topics: {', '.join(analysis['keywords']) if analysis and analysis['keywords'] else 'Not available'}

Content Sentiment: {analysis['sentiment']['sentiment'] if analysis else 'Not available'}

Full Content: {website_content}
            """

            messages = [
                {
                    "role": "system",
                    "content": """You are an advanced AI assistant that provides detailed analysis of website content.
You can analyze the content's sentiment, extract key topics, and provide summaries.
Always reference the provided analysis in your responses when relevant."""
                },
                {
                    "role": "user",
                    "content": f"""Context: {context}\n\nUser question: {user_message}\n\nPlease provide a detailed response based on the website content and analysis:"""
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