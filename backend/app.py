from flask import Flask, request, jsonify
from flask_cors import CORS
from together import Together
from config import Config
from utils.text_processor import process_website_content, scrape_website
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS with specific settings
CORS(app, resources={
    r"/api/*": {
        "origins": ["chrome-extension://*", "http://localhost:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize Together client
client = Together()
client.api_key = Config.TOGETHER_API_KEY

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        return ('', 204, headers)

    try:
        data = request.json
        if not data:
            logger.error("No data provided")
            return jsonify({"error": "No data provided"}), 400

        website_content = data.get('website_content', '')
        user_message = data.get('user_message', '')
        url = data.get('url', '')

        logger.info(f"Received request - URL: {url}")
        logger.info(f"User message: {user_message}")

        if not user_message:
            logger.error("No message provided")
            return jsonify({"error": "No message provided"}), 400

        # If URL is provided, scrape the website
        if url:
            logger.info(f"Scraping URL: {url}")
            website_content = scrape_website(url)
        else:
            website_content = process_website_content(website_content)

        logger.info(f"Processed content length: {len(website_content)}")
        logger.info(f"Content preview: {website_content[:200]}...")

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

        logger.info("Calling Together API")
        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=messages,
            max_tokens=10000,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
            stream=False
        )

        assistant_response = ""
        for token in response:
            if hasattr(token, 'choices'):
                content = token.choices[0].delta.content
                if content:
                    assistant_response += content

        logger.info(f"Assistant response: {assistant_response[:200]}...")
        return jsonify({"response": assistant_response})

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')