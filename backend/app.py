from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from utils.chat_handler import ChatHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["chrome-extension://*", "http://localhost:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize chat handler
chat_handler = ChatHandler(Config.TOGETHER_API_KEY, Config.MODEL_NAME)

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

        if not user_message:
            logger.error("No message provided")
            return jsonify({"error": "No message provided"}), 400

        # Prepare website content
        processed_content = chat_handler.prepare_content(website_content, url)
        logger.info(f"Processed content length: {len(processed_content)}")

        # Generate response
        assistant_response = chat_handler.generate_response(processed_content, user_message)
        logger.info(f"Assistant response: {assistant_response[:200]}...")

        return jsonify({"response": assistant_response})

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')