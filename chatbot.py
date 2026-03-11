import numpy as np
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class ECommerceChatbot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer()
        
        # Load FAQ data
        with open('faq_data.json', 'r') as file:
            self.faq_data = json.load(file)
        
        # Prepare questions and answers
        self.questions = [item['question'] for item in self.faq_data]
        self.answers = [item['answer'] for item in self.faq_data]
        
        # Create TF-IDF matrix for questions
        self.preprocessed_questions = [self.preprocess_text(q) for q in self.questions]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.preprocessed_questions)
        
        # Simulated order database
        self.orders = {
            'ORD12345': {
                'status': 'Shipped', 
                'estimated_delivery': '2024-03-15', 
                'items': ['Laptop', 'Mouse'],
                'tracking_link': 'https://track.carrier.com/123456'
            },
            'ORD67890': {
                'status': 'Processing', 
                'estimated_delivery': '2024-03-18', 
                'items': ['Phone Case'],
                'tracking_link': None
            },
            'ORD11111': {
                'status': 'Delivered', 
                'estimated_delivery': '2024-03-10', 
                'items': ['Headphones'],
                'tracking_link': 'https://track.carrier.com/789012'
            },
            'ORD22222': {
                'status': 'Out for Delivery', 
                'estimated_delivery': '2024-03-12', 
                'items': ['Keyboard'],
                'tracking_link': 'https://track.carrier.com/345678'
            },
            'ORD33333': {
                'status': 'Cancelled', 
                'estimated_delivery': 'N/A', 
                'items': ['Monitor'],
                'tracking_link': None
            }
        }
        
        # Conversation context
        self.context = {
            'last_topic': None,
            'pending_order_id': None,
            'awaiting_order_id': False
        }
        
        # Simple greeting words
        self.greeting_words = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        self.farewell_words = ['bye', 'goodbye', 'thanks', 'thank you']

    def preprocess_text(self, text):
        """Preprocess text by cleaning, lemmatizing and removing stopwords"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        
        # Remove stopwords and lemmatize
        processed_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 1
        ]
        
        return ' '.join(processed_tokens)

    def get_best_match(self, user_query, threshold=0.2):
        """Find the best matching question using cosine similarity"""
        # Preprocess user query
        processed_query = self.preprocess_text(user_query)
        
        # Transform query using the same vectorizer
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get the best match
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]
        
        print(f"Query: '{user_query}'")  # Debug
        print(f"Best match: '{self.questions[best_match_idx]}' with similarity: {best_similarity}")  # Debug
        
        if best_similarity >= threshold:
            return self.answers[best_match_idx]
        return None

    def extract_order_id(self, text):
        """Extract order ID from text"""
        order_id_pattern = r'ORD\d{5}'
        matches = re.findall(order_id_pattern, text.upper())
        return matches[0] if matches else None

    def handle_order_query(self, query):
        """Handle order-related queries with context"""
        # Check for order ID in the query
        order_id = self.extract_order_id(query)
        
        if order_id:
            self.context['pending_order_id'] = order_id
            self.context['awaiting_order_id'] = False
            return self.get_order_details(order_id)
        
        # Check if we're awaiting an order ID from previous context
        if self.context['awaiting_order_id']:
            # Assume the user just provided the order ID
            potential_order_id = query.strip().upper()
            if re.match(r'ORD\d{5}', potential_order_id):
                self.context['pending_order_id'] = potential_order_id
                self.context['awaiting_order_id'] = False
                return self.get_order_details(potential_order_id)
        
        # Check if it's an order-related question without ID
        order_keywords = ['track', 'order', 'status', 'where', 'delivery', 'shipped', 'arrive', 'items']
        if any(keyword in query.lower() for keyword in order_keywords):
            self.context['awaiting_order_id'] = True
            self.context['last_topic'] = 'order'
            return "To help with your order, please provide your order ID (e.g., ORD12345)."
        
        return None

    def get_order_details(self, order_id):
        """Get detailed order information"""
        if order_id in self.orders:
            order = self.orders[order_id]
            items_list = ', '.join(order['items'])
            
            if order['status'] == 'Shipped':
                return f"Order #{order_id} is {order['status']}. Estimated delivery: {order['estimated_delivery']}. Items in this order: {items_list}. You will receive a tracking link via email once it's out for delivery."
            elif order['status'] == 'Out for Delivery':
                return f"Order #{order_id} is {order['status']} today! Estimated delivery: {order['estimated_delivery']}. Items: {items_list}"
            elif order['status'] == 'Delivered':
                return f"Order #{order_id} was {order['status'].lower()} on {order['estimated_delivery']}. Items delivered: {items_list}"
            elif order['status'] == 'Processing':
                return f"Order #{order_id} is currently {order['status']} and estimated to deliver by {order['estimated_delivery']}. Items: {items_list}"
            elif order['status'] == 'Cancelled':
                return f"Order #{order_id} has been {order['status'].lower()}. Items: {items_list}"
            else:
                return f"Order #{order_id} is {order['status']}. Estimated delivery: {order['estimated_delivery']}. Items: {items_list}"
        else:
            return f"Order #{order_id} not found. Valid order IDs: ORD12345, ORD67890, ORD11111, ORD22222, ORD33333"

    def handle_return_query(self, query):
        """Handle return-related queries"""
        return_keywords = ['return', 'refund', 'money back', 'damaged', 'defective']
        if any(keyword in query.lower() for keyword in return_keywords):
            if 'damaged' in query.lower() or 'defective' in query.lower():
                return "I'm sorry to hear that! If you received a damaged or defective item, please contact us within 48 hours of delivery. Provide your order ID and photos of the item. We'll arrange a replacement or refund immediately."
            elif 'return shipping' in query.lower() or 'pay for return' in query.lower():
                return "Return shipping is free for defective items or if we made an error. For other returns, a small shipping fee may apply. This information will be provided when you initiate the return."
            elif 'how long' in query.lower() and 'refund' in query.lower():
                return "Refunds are processed within 5-7 business days after we receive and inspect your returned item. The refund will be issued to your original payment method."
        return None

    def get_response(self, user_input):
        """Get chatbot response for user input with context awareness"""
        user_input_lower = user_input.lower().strip()
        
        # Check for simple greetings (only if it's a short message)
        if len(user_input_lower.split()) <= 3:
            for greeting in self.greeting_words:
                if greeting in user_input_lower or user_input_lower == greeting:
                    self.context['last_topic'] = 'greeting'
                    return "Hello! How can I help you today? You can ask me about orders, returns, shipping, payments, and more."
        
        # Check for farewells
        for farewell in self.farewell_words:
            if farewell in user_input_lower:
                self.context['last_topic'] = None
                self.context['awaiting_order_id'] = False
                return "You're welcome! Let me know if you need anything else."
        
        # Handle order tracking with context
        if any(word in user_input_lower for word in ['track', 'order', 'status', 'where', 'delivery', 'shipped', 'arrive', 'items']):
            order_response = self.handle_order_query(user_input)
            if order_response:
                return order_response
        
        # Handle return-related queries
        return_response = self.handle_return_query(user_input)
        if return_response:
            return return_response
        
        # Try to find a match in FAQ
        faq_response = self.get_best_match(user_input)
        if faq_response:
            return faq_response
        
        # Handle follow-up questions based on context
        if self.context['awaiting_order_id']:
            return "Please provide a valid order ID in the format ORD12345."
        
        # Default response
        return "I'm sorry, I don't have information about that. Please contact customer support at support@ecommerce.com or call 1-800-123-4567 for further assistance. You can also try rephrasing your question."

if __name__ == "__main__":
    # Test the chatbot
    chatbot = ECommerceChatbot()
    print("E-Commerce Chatbot initialized. Type 'quit' to exit.")
    print("-" * 50)
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            print("Chatbot: Goodbye!")
            break
        response = chatbot.get_response(user_input)
        print(f"Chatbot: {response}")