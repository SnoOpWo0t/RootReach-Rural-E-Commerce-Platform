# 📋 AI Chat & Messages Quick Reference Guide

## 🎯 What's New

| Feature | What It Does | How to Access |
|---------|-------------|--------------|
| **Enhanced AI Chat** | AI knows your platform policies & FAQs | Visit `/ai-assistant/` |
| **Message Suggestions** | AI suggests responses while typing | Chat pages (after template integration) |
| **FAQ Management** | Add/edit platform questions & answers | Admin → AI Knowledge Base |
| **Response Templates** | Manage message suggestion patterns | Admin → AI Message Suggestion |

---

## 👥 For Different Users

### 🛍️ Buyers Using Chat
1. Open any product chat
2. Start typing your message
3. See AI suggestions appear (blue box)
4. Click suggestion to use it
5. Send message

### 💼 Sellers Using Chat
1. Go to "Seller Messages"
2. Click on a buyer message
3. Start typing reply
4. AI suggestions appear
5. Click to insert, then send

### 👨‍💼 Admins Managing FAQs
```
Dashboard → Admin → AI Knowledge Base → Add
```
- **Question**: What users ask (e.g., "Can I return items?")
- **Answer**: Your response (e.g., "Yes, 30-day return policy...")
- **Keywords**: Help matching (e.g., "return, refund, money back")
- **Category**: Choose type (FAQ, Policy, Shipping, etc.)
- **Priority**: 0-10 (higher = more important)
- **Active**: Check to enable

**Example:**
```
Question: Can I return items?
Answer: Yes, within 30 days of purchase
Keywords: return, refund, money back, changes my mind
Category: Policy
Priority: 10
Active: ✓
```

### 📝 Admins Managing Message Templates
```
Dashboard → Admin → AI Message Suggestion → Add
```
- **Suggestion Type**: greeting, product_inquiry, price_negotiation, etc.
- **Message Template**: Example buyer message
- **Response Suggestions**: JSON array `["Response 1", "Response 2", "Response 3"]`
- **Active**: Check to enable

**Example:**
```
Type: price_negotiation
Template: Can you reduce the price?
Responses: [
  "We offer bulk discounts!",
  "Our price is competitive",
  "Free shipping available!"
]
Active: ✓
```

---

## 🔧 Quick Commands

### Check Knowledge Base Status
```bash
cd f:\RoorReach_1\RoorReach_1
python manage.py shell

# Count entries
from core.models import AIKnowledgeBase
print(AIKnowledgeBase.objects.count())  # Should show 22+

# View all FAQs
AIKnowledgeBase.objects.values_list('question', flat=True)

# Exit
exit()
```

### Test API Suggestion
```bash
# Using curl (Windows PowerShell)
$body = @{
    message = "Can you reduce the price?"
    product_id = 1
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/message-suggestions/" `
  -Method POST -Body $body -ContentType "application/json"
