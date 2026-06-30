# 📚 RootReach Developer & Feature Guide

Welcome to the consolidated documentation for the RootReach E-Commerce Platform. This guide covers the core features, AI integrations, and algorithms powering the platform.

---

## 🤖 1. AI Chat & Knowledge Base

The platform features a smart AI Assistant that provides automatic message suggestions and answers FAQs based on platform policies.

### For Admins
Manage the AI's behavior directly from the Django Admin dashboard:
- **Manage FAQs**: Go to `Admin → AI Knowledge Base` to add questions and answers. Set priority (0-10) to control importance.
- **Message Templates**: Go to `Admin → AI Message Suggestion` to manage autocomplete responses for common scenarios (e.g., price negotiation, shipping).

### Quick Commands
```bash
# Populate initial AI Knowledge Base FAQs
python manage.py populate_ai_knowledge_base
```

### UI Integration
To enable AI suggestions in any chat template, include the following component:
```html
{% include "components/ai_message_suggestions.html" %}
```
*Note: For deep technical details on the AI architecture, refer to the `AI_DOCUMENTATION/` directory.*

---

## 🔥 2. Trending & Rural Products Algorithm

The home page features dynamic sections that use **real database metrics** (not dummy data) to recommend products to users.

### "Trending In Your Area"
Shows popular products specific to the user's region.
- **Algorithm**: Filters products by the user's `region` field.
- **Ranking**: Sorted by `order_count` (popularity), `avg_rating` (quality), and `created_at` (freshness).

### "Popular Rural Products"
Highlights authentic, local, and artisan goods.
- **Algorithm**: Scans product names and descriptions for keywords like *organic, handmade, rural, local, artisan*.
- **Ranking**: Sorted by total engagement (`orders` + `reviews`) and `avg_rating`.

### How to Test
1. Add products using keywords (e.g., "handmade pottery").
2. Set the product's region (e.g., "Jessore").
3. Purchase them (creates Orders) and leave Reviews.
4. The products will automatically rise in the Trending and Rural sections!

---

## 🐛 3. Quick Troubleshooting

- **Knowledge base is empty?** Run `python manage.py populate_ai_knowledge_base`.
- **Suggestions API returning 404/403?** Ensure `{% csrf_token %}` is in your form and `python manage.py migrate` has been run.
- **Products not showing in Trending?** Ensure product `stock > 0`, region matches the user, and it has at least 1 order.
- **JavaScript errors in chat?** Ensure your template includes `data-product-id="{{ product.id }}"`.

---
*Generated: April 2026. This file replaces the legacy AI, Quick Reference, and Trending documentation files.*
