def process_website_content(content):
    """
    Process and clean website content for better context understanding.
    """
    # Remove excess whitespace
    content = ' '.join(content.split())

    # Limit content length to prevent token overflow
    max_length = 10000
    if len(content) > max_length:
        content = content[:max_length] + "..."

    return content