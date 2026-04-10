"""
Default AI Message Suggestion Templates
Used by the AI to provide smart response suggestions in buyer-seller messaging
"""

SUGGESTION_TEMPLATES = [
    # Greetings
    {
        "suggestion_type": "greeting",
        "message_template": "Hi, I'm interested in your product",
        "response_suggestions": [
            "Thanks for your interest! How can I help you today?",
            "Happy to assist! Do you have any questions about this item?",
            "Welcome! I'm here to help. What would you like to know?"
        ]
    },
    
    # Product Inquiries
    {
        "suggestion_type": "product_inquiry",
        "message_template": "Can you tell me more about this product?",
        "response_suggestions": [
            "Absolutely! This is a premium quality product with excellent reviews. All details are in the product description. Any specific questions?",
            "Sure! This item is highly rated and in stock. Check the specifications above. Feel free to ask anything specific!",
            "Of course! It's a top-quality item. Let me know what details you'd like to know more about."
        ]
    },
    {
        "suggestion_type": "product_inquiry",
        "message_template": "What's the condition of this product?",
        "response_suggestions": [
            "This product is brand new and never used. It comes with complete packaging and warranty.",
            "It's in excellent condition - brand new with all original packaging intact.",
            "Pristine condition! Fresh from stock and ready to ship immediately."
        ]
    },
    
    # Price Negotiation
    {
        "suggestion_type": "price_negotiation",
        "message_template": "Can you offer a discount?",
        "response_suggestions": [
            "We already offer great value! But for bulk orders, we can discuss special pricing.",
            "Our current price is very competitive. We can offer a discount for multiple units - how many are you interested in?",
            "The price is already our best offer, but we offer free shipping on orders over a certain amount!"
        ]
    },
    {
        "suggestion_type": "price_negotiation",
        "message_template": "Is this your lowest price?",
        "response_suggestions": [
            "Yes, this is our best competitive price. Quality guaranteed at this price point!",
            "This is our standard price and it's fair for the quality. Very reasonable compared to the market.",
            "Absolutely! This is our final price and we stand behind its value."
        ]
    },
    
    # Shipping Questions
    {
        "suggestion_type": "shipping_question",
        "message_template": "How long does delivery take?",
        "response_suggestions": [
            "Delivery takes 3-7 business days depending on your location. I can check the exact timeline for your area if needed.",
            "Standard delivery is 5-7 days. We also offer express shipping if you need it faster!",
            "Usually 3-5 days to most areas. Your exact delivery date will be shown after checkout."
        ]
    },
    {
        "suggestion_type": "shipping_question",
        "message_template": "Do you ship to my area?",
        "response_suggestions": [
            "Where are you located? Let me check if we deliver to that area!",
            "We deliver nationwide! Which region are you in? I can confirm delivery availability.",
            "Yes, we ship across the country. Enter your location at checkout to confirm delivery options."
        ]
    },
    
    # Common Objections
    {
        "suggestion_type": "complaint",
        "message_template": "Why is the item so expensive?",
        "response_suggestions": [
            "This is premium quality with excellent reviews backing it up. The price reflects the value and durability!",
            "Great question! The higher price ensures quality and durability. Many customers say it's worth the investment.",
            "We offer best value for this quality. Compare with similar products and you'll see why it's priced this way."
        ]
    },
    
    # Order Status
    {
        "suggestion_type": "order_status",
        "message_template": "When will my order arrive?",
        "response_suggestions": [
            "Your order is on track for [DATE]. You should receive it within the timeline shown in your order details.",
            "It's being processed and should ship within 1-2 days. You'll get a tracking number then!",
            "Shipping out today/tomorrow! You'll receive tracking info in your email shortly."
        ]
    },
    
    # Generic/General
    {
        "suggestion_type": "general",
        "message_template": "I need help",
        "response_suggestions": [
            "Of course! I'm here to help. What do you need assistance with?",
            "Happy to help! What's your question or concern?",
            "No problem at all! How can I assist you?"
        ]
    },
]

# Message patterns for quick AI matching
COMMON_PATTERNS = {
    'price': ['price', 'cost', 'how much', 'expensive', 'cheap', 'affordable', 'discount'],
    'availability': ['available', 'stock', 'in stock', 'when available', 'out of stock'],
    'shipping': ['ship', 'deliver', 'fast', 'how long', 'arrival', 'days', 'express'],
    'quality': ['quality', 'spec', 'details', 'material', 'size', 'condition'],
    'greeting': ['hello', 'hi', 'interested', 'interested in', 'looking for'],
    'payment': ['pay', 'payment', 'how to pay', 'accept'],
    'return': ['return', 'refund', 'exchange', 'money back'],
}
