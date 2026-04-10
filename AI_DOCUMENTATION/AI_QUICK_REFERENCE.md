# AI System - Developer Quick Reference 👨‍💻

**Quick access** for developers implementing AI features. Full documentation: `AI_SYSTEM_DOCUMENTATION.md`

## One-Liner Usage

```python
from core.ai_manager import get_ai_response
response, service = get_ai_response("Your question")
```

## Common Patterns

### Pattern 1: Simple Chatbot Response
```python
def chatbot_view(request):
    from core.ai_manager import get_ai_response
    
    question = request.POST.get('message')
    response, service = get_ai_response(question)
    
    return JsonResponse({
        'response': response,
        'service': service
    })
```

### Pattern 2: Message Suggestions for Sellers
```python
def get_seller_suggestions(request):
    from core.ai_manager import get_ai_response
    
    customer_message = request.GET.get('msg')
    suggestion, _ = get_ai_response(f"Write a professional seller response for: {customer_message}")
    
    return JsonResponse({'suggestion': suggestion})
```

### Pattern 3: Product Recommendations
```python
def recommend_products(request):
    from core.ai_assistant import get_shopping_assistant_result
    
    query = request.GET.get('q')
    result = get_shopping_assistant_result(query)
    
    return JsonResponse({
        'reply': result.reply,
        'products': [p.id for p in result.recommendations]
    })
```

### Pattern 4: Check Which Service Used
```python
response, service = get_ai_response("question")

if service == 'gemini':
    print("✨ Using Google's Gemini")
elif service == 'huggingface':
    print("⚡ Using HuggingFace (Gemini quota likely exhausted)")
elif service == 'fallback':
    print("🔄 Using pattern matching (APIs might be down)")
```

### Pattern 5: Admin - View Statistics
```python
from core.ai_manager import get_ai_stats

@login_required
def admin_ai_stats(request):
    if not request.user.is_staff:
        return redirect('home')
    
    stats = get_ai_stats()
    return render(request, 'admin_ai_stats.html', {'stats': stats})
```

## Configuration

### Enable Gemini (Recommended)
```
# In .env file:
GEMINI_API_KEY=your_free_key_from_makersuite.google.com
```

### Database Setup
```bash
python manage.py migrate  # Creates AI tables
python manage.py populate_ai_knowledge_base  # Loads 22 FAQs
```

## API Endpoints

| Endpoint | Method | Auth | Returns |
|----------|--------|------|---------|
| `/api/chatbot/` | POST | None | `{success, response, service, error}` |
| `/api/ai-stats/` | GET | Admin | `{stats}` |
| `/api/ai-stats/reset/` | POST | Admin | `{success, message}` |
| `/api/message-suggestions/` | POST | Login | `{success, suggestions}` |

## Test Queries

```bash
# Test endpoint
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"message":"What products do you have?"}'

# PowerShell
$body = @{message = 'test'} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/api/chatbot/" \
  -Method Post -ContentType "application/json" -Body $body
```

## JavaScript Usage

```javascript
// Fetch response
const res = await fetch('/api/chatbot/', {
    method: 'POST',
    body: JSON.stringify({message: 'test'})
});
const data = await res.json();
console.log(data.response);  // AI response
console.log(data.service);   // gemini/huggingface/fallback
```

## Logging & Debugging

### View logs
```bash
tail -f logs/django.log | grep "AI\|gemini\|huggingface"
```

### Check stats
```python
from core.ai_manager import get_ai_stats
print(get_ai_stats())  # Total responses by service
```

### Force service (testing)
```python
from core.ai_manager import get_ai_manager
get_ai_manager().force_service('fallback')  # For testing
```

## Error Handling

```python
try:
    response, service = get_ai_response(user_input)
except Exception as e:
    response = "I'm having trouble right now, please try again later"
    service = None
```

## Key Files

| File | Purpose |
|------|---------|
| `core/ai_manager.py` | Main manager with fallback logic |
| `core/gemini_chatbot.py` | Gemini API integration |
| `core/huggingface_chatbot.py` | HuggingFace free inference |
| `core/ai_assistant.py` | Shopping assistant |
| `core/models.py` | AIKnowledgeBase, AIMessageSuggestion |
| `core/views.py` | API endpoints |
| `core/urls.py` | URL routes |

## Service Priority

```
Try Gemini (free tier)
  ↓ (if quota exhausted)
Try HuggingFace (free API)
  ↓ (if connection failed)
Use Pattern Matching (local, always works)
```

## Cost: $0/month

- Gemini: Free tier (1500 req/min)
- HuggingFace: Completely free
- Pattern Matching: Local, instant

## Features
- ✅ Auto-switching between services
- ✅ Usage tracking
- ✅ Quota detection
- ✅ Admin monitoring
- ✅ Always returns response
- ✅ Never fails

## Future Enhancements

- [ ] Dashboard widget for service status
- [ ] Email alerts on quota exhaustion
- [ ] Response quality scoring
- [ ] User feedback on responses
- [ ] Multi-language support
- [ ] Custom model fine-tuning

---

**For full documentation:** See `AI_SYSTEM_DOCUMENTATION.md`
