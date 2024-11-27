import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    def __init__(self, max_length=10000):
        self.max_length = max_length

    def process(self, content):
        """
        Process and clean text content
        """
        try:
            # Remove excess whitespace and newlines
            content = ' '.join(content.split())

            # Remove multiple spaces
            while '  ' in content:
                content = content.replace('  ', ' ')

            # Limit content length
            if len(content) > self.max_length:
                content = content[:self.max_length] + "..."

            return content

        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return f"Error processing text: {str(e)}"