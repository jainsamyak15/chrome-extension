from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from together import Together
from config import Config
from utils.text_processor import process_website_content
import json

app = Flask(__name__)

# Configure CORS to allow all origins
CORS(app, resources={r"/*": {"origins": "*"}})





# Initialize Together client
client = Together()
client.api_key = Config.TOGETHER_API_KEY


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

    try:
        print("Request Headers:", request.headers)
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        website_content = data.get('website_content', '')
        user_message = data.get('user_message', '')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Process the message and get response
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

        # Call the Together API
        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
            stream=False
        )

        # Log the response for debugging
        print("Together API Response:", response)

        # Extract the response text
        assistant_response = ""
        for token in response:
            if hasattr(token, 'choices'):
                content = token.choices[0].delta.content
                if content:
                    assistant_response += content

        return jsonify({"response": assistant_response})

    except Exception as e:
        print(f"Error processing request: {str(e)}")  # Server-side logging
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)