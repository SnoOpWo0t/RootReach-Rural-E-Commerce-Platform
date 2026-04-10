# 🔥 Trending & 🌿 Popular Rural Products - How They Work

## 📍 Overview

These two sections on the home page use **real database data** with intelligent algorithms to recommend products based on:
- **User engagement** (orders, reviews, ratings)
- **Location-based popularity** (regional trending)
- **Product categories** (rural/artisan keywords)

---

## 🔥 TRENDING IN YOUR AREA

### What It Does:
Displays products that are currently **trending and popular in the user's region**, based on order volume and ratings.

### Algorithm:
```
1. Get user's region (from user profile's division field)
2. Find products from THAT region sorted by:
   - Most ordered (popularity metric)
   - Highest ratings (quality metric)
   - Most recent (freshness metric)
3. Return top 6 products
4. Fallback: If no region products, show all trending products nationwide
```

### Data Sources:
| Field | Source | Purpose |
|-------|--------|---------|
| `region` | Product model | Filter by user's area |
| `order_count` | Count of Orders linked to product | Popularity score |
| `avg_rating` | Average of Review ratings | Quality metric |
| `created_at` | Product creation date | Freshness |
| `stock > 0` | Product stock field | Only available items |

### Template Location:
📄 [core/templates/home.html](core/templates/home.html#L659) - Lines 659-717

### Real Database Usage:
```python
# Products with most orders in user's region = Trending!
trending_products = Product.objects \
    .filter(region__icontains=user_region, stock__gt=0) \
    .annotate(
        order_count=Count('order'),        # How many times bought
        avg_rating=Avg('reviews__rating')  # Average rating
    ) \
    .order_by('-order_count', '-avg_rating', '-created_at')[:6]
```

---

## 🌿 POPULAR RURAL PRODUCTS

### What It Does:
Shows **authentic, artisan, and locally-produced products** that are popular and well-reviewed.

### Algorithm:
```
1. Search for products matching rural/artisan keywords:
   - "organic", "handmade", "rural", "local", "artisan"
   - "natural", "eco", "traditional", "homemade", "cottage"
   
2. For matching products, calculate engagement score:
   engagement_score = order_count + review_count
   
3. Sort by:
   - Highest engagement (orders + reviews)
   - Highest ratings
   - Most orders
   - Most recent
   
4. Return top 6 products

5. If < 6 found: Fill remaining with high-rated (3.5+) popular products
```

### Data Sources:
| Field | Source | Purpose |
|-------|--------|---------|
| `name` | Product model | Check for rural keywords |
| `description` | Product model | Check for rural keywords |
| `order_count` | Count of Orders | Popularity metric |
| `review_count` | Count of Reviews | Engagement metric |
| `engagement_score` | orders + reviews | Total engagement |
| `avg_rating` | Average Review rating | Quality metric |

### Template Location:
📄 [core/templates/home.html](core/templates/home.html#L718) - Lines 718-776

### Real Database Usage:
```python
# Products matching rural keywords with high engagement
rural_keywords = [
    'organic', 'handmade', 'rural', 'local', 'artisan', 
    'natural', 'eco', 'traditional', 'homemade', 'cottage'
]

rural_products = Product.objects \
    .filter(
        Q(name__icontains_any=rural_keywords) | 
        Q(description__icontains_any=rural_keywords),
        stock__gt=0
    ) \
    .annotate(
        order_count=Count('order'),
        review_count=Count('reviews'),
        engagement_score=Count('order') + Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ) \
    .order_by(
        '-engagement_score',  # Most engaging first
        '-avg_rating',        # Then highest rated
        '-order_count',       # Then most popular
        '-created_at'         # Then most recent
    )[:6]
```

---

## 📊 Key Files Involved

### 1. **Backend Logic** - `core/views.py` (Lines 60-100)
   - Contains the algorithms
   - Fetches data from database
   - Passes to template via context variables

### 2. **Template Display** - `core/templates/home.html`
   - **Trending**: Lines 659-717
   - **Rural**: Lines 718-776
   - Uses context variables: `trending_products`, `rural_products`

### 3. **Database Models** - `core/models.py`
   - **Product**: name, description, region, stock, created_at
   - **Order**: Linked to product, shows purchase count
   - **Review**: Linked to product, provides ratings and engagement

---

## 🗄️ Database Relationships

```
Product
├── name (text to search for keywords)
├── description (text to search for keywords)  
├── region (location filtering)
├── stock (availability)
├── seller (FK to CustomUser)
├── created_at (freshness)
├── reviews (reverse FK from Review)
│   └── rating (for avg_rating annotation)
└── order (reverse FK from Order)
    └── Counted for popularity

Order
├── product (FK to Product) → Used to count purchases
├── buyer (FK to CustomUser)
└── status

Review
├── product (FK to Product) → Used to count reviews
├── reviewer (FK to CustomUser)
├── rating → Used for avg_rating
└── comment
```

---

## 💾 How To Make It Work With Real Data

### Step 1: Add Products with Rural Keywords ✅
When adding products from the admin panel or product form, use these keywords in the name/description:
- ✓ "Organic rice farming"
- ✓ "Handmade pottery"
- ✓ "Local honey"
- ✓ "Eco-friendly baskets"

### Step 2: Generate Orders 🛒
For testing:
1. Add products as a seller
2. Purchase them as a buyer → Creates Order records
3. Products will automatically appear in "Trending"

### Step 3: Add Reviews ⭐
1. Go to purchased products
2. Leave reviews with ratings (1-5 stars)
3. System recalculates avg_rating automatically

### Step 4: Set Region Fields 📍
Ensure in Product model:
```python
product.region = 'Jessore'  # or Dhaka, Sylhet, etc.
```
Trending will now show products from user's region!

---

## 🔍 Testing Queries

### Test Trending Products:
```python
from core.models import Product, Order, Review
from django.db.models import Avg, Count

trending = Product.objects.annotate(
    order_count=Count('order', distinct=True),
    avg_rating=Avg('reviews__rating')
).order_by('-order_count', '-avg_rating')[:6]

for p in trending:
    print(f"{p.name} - Orders: {p.order_count}, Rating: {p.avg_rating}")
```

### Test Rural Products:
```python
rural_keywords = ['organic', 'handmade', 'rural', 'local', 'artisan', 'natural']
rural_query = Q()
for keyword in rural_keywords:
    rural_query |= Q(name__icontains=keyword) | Q(description__icontains=keyword)

rural = Product.objects.filter(rural_query).annotate(
    engagement=Count('order') + Count('reviews'),
    avg_rating=Avg('reviews__rating')
).order_by('-engagement', '-avg_rating')[:6]

for p in rural:
    print(f"{p.name} - Engagement: {p.engagement}, Rating: {p.avg_rating}")
```

---

## 🎯 Live Metrics Tracked

### For Each Product:
| Metric | Used In | Calculation |
|--------|---------|-------------|
| **order_count** | Both sections | Count of all linked Order records |
| **review_count** | Rural products | Count of all linked Review records |
| **engagement_score** | Rural products | order_count + review_count |
| **avg_rating** | Both sections | Average of all review.rating values |
| **created_at** | Tiebreaker | Most recent first if scores equal |

---

## ✨ What Makes It Real

❌ **NOT DUMMY DATA** - The system uses:
- ✅ Actual database product records
- ✅ Real order history (how many times sold)
- ✅ Real customer reviews (ratings and engagement)
- ✅ Real regional data (user's division/location)
- ✅ Real keyword matching (product name/description)

Every product shown is dynamically calculated based on **actual user behavior and purchases**.

---

## 📈 Optimization Tips

To make products appear in these sections:

1. **For Trending**:
   - Get orders (customers buying)
   - Get high ratings (customers loving it)
   - Keep stock > 0

2. **For Rural**:
   - Use keywords: organic, handmade, local, artisan, etc.
   - Get orders and reviews (engagement)
   - Maintain high ratings (3.5+)

---

## 🐛 Troubleshooting

### Products not showing?
- [ ] Check if `stock > 0`
- [ ] Verify `region` is set
- [ ] Ensure product has at least 1 order or review
- [ ] Check keywords in name/description for rural section

### Wrong products showing?
- [ ] Ratings not calculated: Add review with rating
- [ ] Order count low: Purchase more products
- [ ] Region not matching: Update product region field

---

**Last Updated**: April 4, 2026
**Status**: ✅ Fully Functional with Real Data
