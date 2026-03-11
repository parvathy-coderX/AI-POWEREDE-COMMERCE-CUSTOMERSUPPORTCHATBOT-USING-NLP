// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const chatForm = document.getElementById('chatForm');
const sendButton = document.getElementById('sendButton');

// State
let isTyping = false;

// Event Listeners
chatForm.addEventListener('submit', handleSendMessage);
userInput.addEventListener('keypress', handleKeyPress);

// Handle Send Message
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message || isTyping) return;
    
    // Clear input
    userInput.value = '';
    
    // Display user message
    addMessage(message, 'user');
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send to backend
        const response = await sendToBackend(message);
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Display bot response
        addMessage(response, 'bot');
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

// Handle Key Press
function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
}

// Send Message to Backend
async function sendToBackend(message) {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        return data.response || data.message || 'No response from server';
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Track Order (used by chatbot logic)
async function trackOrder(orderId) {
    try {
        const response = await fetch('/track-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ order_id: orderId })
        });
        
        const data = await response.json();
        return data.message || 'Order status retrieved';
    } catch (error) {
        console.error('Error tracking order:', error);
        return 'Error tracking order. Please try again.';
    }
}

// Add Message to Chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-icon">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-text">${formatMessage(text)}</div>
        </div>
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Format Message (handle URLs, line breaks, etc.)
function formatMessage(text) {
    // Convert URLs to links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    text = text.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');
    
    // Convert line breaks to <br>
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Show Typing Indicator
function showTypingIndicator() {
    isTyping = true;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="message-icon">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

// Remove Typing Indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isTyping = false;
}

// Scroll to Bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Focus on input
    userInput.focus();
    
    // Add smooth scrolling
    chatMessages.style.scrollBehavior = 'smooth';
});

// Error Handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    addMessage('An error occurred. Please refresh the page.', 'bot');
});