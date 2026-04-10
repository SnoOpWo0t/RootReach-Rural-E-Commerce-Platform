"""
Smart AI Manager for RootReach
Automatically manages multiple AI providers with intelligent fallback:
1. Primary: Gemini (free tier)
2. Secondary: HuggingFace (free inference)
3. Fallback: Local pattern matching

This ensures:
- Always free (no paid services)
- Never stuck without responses
- Automatic fallback when one service exhausted
- Tracks which service is being used
"""

import logging
import os
from typing import Dict, Tuple, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Track AI service usage for analytics
AI_SERVICE_LOG = {
    'gemini': {'count': 0, 'errors': 0},
    'huggingface': {'count': 0, 'errors': 0},
    'fallback': {'count': 0, 'errors': 0},
}


class SmartAIManager:
    """
    Intelligently manages multiple AI providers with automatic fallback.
    Tries free services in order of preference.
    """
    
    def __init__(self):
        self.service_priority = [
            'gemini',        # Try Gemini first (free tier)
            'huggingface',   # Then HuggingFace (free inference)
            'fallback',      # Finally local pattern matching (always works)
        ]
        self.current_service = 'gemini'
        self.gemini_quota_exceeded = False
        self.huggingface_available = True
    
    def get_response(self, message: str, conversation_history: Optional[list] = None) -> Tuple[str, str]:
        """
        Get AI response with automatic fallback.
        
        Args:
            message: User message
            conversation_history: Optional conversation history
            
        Returns:
            Tuple of (response, service_used)
        """
        for service in self.service_priority:
            try:
                response = self._try_service(service, message, conversation_history)
                if response:
                    self.current_service = service
                    AI_SERVICE_LOG[service]['count'] += 1
                    logger.info(f"✓ {service.upper()} responded successfully")
                    return response, service
            except Exception as e:
                error_msg = str(e).lower()
                AI_SERVICE_LOG[service]['errors'] += 1
                
                # Check for specific errors
                if 'resource_exhausted' in error_msg or 'quota' in error_msg:
                    self.gemini_quota_exceeded = True
                    logger.warning(f"⚠️  {service.upper()} quota exhausted: {str(e)[:100]}")
                elif 'connection' in error_msg or 'timeout' in error_msg:
                    logger.warning(f"⚠️  {service.upper()} connection issue: {str(e)[:100]}")
                else:
                    logger.error(f"❌ {service.upper()} error: {str(e)[:100]}")
                
                continue
        
        # Should not reach here, but just in case
        logger.critical("❌ All AI services failed!")
        return self._get_fallback_response(message), 'fallback'
    
    def _try_service(self, service: str, message: str, history: Optional[list] = None) -> Optional[str]:
        """Try specific AI service."""
        if service == 'gemini':
            if self.gemini_quota_exceeded:
                raise Exception("Gemini quota already exhausted, skipping")
            
            from .gemini_chatbot import chat_with_gemini, initialize_gemini
            if not initialize_gemini():
                raise Exception("Gemini not initialized")
            
            return chat_with_gemini(message, history)
        
        elif service == 'huggingface':
            from .huggingface_chatbot import chat_with_huggingface, validate_message
            if not validate_message(message):
                raise Exception("Invalid message format")
            
            return chat_with_huggingface(message)
        
        elif service == 'fallback':
            return self._get_fallback_response(message)
        
        return None
    
    def _get_fallback_response(self, message: str) -> str:
        """Generate response using local pattern matching."""
        from .huggingface_chatbot import SMART_PATTERNS
        
        msg_lower = message.lower().strip()
        best_match = None
        best_score = 0
        
        for keywords_str, response in SMART_PATTERNS.items():
            keywords = [k.strip() for k in keywords_str.split('|')]
            matches = sum(1 for keyword in keywords if keyword in msg_lower)
            
            if matches > best_score:
                best_score = matches
                best_match = response
        
        if best_match:
            return best_match
        
        return "📞 I'm having trouble understanding that. Could you rephrase your question? I'm here to help with products, shipping, returns, or account info!"
    
    def get_stats(self) -> Dict:
        """Get usage statistics for monitoring."""
        total_responses = sum(log['count'] for log in AI_SERVICE_LOG.values())
        
        return {
            'total_responses': total_responses,
            'gemini': AI_SERVICE_LOG['gemini'],
            'huggingface': AI_SERVICE_LOG['huggingface'],
            'fallback': AI_SERVICE_LOG['fallback'],
            'current_service': self.current_service,
            'gemini_quota_exceeded': self.gemini_quota_exceeded,
        }
    
    def reset_stats(self) -> None:
        """Reset usage statistics."""
        for service in AI_SERVICE_LOG:
            AI_SERVICE_LOG[service] = {'count': 0, 'errors': 0}
        logger.info("📊 AI service statistics reset")
    
    def force_service(self, service: str) -> bool:
        """Force use specific service (for testing/debugging)."""
        if service not in self.service_priority:
            return False
        
        self.service_priority.remove(service)
        self.service_priority.insert(0, service)
        logger.info(f"🔧 Forcing AI service priority: {self.service_priority}")
        return True


# Global instance
_ai_manager = None


def get_ai_manager() -> SmartAIManager:
    """Get or create the global AI manager instance."""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = SmartAIManager()
    return _ai_manager


def get_ai_response(message: str, conversation_history: Optional[list] = None) -> Tuple[str, str]:
    """
    Get AI response with automatic fallback between services.
    
    Args:
        message: User message
        conversation_history: Optional conversation history
        
    Returns:
        Tuple of (response, service_used)
    """
    manager = get_ai_manager()
    return manager.get_response(message, conversation_history)


def get_ai_stats() -> Dict:
    """Get AI service usage statistics."""
    manager = get_ai_manager()
    return manager.get_stats()


def reset_ai_stats() -> None:
    """Reset AI service statistics."""
    manager = get_ai_manager()
    manager.reset_stats()
