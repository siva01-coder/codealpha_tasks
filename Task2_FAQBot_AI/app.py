import os
from flask import Flask, render_template, request, jsonify
from chatbot import FAQChatbot

app = Flask(__name__)

# Initialize FAQ Chatbot once when Flask server starts up
print("[Server Setup] Initializing FAQBot AI NLP Engine...")
bot = FAQChatbot()
print("[Server Setup] FAQBot AI Ready!")

@app.route('/')
def index():
    """Renders the single-page FAQBot AI application UI."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """
    POST /api/chat
    Payload: { "message": "User query", "context": { "last_category": "...", "last_faq_id": 1 } }
    Returns: JSON FAQ response with confidence score, category, and NLP metrics.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request format. Expected JSON body.",
                "answer": "Invalid request format.",
                "confidence": 0,
                "category": None
            }), 400

        user_message = data.get('message', '')
        session_context = data.get('context', {})

        # Process via Chatbot NLP Engine
        response = bot.get_response(user_message, session_context)
        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f"Error processing chat request: {e}")
        return jsonify({
            "success": False,
            "error": "Something went wrong while processing your question.",
            "answer": "Something went wrong while processing your question. Please try again.",
            "confidence": 0,
            "category": None
        }), 500

@app.route('/api/faqs', methods=['GET'])
def get_faqs_api():
    """
    GET /api/faqs?category=Admissions
    Returns the list of FAQs optionally filtered by category.
    """
    category = request.args.get('category', 'All')
    faqs = bot.get_faqs_by_category(category)
    return jsonify({
        "success": True,
        "count": len(faqs),
        "category": category,
        "faqs": faqs
    })

@app.route('/api/categories', methods=['GET'])
def get_categories_api():
    """
    GET /api/categories
    Returns list of all available FAQ categories with entry counts.
    """
    categories = bot.get_categories()
    return jsonify({
        "success": True,
        "categories": categories
    })

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error."}), 500

if __name__ == '__main__':
    # Run dev server on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