```

### Reload Knowledge Base
```bash
python manage.py populate_ai_knowledge_base
```

---

## 🛠️ Integration Checklist

- [ ] Review `AI_ENHANCEMENTS_SETUP.md`
- [ ] Read `AI_MESSAGE_SUGGESTIONS_INTEGRATION.md`
- [ ] Add component to `product_chat.html`:
  ```html
  {% include "components/ai_message_suggestions.html" %}
  ```
- [ ] Add component to `seller_messages.html`
- [ ] Add component to `buyer_order_messages.html`
- [ ] Test suggestions in chat
- [ ] Customize CSS if needed
- [ ] Add custom FAQs via admin

---

## 📊 Admin Dashboard Locations

| Feature | URL |
|---------|-----|
| AI Knowledge Base | `/admin/core/aiknowledgebase/` |
| Message Suggestions | `/admin/core/aimessagesuggestion/` |
| Products | `/admin/core/product/` |
| Orders | `/admin/core/order/` |

---

## 🐛 Troubleshooting

### "Suggestions not showing"
1. Check template has: `{% include "components/ai_message_suggestions.html" %}`
2. Open DevTools (F12) → Network tab
3. Type in message field
4. Look for `/api/message-suggestions/` request
5. Check if request is successful (200 status)

### "No knowledge base entries"
1. Run: `python manage.py populate_ai_knowledge_base`
2. Check admin: `/admin/core/aiknowledgebase/`
3. Should show 22+ entries

### "API returns 403"
1. Ensure CSRF token in form: `{% csrf_token %}`
2. Check browser console for errors
3. Verify user is logged in

---

## 📈 Suggested FAQ Additions

Based on your platform, consider adding:

**High Priority (Priority: 9-10)**
- How do I track my order?
- What is your return policy?
- How long does shipping take?
- How do I become a seller?
- What payment methods are accepted?

**Medium Priority (Priority: 6-8)**
- How do I update my profile?
- How do I search for products?
- Can I compare products?
- How do I leave a review?
- Is payment secure?

**Lower Priority (Priority: 3-5)**
- How do I delete my account?
- What are your business hours?
- Do you have a mobile app?
- Why is item X expensive?

---

## 💡 Message Suggestions Strategy

### Most Useful Types
1. **price_negotiation** - Very common
2. **shipping_question** - Frequent
3. **product_inquiry** - Important
4. **greeting** - Quick wins
5. **order_status** - High value

### Low Response Time Topics
- Greetings
- Product specifications
- Stock availability
- Shipping info

### High Value but Complex
- Returns/refunds
- Custom orders
- Price negotiation
- Bulk purchases

---

## 📞 Getting Help

### Check These First
1. **Django Admin**: `/admin/` - All features visible and editable
2. **Guides**: Read the setup and integration markdown files
3. **Logs**: `python manage.py shell` - Debug database queries
4. **API**: Manual curl/Postman testing

### Common Issues

**Issue**: Knowledge base is empty
**Fix**: `python manage.py populate_ai_knowledge_base`

**Issue**: Suggestions API 404
**Fix**: Run `python manage.py migrate`

**Issue**: Suggestions not appearing in chat
**Fix**: Add `{% include "components/ai_message_suggestions.html" %}` to template

**Issue**: JavaScript errors in console
**Fix**: Check template data attributes: `data-product-id="{{ product.id }}"`

---

## 🎓 Learning Resources

### Files to Read
- `AI_IMPLEMENTATION_COMPLETE.md` - Overview of all changes
- `AI_ENHANCEMENTS_SETUP.md` - Detailed setup guide
- `AI_MESSAGE_SUGGESTIONS_INTEGRATION.md` - How to add UI to templates
- `core/ai_assistant.py` - AI logic code
- `core/views.py` - API endpoint code

### Code References
- **Main AI Logic**: `core/ai_assistant.py`
- **API Endpoint**: `core/views.py` → `get_message_suggestions_api()`
- **Models**: `core/models.py` → `AIKnowledgeBase`, `AIMessageSuggestion`
- **URL Route**: `core/urls.py` → `/api/message-suggestions/`
- **Component**: `core/templates/components/ai_message_suggestions.html`

---

## ⚡ Performance Tips

1. **Keep Knowledge Base Lean**: Remove inactive entries
2. **Organize by Priority**: Set appropriate priorities
3. **Batch Import**: Add multiple FAQs at once
4. **Monitor Usage**: Check admin usage_count field
5. **Cache Popular**: Pin frequently used suggestions

---

## 🎨 Customization Examples

### Change Suggestion Box Color
Edit `components/ai_message_suggestions.html`:
```css
.ai-suggestions {
    background: #e8f5e9;  /* Green instead of blue */
    border-left-color: #2e7d32;
}
```

### Change Number of Suggestions
Edit JavaScript:
```javascript
suggestions.slice(0, 5)  // Show 5 instead of 3
```

### Change Wait Time for Suggestions
Edit initialization:
```javascript
debounceDelay: 300  // 300ms instead of 500ms
```

---

## ✨ Pro Tips

1. **Use High Priority**: Set frequently asked questions to priority 10
2. **Specific Keywords**: Use exact terms customers use
3. **Template Variety**: Create 3+ response templates for each type
4. **Monitor Usage**: Check usage_count to see what's popular
5. **Update Regularly**: Review and refresh FAQs quarterly
6. **Test Before Deploy**: Use admin interface to test new entries
7. **Link to Products**: Create product-specific suggestions

---

## 📋 Checklist for Success

- [ ] Knowledge base populated (22+ entries)
- [ ] Admin can access both AI models
- [ ] API endpoint tested and working
- [ ] UI component integrated into templates
- [ ] Messages showing suggestions in chat
- [ ] Custom FAQs added
- [ ] Custom message templates added
- [ ] Team trained on new features
- [ ] Users can see improvements
- [ ] Analytics tracked (usage_count)

---

## 🎉 You're All Set!

Your AI-powered messaging system is ready to:
- ✅ Help buyers get faster responses
- ✅ Help sellers respond intelligently
- ✅ Reduce support tickets
- ✅ Improve customer satisfaction
- ✅ Scale conversations efficiently

**Start by**:
1. Reading the setup guide
2. Adding FAQs in admin
3. Integrating UI to templates
4. Testing with real messages
5. Monitoring usage and feedback

**Questions?** Check the admin panel and markdown guides - everything is documented!
