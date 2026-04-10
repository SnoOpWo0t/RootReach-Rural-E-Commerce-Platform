"""
Management command to add helpful AI context data to products
Enriches product information for better AI recommendations
"""

from django.core.management.base import BaseCommand
from core.models import Product, Category
import json


class Command(BaseCommand):
    help = 'Enrich products with AI context data (categories, tags, descriptions)'

    def handle(self, *args, **options):
        """Add AI-friendly data to products"""
        
        # Get all products
        products = Product.objects.all()
        updated_count = 0
        
        for product in products:
            # Skip if already has rich data
            if product.description and len(product.description) > 50:
                continue
            
            # Based on category, provide smarter description
            category = product.category
            
            # Sample AI-enhanced descriptions by category
            descriptions = self._get_category_descriptions()
            
            if category and category.name in descriptions:
                base_desc = descriptions[category.name]
                if not product.description or len(product.description) < 30:
                    product.description = base_desc.format(
                        name=product.name,
                        price=product.price
                    )
                    product.save()
                    updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Enriched {updated_count} products with AI data'))
        
        # List categories with data
        categories = Category.objects.all()
        self.stdout.write(f'✓ Processed {len(categories)} categories')

    def _get_category_descriptions(self):
        """Return AI-enhanced descriptions by category"""
        return {
            'Electronics': 'Quality {name} - reliable performance guaranteed. Perfect for daily use and long-term durability. Original product with warranty coverage.',
            
            'Fashion': 'Stylish {name} - latest trends and comfortable fit. Premium quality material. Available in multiple sizes and colors. Perfect purchase for fashion lovers.',
            
            'Home & Garden': 'Premium {name} for your home - durable and practical. Enhances home beauty and functionality. Best quality at {price}. Great for decoration and daily use.',
            
            'Beauty & Personal Care': '{name} - quality beauty product for personal care. Safe and effective. Perfect for all skin types. Award-winning product with excellent reviews.',
            
            'Books': '{name} - must-read publication. Educational and engaging content. Perfect gift for readers. Original edition from trusted publisher.',
            
            'Sports & Outdoors': 'Premium {name} for sports enthusiasts. Durable and performance-tested. Ideal for outdoor activities. Professional grade quality.',
            
            'Toys & Games': 'Fun {name} for all ages - safe and educational. Highly durable construction. Great for family entertainment. Children and adults love it!',
            
            'Food & Groceries': 'Quality {name} - fresh and hygienic. Best taste guaranteed. Sourced from trusted suppliers. Daily essentials at affordable price {price}.',
            
            'Automotive': 'Reliable {name} for vehicles - performance tested. Improves vehicle functionality. Easy installation. Long-lasting durability.',
            
            'Stationery': 'Essential {name} for students and professionals. Quality writing instruments and paper. Perfect for school, office, or study.',
        }
