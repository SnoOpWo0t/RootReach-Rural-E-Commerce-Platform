"""
Gemini AI Chatbot Service for RootReach
This module handles integration with Google Generative AI (Gemini) for intelligent chatbot responses.
"""

import os
import logging
from typing import Optional
import google.genai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialize and store Gemini client
_gemini_client = None

def initialize_gemini():
    """Initialize Gemini API client with API key from environment or settings."""
    global _gemini_client
    
    if _gemini_client is not None:
        return True
    
    api_key = os.getenv('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        logger.warning("GEMINI_API_KEY not found in environment or settings")
        return False
    
    try:
        _gemini_client = genai.Client(api_key=api_key)
        logger.info("Gemini API client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {str(e)}")
        return False


def get_system_prompt() -> str:
    """
    Get the system prompt that defines the chatbot's personality and knowledge base.
    """
    return """You are an intelligent customer service AI assistant for RootReach, an e-commerce platform.

Your responsibilities:
1. Help customers with product inquiries and recommendations
2. Provide information about pricing, shipping, and delivery
3. Explain return and refund policies
4. Guide sellers through the application process
5. Answer questions about account management and security
6. Be friendly, professional, and solution-oriented
7. Provide accurate information about the platform

RootReach Information:
- RootReach is an e-commerce marketplace connecting buyers and sellers
- Platform features include product listings, shopping cart, order tracking, and messaging system
- Sellers can apply to join the platform and manage their products
- Payment methods include various online payment options
- Shipping is handled through partners
- Return policy allows returns within 30 days of purchase
- All transactions are secured with encryption

Guidelines:
- Keep responses concise and helpful (2-3 sentences max for quick queries, can be longer for detailed questions)
- Use emojis sparingly and only when appropriate (like 📦 for shipping, 💰 for pricing)
- If you don't know something specific about RootReach, be honest and suggest contacting support
- Always prioritize customer satisfaction
- Be empathetic when dealing with complaints or issues"""


def chat_with_gemini(user_message: str, conversation_history: Optional[list] = None) -> str:
    """
    Send a message to Gemini and get an AI response.
    
    Args:
        user_message: The user's input message
        conversation_history: Optional list of previous messages for context
        
    Returns:
        The AI-generated response from Gemini
    """
    try:
        # Initialize Gemini client
        if not initialize_gemini():
            return "I'm currently unavailable. Please check that your Gemini API key is set in the .env file."
        
        # Prepare system instruction
        system_prompt = get_system_prompt()
        
        # Try with the most compatible model first
        # These models work with the google-genai package
        models_to_try = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
        
        last_error = None
        for model_name in models_to_try:
            try:
                # Create the request with system instruction
                response = _gemini_client.models.generate_content(
                    model=model_name,
                    contents=[
                        {
                            "role": "user",
                            "parts": [{"text": f"{system_prompt}\n\nUser: {user_message}"}]
                        }
                    ]
                )
                
                if response.text:
                    logger.info(f"Gemini response generated successfully using {model_name}")
                    return response.text
                    
            except Exception as model_error:
                last_error = str(model_error)
                logger.warning(f"Model {model_name} failed: {last_error[:100]}")
                continue
        
        # Handle specific error cases
        if last_error:
            if "RESOURCE_EXHAUSTED" in last_error or "quota" in last_error.lower():
                logger.error("API quota exceeded on free tier")
                return "My free API quota has been exceeded. Please get a new API key from https://aistudio.google.com/app/apikey or enable billing at https://console.cloud.google.com/."
            elif "NOT_FOUND" in last_error and "models/" in last_error:
                logger.error("Model not found or not available on this API tier")
                return "The AI model is not available on the free tier. Please enable billing or get a new API key with billing enabled."
            elif "UNAUTHENTICATED" in last_error or "invalid" in last_error.lower():
                logger.error("Invalid or missing API key")
                return "The API key is invalid or missing. Please check your .env file and ensure GEMINI_API_KEY is set correctly."
        
        logger.error(f"All models failed. Last error: {last_error}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again later or check the server logs for details."
            
    except Exception as e:
        logger.error(f"Unexpected error in chat_with_gemini: {str(e)}")
        return "I apologize, but an unexpected error occurred. Please try again later."


def validate_message(message: str) -> bool:
    """
    Validate user message for safety and content.
    
    Args:
        message: The message to validate
        
    Returns:
        True if message is valid, False otherwise
    """
    if not message or not isinstance(message, str):
        return False
    
    # Check message length (reasonable limits)
    if len(message.strip()) == 0 or len(message) > 2000:
        return False
    
    return True
