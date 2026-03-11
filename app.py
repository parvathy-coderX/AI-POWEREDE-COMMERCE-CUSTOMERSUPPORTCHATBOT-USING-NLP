from flask import Flask, render_template, request, jsonify
from chatbot import ECommerceChatbot
import json

app = Flask(__name__)

# Initialize the chatbot
chatbot = ECommerceChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get chatbot response
        response = chatbot.get_response(user_message)
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/track-order', methods=['POST'])
def track_order():
    try:
        order_id = request.json.get('order_id', '')
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
        
        # Track order status
        order_status = chatbot.track_order(order_id)
        return jsonify(order_status)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)