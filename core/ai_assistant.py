import json
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from django.conf import settings
from django.db.models import Avg, Q

from .models import Product, AIKnowledgeBase, AIMessageSuggestion

try:
    from openai import OpenAI
except ImportError:  # openai is optional at runtime
    OpenAI = None


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "best", "buy", "can", "for", "from", "get",
    "give", "help", "i", "in", "is", "it", "me", "my", "need", "of", "on", "or", "show",
    "something", "that", "the", "to", "want", "with",
}


@dataclass
class AssistantResult:
    reply: str
    recommendations: List[Product]
    used_llm: bool


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
    return [token for token in tokens if token not in _STOPWORDS and len(token) > 1]


def _get_knowledge_base_context() -> str:
    """Fetch relevant knowledge base entries to enrich AI context"""
    try:
        kb_entries = AIKnowledgeBase.objects.filter(is_active=True).order_by('-priority')[:20]
        if not kb_entries:
            return ""
        
        context_items = []
        for entry in kb_entries:
            context_items.append(f"Q: {entry.question}\nA: {entry.answer}")
        
        return "\n\n".join(context_items)
    except:
        return ""


def _get_platform_context() -> str:
    """Get comprehensive platform information for AI context"""
    try:
        product_count = Product.objects.filter(stock__gt=0).count()
        category_count = Product.objects.values('category').distinct().count()
        top_products = Product.objects.filter(stock__gt=0).order_by('-rating')[:3]
        
        context = f"""
RootReach Platform Status:
- Active Products: {product_count}
- Categories: {category_count}
- Featured: {', '.join([p.name for p in top_products]) if top_products else 'Various items'}

Platform Policies:
- Return Policy: 30 days full return guarantee
- Payment: Secure online payment gateways
- Shipping: Partner-based nationwide delivery
- Support: 24/7 customer service available
- Seller Rating: Quality verified with buyer reviews
"""
        return context
    except:
        return ""


def _score_product(product, tokens: Iterable[str]) -> float:
    name = product.get('name', '') if isinstance(product, dict) else (product.name or '')
    description = product.get('description', '') if isinstance(product, dict) else (product.description or '')
    region = product.get('region', '') if isinstance(product, dict) else (product.region or '')
    category_name = product.get('category__name', '') if isinstance(product, dict) else (product.category.name if hasattr(product, 'category') and product.category else '')
    
    haystack = " ".join([name, description, region, category_name]).lower()
    score = 0.0
    for token in tokens:
        if token in haystack:
            score += 2.0
        if name and token in name.lower():
            score += 2.0
    return score


def _candidate_products(limit: int = 50) -> List[Product]:
    return list(
        Product.objects.select_related("category", "seller")
        .filter(stock__gt=0)
        .values("id", "name", "description", "region", "category__name", "created_at")
        .order_by("-created_at")[:limit]
    )


def _build_fallback_reply(query: str, recommendations: List[Product]) -> str:
    if not recommendations:
        return (
            "I could not find a close match right now. Try adding details like product type, budget, "
            "or preferred region."
        )

    names = ", ".join(product.name for product in recommendations[:3])
    return f"Based on your request ({query}), these are strong matches: {names}."


