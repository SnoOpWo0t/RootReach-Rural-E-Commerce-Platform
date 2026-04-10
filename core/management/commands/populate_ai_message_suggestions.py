"""
Management command to populate AI Message Suggestion Templates
Provides sellers with suggested responses to common buyer inquiries
"""

from django.core.management.base import BaseCommand
from core.models import AIMessageSuggestion
import json


class Command(BaseCommand):
    help = 'Populate AI message suggestion templates for sellers'

    def handle(self, *args, **options):
        """Populate message suggestion templates"""
        
        if AIMessageSuggestion.objects.exists():
            self.stdout.write(self.style.WARNING('✓ Message suggestions already exist. Skipping.'))
            return
        
        templates = self._get_suggestion_templates()
        
        created_count = 0
        for template in templates:
            suggestion, created = AIMessageSuggestion.objects.get_or_create(
                message_template=template['template'],
                defaults={
                    'suggestion_type': template['type'],
                    'response_suggestions': json.dumps(template['suggestions']),
                    'is_active': True,
                    'usage_count': 0
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully added {created_count} message suggestion templates!'))
        
        # Show summary
        total = AIMessageSuggestion.objects.filter(is_active=True).count()
        by_type = AIMessageSuggestion.objects.filter(is_active=True).values('suggestion_type').distinct().count()
        self.stdout.write(self.style.SUCCESS(f'✓ Total templates: {total} across {by_type} types'))

    def _get_suggestion_templates(self):
        """Return message suggestion templates"""
        return [
            # ========================
            # PRICE INQUIRIES
            # ========================
            {
                'type': 'price_inquiry',
                'template': 'Is the price negotiable? Can you offer a discount?',
                'suggestions': [
                    'The price is fixed and competitive. However, we offer bulk discounts for orders of 5+ units (10% off).',
                    'Best price available! We match market rates. Order now to get the best deal before prices increase.',
                    'Limited time offer: Order today and get 5% off! Check our current promotions.',
                ]
            },
            {
                'type': 'price_inquiry',
                'template': 'How much is this product?',
                'suggestions': [
                    'The current price is shown in the listing. Free delivery on orders over 500 Tk!',
                    'Exact price is displayed on the product page. We offer payment plans for orders over 5000 Tk.',
                    'Price is competitive and already discounted from retail. Check checkout for exact total including any offers.',
                ]
            },
            {
                'type': 'price_inquiry',
                'template': 'Your price is higher than others. Why?',
                'suggestions': [
                    'Our price includes quality guarantee and fast shipping. Plus, you get buyer protection!',
                    'We ensure original products only. Compare quality, not just price! Our rating proves it.',
                    'Higher price = higher quality and better service. Our reviews speak for themselves.',
                ]
            },

            # ========================
            # AVAILABILITY/STOCK
            # ========================
            {
                'type': 'availability',
                'template': 'Is this available? When will it be in stock?',
                'suggestions': [
                    'Yes, in stock right now! Ready to ship immediately. Order today and get it within 3-5 days.',
                    'Currently out of stock but restocking next week. Want to pre-order? Priority shipping!',
                    'Limited stock available (only 3 left). Recommend ordering ASAP before it sells out.',
                ]
            },
            {
                'type': 'availability',
                'template': 'Do you have this in a different color/size?',
                'suggestions': [
                    'Yes, available in: Black, White, Red, and Blue. Which color do you prefer?',
                    'We have sizes XS to XL in stock. Check our complete range on the main product page.',
                    'Limited availability in other colors but we can special order. 5-7 days extra wait time.',
                ]
            },
            {
                'type': 'availability',
                'template': 'What\'s the minimum order quantity?',
                'suggestions': [
                    'Minimum 1 unit. No bulk requirements! Order as few or as many as you want.',
                    'Typically 1 unit minimum, but bulk discounts available for 5+ units (10% off).',
                    'No minimum order. Special pricing for bulk orders (50+ units available).',
                ]
            },

            # ========================
            # PRODUCT QUALITY & SPECIFICATIONS
            # ========================
            {
                'type': 'quality',
                'template': 'Is this original/authentic?',
                'suggestions': [
                    '100% original guaranteed! Authentic product with warranty. Buy with confidence!',
                    'Yes, official product. Full warranty included. Our reputation depends on authenticity!',
                    'Completely genuine. Money-back guarantee if you find it\'s not original.',
                ]
            },
            {
                'type': 'quality',
                'template': 'What is the warranty/guarantee?',
                'suggestions': [
                    '1-year manufacturer warranty included. Covers all manufacturing defects. Terms detailed in manual.',
                    '6-month warranty + 30-day money-back guarantee. We\'re confident in quality!',
                    'Extended 2-year warranty available for additional 500 Tk. Standard 1-year included.',
                ]
            },
            {
                'type': 'quality',
                'template': 'What material is this made from?',
                'suggestions': [
                    'Premium materials used: [material details]. Check product specs for complete breakdown.',
                    'High-quality [material] construction. Durable and tested for longevity.',
                    'Detailed material composition on the product page. Premium grade used throughout.',
                ]
            },
            {
                'type': 'quality',
                'template': 'Does this come with all accessories?',
                'suggestions': [
                    'Yes! Complete package with all accessories: [list items]. Nothing extra needed.',
                    'Standard accessories included. Optional extras available for purchase if needed.',
                    'All essential items included. See accessory list on product page.',
                ]
            },

            # ========================
            # SHIPPING & DELIVERY
            # ========================
            {
                'type': 'shipping',
                'template': 'How quickly can you ship this?',
                'suggestions': [
                    'Ships same day! You\'ll get tracking tomorrow morning. Delivery in 3-5 days.',
                    'Usually ships within 24 hours. Express option available for 200 Tk (next day).',
                    'Standard shipping: 3-5 days. Express available for faster delivery options.',
                ]
            },
            {
                'type': 'shipping',
                'template': 'What is the shipping cost?',
                'suggestions': [
                    'Free shipping included in price for Dhaka! Only 150 Tk for other divisions.',
                    'Shipping costs depend on location. Calculated at checkout. Free for 3000+ Tk orders.',
                    'Included in the price for metro areas. 100-300 Tk for outside Dhaka (calculated automatically).',
                ]
            },
            {
                'type': 'shipping',
                'template': 'Can you ship to [specific location]?',
                'suggestions': [
                    'Yes, we ship nationwide! Standard delivery to your area is 5-7 days.',
                    'We deliver everywhere in Bangladesh! May take 7-10 days for remote areas.',
                    'Yes, all divisions covered! Confirm your exact location for accurate delivery time.',
                ]
            },
            {
                'type': 'shipping',
                'template': 'How do I track my order?',
                'suggestions': [
                    'You\'ll get tracking number via SMS/email. Track it on RootReach or courier website in real-time.',
                    'I\'ll share tracking details right after shipping. Monitor progress on the platform.',
                    'Automatic tracking provided. Check "My Orders" for live location updates.',
                ]
            },

            # ========================
            # RETURNS & COMPLAINTS
            # ========================
            {
                'type': 'return',
                'template': 'What if the product is damaged/defective?',
                'suggestions': [
                    'Contact me immediately with photos. I\'ll replace it free or issue full refund. 100% satisfaction guaranteed!',
                    'I offer 30-day returns for any issues. Damaged items replaced at no cost.',
                    'Full coverage under buyer protection. Report damage immediately, we\'ll sort it out.',
                ]
            },
            {
                'type': 'return',
                'template': 'Can I return this if I change my mind?',
                'suggestions': [
                    'Yes! 30-day return policy. Return in original condition for full refund.',
                    'Absolutely! You have 30 days. Just ship it back, I\'ll refund after inspection.',
                    'Of course! Money-back guarantee if not satisfied. Return shipping varies by item size.',
                ]
            },
            {
                'type': 'return',
                'template': 'How does the return process work?',
                'suggestions': [
                    'Simple: Request return → I confirm → You ship product → I inspect → Refund issued (3-5 days).',
                    'Report issue in app → Arrange pickup → I inspect → Refund within 7 days.',
                    'Easy process: Request return → Get shipping label → Ship back → Get refund within 10 days.',
                ]
            },

            # ========================
            # PAYMENT & TERMS
            # ========================
            {
                'type': 'payment',
                'template': 'What payment methods do you accept?',
                'suggestions': [
                    'All methods: Credit/Debit Card, bKash, Nagad, Rocket, Bank Transfer. Choose at checkout.',
                    'Accept mobile banking (bKash/Nagad/Rocket) and all cards. Super convenient!',
                    'Multiple options available: Cards, Mobile Banking, Online Payment. Pay however you prefer.',
                ]
            },
            {
                'type': 'payment',
                'template': 'Can I pay cash on delivery?',
                'suggestions': [
                    'Yes! Pay when you receive the product. COD available for most areas.',
                    'Absolutely! Check COD availability for your location at checkout.',
                    'COD available to most locations. Exact delivery time and charges shown.',
                ]
            },
            {
                'type': 'payment',
                'template': 'Can I get discount for bulk order?',
                'suggestions': [
                    'Yes! Bulk pricing: 5-10 units = 10% off, 10+ units = 15% off. Contact me for custom quote.',
                    'Great question! Discounts available: 5+ units (10%), 20+ units (20%). Inform quantity!',
                    'Definitely! Bulk orders get special pricing. Order 10+ for best rates.',
                ]
            },

            # ========================
            # COMPARISON & RECOMMENDATION
            # ========================
            {
                'type': 'recommendation',
                'template': 'How is this compared to brand X?',
                'suggestions': [
                    'Great value compared to brand X! Similar quality, better price. Our buyers prefer it.',
                    'Brand X is more expensive. Ours offers better features at lower cost. Check reviews!',
                    'This offers better value. Comparable quality with more features included.',
                ]
            },
            {
                'type': 'recommendation',
                'template': 'Do you recommend this product?',
                'suggestions': [
                    '100% yes! It\'s our bestseller with 4.8/5 stars. Customers love it!',
                    'Definitely! Best in its category. Check our 500+ 5-star reviews.',
                    'Highly recommended! Best-seller status speaks for itself. Trusted by thousands.',
                ]
            },

            # ========================
            # GENERAL INQUIRY
            # ========================
            {
                'type': 'general',
                'template': 'I have a question about this product.',
                'suggestions': [
                    'Happy to help! What would you like to know? I\'m here for any questions!',
                    'Sure! Ask away. I\'ll answer ASAP with all the details you need.',
                    'Of course! Feel free to ask anything. Detailed answer coming right up!',
                ]
            },
            {
                'type': 'general',
                'template': 'Can I negotiate the price?',
                'suggestions': [
                    'Price is set but reasonable. For bulk orders (5+), I can offer 10% discount.',
                    'Our price is competitive and fair. Slight negotiation possible for large orders.',
                    'Limited flexibility on single units. But bulk buyers get special rates!',
                ]
            },
            {
                'type': 'general',
                'template': 'Thank you for the product!',
                'suggestions': [
                    'You\'re welcome! Happy we could help. Please leave a review if satisfied! 😊',
                    'Thanks for buying! Hope you love it. Your feedback means a lot!',
                    'Pleasure serving you! Please rate us. We\'d love your feedback! ⭐',
                ]
            },
        ]