def _openai_response(query: str, ranked_products: List[Tuple[Product, float]]) -> Dict:
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key or OpenAI is None:
        return {}

    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    shortlist = [
        {
            "id": p.id,
            "name": p.name,
            "price": str(p.discounted_price or p.price),
            "region": p.region,
            "category": p.category.name if p.category else "",
            "stock": p.stock,
            "rating": float(getattr(p, "avg_rating", 0) or 0),
            "heuristic_score": round(score, 2),
        }
        for p, score in ranked_products[:15]
    ]

    # Enhanced system prompt with knowledge base context
    kb_context = _get_knowledge_base_context()
    platform_context = _get_platform_context()
    
    system_prompt = f"""You are an expert e-commerce shopping assistant for RootReach.
Your responsibilities:
1. Help customers find the perfect products
2. Answer questions about policies, shipping, and payments
3. Provide personalized recommendations
4. Be helpful, concise, and professional

Platform Information:
{platform_context}

Knowledge Base:
{kb_context}

IMPORTANT: Return ONLY valid JSON with these keys:
- reply: A helpful, concise response (2-3 sentences max)
- product_ids: Array of recommended product IDs (up to 6)
"""
    
    user_prompt = (
        f"Customer query: {query}\n"
        f"Available products shortlist:\n{json.dumps(shortlist)}\n"
        "Select best matching product_ids and provide a helpful response."
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = completion.choices[0].message.content or "{}"
        return json.loads(content)
    except:
        return {}


def get_shopping_assistant_result(query: str, top_k: int = 6) -> AssistantResult:
    query = (query or "").strip()
    if not query:
        return AssistantResult(
            reply="Tell me what you want to buy, and I will recommend products.",
            recommendations=[],
            used_llm=False,
        )

    products = _candidate_products()
    tokens = _tokenize(query)
    ranked = sorted(
        ((product, _score_product(product, tokens)) for product in products),
        key=lambda item: item[1],
        reverse=True,
    )

    top_ranked = ranked[:top_k]
    ranked_ids = [product.get('id') if isinstance(product, dict) else product.id for product, _score in top_ranked if _score > 0]
    
    # Fetch full Product objects for top ranked items
    fallback_recommendations = list(Product.objects.filter(id__in=ranked_ids).select_related('category'))[:top_k]
    fallback_reply = _build_fallback_reply(query, fallback_recommendations)

    # Skip LLM call if no API key set for speed
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if api_key and OpenAI is not None:
        llm_data = _openai_response(query, ranked[:15])
        if llm_data:
            product_ids = [pid for pid in llm_data.get("product_ids", []) if isinstance(pid, int)]
            llm_recommendations = list(Product.objects.filter(id__in=product_ids).select_related('category'))[:top_k]
            if llm_recommendations:
                return AssistantResult(
                    reply=llm_data.get("reply", fallback_reply),
                    recommendations=llm_recommendations,
                    used_llm=True,
                )

    return AssistantResult(
        reply=fallback_reply,
        recommendations=fallback_recommendations,
        used_llm=False,
    )


# ====================================
# MESSAGE SUGGESTION API
# ====================================

def get_message_suggestions(message: str, product_id: int = None) -> Dict:
    """Get AI-powered suggestions for responding to a message"""
    try:
        # Find similar message patterns
        suggestions = AIMessageSuggestion.objects.filter(
            is_active=True,
            product_id=product_id
        ).order_by('-usage_count')[:5]
        
        response_data = {
            'suggestions': [],
            'template_matches': []
        }
        
        # Get suggested responses
        for suggestion in suggestions:
            try:
                responses = json.loads(suggestion.response_suggestions)
                response_data['suggestions'].extend(responses[:2])
                response_data['template_matches'].append({
                    'type': suggestion.suggestion_type,
                    'template': suggestion.message_template
                })
            except:
                pass
        
        # If no AI suggestions, return smart defaults based on message type
        if not response_data['suggestions']:
            defaults = _get_default_suggestions(message)
            response_data['suggestions'] = defaults
            
        return response_data
    except Exception as e:
        return {'suggestions': [], 'error': str(e)}


def _get_default_suggestions(message: str) -> List[str]:
    """Generate smart default suggestions based on message content"""
    message_lower = message.lower()
    
    suggestions = []
    
    # Price inquiry
    if any(word in message_lower for word in ['price', 'cost', 'how much', 'expensive', 'cheap']):
        suggestions.extend([
            "The current price is shown above. We also offer bulk discounts!",
            "Special offer available for quantity purchases. Let me know if interested!",
            "Best price guaranteed. Compare with others and let us know!"
        ])
    
    # Availability/Stock
    elif any(word in message_lower for word in ['available', 'stock', 'in stock', 'when available']):
        suggestions.extend([
            "Yes, it's currently in stock and ready to ship!",
            "In stock and available for immediate delivery.",
            "Limited stock available. I recommend ordering soon!"
        ])
    
    # Shipping/Delivery
    elif any(word in message_lower for word in ['ship', 'deliver', 'fast', 'how long', 'arrival']):
        suggestions.extend([
            "Delivery typically takes 3-7 days depending on your location.",
            "We offer same-week delivery for most areas!",
            "Free shipping on orders above a certain amount. Details in checkout!"
        ])
    
    # Quality/Specifications
    elif any(word in message_lower for word in ['quality', 'spec', 'details', 'material', 'size']):
        suggestions.extend([
            "High quality product verified by hundreds of positive reviews.",
            "All details are in the product description above.",
            "Premium quality at competitive price. Check specifications in the listing!"
        ])
    
    # Greeting/General
    else:
        suggestions.extend([
            "Thanks for your interest! How can I help you today?",
            "Happy to assist! Do you have any questions about this product?",
            "I'm here to help! Feel free to ask anything about this item."
        ])
    
    return suggestions[:3]