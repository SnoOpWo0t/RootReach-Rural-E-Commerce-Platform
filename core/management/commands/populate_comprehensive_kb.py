"""
Management command to populate expanded AI knowledge base with comprehensive data
including FAQs, policies, seller guides, and product information
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import AIKnowledgeBase
import json


class Command(BaseCommand):
    help = 'Populate comprehensive AI knowledge base with FAQs, policies, seller guides, and product info'

    def handle(self, *args, **options):
        """Populate expanded knowledge base"""
        
        # Check if already populated
        if AIKnowledgeBase.objects.filter(category__in=['faq', 'payment', 'shipping', 'policy']).count() > 30:
            self.stdout.write(self.style.WARNING('✓ Knowledge base already has comprehensive data. Skipping.'))
            return
        
        knowledge_items = self._get_comprehensive_knowledge()
        
        created_count = 0
        for item in knowledge_items:
            kb, created = AIKnowledgeBase.objects.get_or_create(
                category=item['category'],
                question=item['question'],
                defaults={
                    'answer': item['answer'],
                    'keywords': item.get('keywords', ''),
                    'priority': item.get('priority', 5),
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully added {created_count} knowledge base entries!'))
        
        # Show summary
        total = AIKnowledgeBase.objects.filter(is_active=True).count()
        by_category = AIKnowledgeBase.objects.filter(is_active=True).values('category').distinct().count()
        self.stdout.write(self.style.SUCCESS(f'✓ Total entries: {total} across {by_category} categories'))

    def _get_comprehensive_knowledge(self):
        """Return comprehensive knowledge base items"""
        return [
            # ========================
            # BUYER FAQs
            # ========================
            {
                'category': 'faq_buyer',
                'question': 'What is RootReach?',
                'answer': 'RootReach is Bangladesh\'s leading e-commerce marketplace connecting buyers and sellers. We provide secure payments, reliable shipping nationwide, quality-verified products, and buyer protection.',
                'keywords': 'what is rootreach, platform, marketplace, bangladesh',
                'priority': 10
            },
            {
                'category': 'faq_buyer',
                'question': 'How do I create an account?',
                'answer': 'Click "Sign Up" on the homepage. Enter your email, create a secure password, and complete your profile with your name and phone number. Instant account creation!',
                'keywords': 'register, signup, account, create account',
                'priority': 9
            },
            {
                'category': 'faq_buyer',
                'question': 'How do I search for products?',
                'answer': 'Use the search bar on the homepage, browse by categories, or use our smart filters (price, rating, region, seller). You can also compare products side-by-side.',
                'keywords': 'search, find products, browse, categories',
                'priority': 8
            },
            {
                'category': 'faq_buyer',
                'question': 'How do I place an order?',
                'answer': 'Add products to cart, review items, enter delivery address, choose payment method, and click "Place Order". You\'ll get instant order confirmation with tracking number.',
                'keywords': 'order, buy, purchase, checkout',
                'priority': 9
            },
            {
                'category': 'faq_buyer',
                'question': 'Can I use a discount code?',
                'answer': 'Yes! Enter promotional codes at checkout if you have them. Check our promotions page for current offers and seasonal discounts.',
                'keywords': 'discount, coupon, code, promo',
                'priority': 7
            },
            {
                'category': 'faq_buyer',
                'question': 'What if I forget my password?',
                'answer': 'Click "Forgot Password" on the login page. Enter your email and we\'ll send you a reset link. Create a new password and you\'re back in!',
                'keywords': 'password, forgot, reset, login',
                'priority': 6
            },
            {
                'category': 'faq_buyer',
                'question': 'Can I edit my order after placing it?',
                'answer': 'You can edit your order if the seller hasn\'t confirmed it yet. Go to Orders → select order → click Edit. Once confirmed, contact support.',
                'keywords': 'edit order, modify order, change order',
                'priority': 6
            },
            {
                'category': 'faq_buyer',
                'question': 'How do I contact the seller?',
                'answer': 'Click "Chat with Seller" on the product page or your order. You can ask questions, negotiate, or discuss issues directly with the seller.',
                'keywords': 'contact seller, message, chat, seller communication',
                'priority': 7
            },
            {
                'category': 'faq_buyer',
                'question': 'How do I leave a review?',
                'answer': 'After delivery, go to your order and click "Write Review". Rate the product (1-5 stars) and write your honest feedback. Reviews help other buyers!',
                'keywords': 'review, rating, feedback, star rating',
                'priority': 7
            },
            {
                'category': 'faq_buyer',
                'question': 'Can I cancel my order?',
                'answer': 'Yes, you can cancel before the seller confirms it. Go to Orders → select order → click Cancel. You\'ll get a full refund if payment was made.',
                'keywords': 'cancel order, order cancellation',
                'priority': 8
            },
            {
                'category': 'faq_buyer',
                'question': 'How many categories are available?',
                'answer': 'RootReach has 8 main product categories: Electronics, Fashion, Home & Garden, Sports, Books, Groceries, Beauty, and Automotive. Each category has thousands of products from verified sellers. You can browse by category or search for specific items!',
                'keywords': 'categories, category, how many, product types, browse categories',
                'priority': 8
            },
            {
                'category': 'faq_buyer',
                'question': 'What categories do you have?',
                'answer': 'Our categories include: Electronics, Fashion, Home & Garden, Sports, Books, Groceries, Beauty, and Automotive. Each has subcategories for easier browsing. Check the Categories page to explore all items!',
                'keywords': 'categories list, product categories, what categories',
                'priority': 8
            },

            # ========================
            # SELLER FAQs
            # ========================
            {
                'category': 'faq_seller',
                'question': 'How do I become a seller?',
                'answer': 'Go to "Sell Zone" → "Apply to Sell". Fill your business details, bank info, and upload documents. Admin approval takes 2-3 business days. Start selling after approval!',
                'keywords': 'seller, become seller, apply seller, how to sell',
                'priority': 10
            },
            {
                'category': 'faq_seller',
                'question': 'What documents do I need to become a seller?',
                'answer': 'You\'ll need: National ID, business registration (if applicable), bank account info, and store details. Documents should be clear and valid.',
                'keywords': 'seller documents, requirements, registration',
                'priority': 9
            },
            {
                'category': 'faq_seller',
                'question': 'How do I add products to my store?',
                'answer': 'Go to Sell Zone → Manage Products → Add Product. Fill in name, description, price, images, stock, and category. Click Save to publish. Instant listing!',
                'keywords': 'add product, list product, upload product',
                'priority': 9
            },
            {
                'category': 'faq_seller',
                'question': 'What is the seller commission?',
                'answer': 'Commission varies by category (typically 5-15%). Exact amount is shown before you list. All fees are transparent in your dashboard.',
                'keywords': 'commission, fee, seller commission',
                'priority': 8
            },
            {
                'category': 'faq_seller',
                'question': 'How are payments made to sellers?',
                'answer': 'After order delivery and 7-day buyer protection period, payment is transferred to your registered bank account. Transfers happen weekly or as per policy.',
                'keywords': 'seller payment, payout, earnings, withdrawal',
                'priority': 9
            },
            {
                'category': 'faq_seller',
                'question': 'How do I respond to buyer questions?',
                'answer': 'Go to Seller Zone → Messages. Respond quickly and professionally. Our AI can suggest helpful replies to save time!',
                'keywords': 'buyer message, chat, communication, response',
                'priority': 8
            },
            {
                'category': 'faq_seller',
                'question': 'Can I increase my product price after listing?',
                'answer': 'Yes! Go to Manage Products → Edit → change price → Save. Price change takes effect immediately.',
                'keywords': 'change price, price update, edit price',
                'priority': 6
            },
            {
                'category': 'faq_seller',
                'question': 'How do I handle low stock?',
                'answer': 'Update stock quantity in Manage Products. When stock reaches 0, listing becomes inactive. Restock anytime to reactivate.',
                'keywords': 'stock, inventory, out of stock',
                'priority': 7
            },
            {
                'category': 'faq_seller',
                'question': 'What happens if a buyer returns a product?',
                'answer': 'Buyer initiates return within 30 days. You\'ll be notified to accept/reject. Accept returns → buyer ships product → you inspect → refund issued or item relisted.',
                'keywords': 'return, refund, seller refund, return policy',
                'priority': 8
            },
            {
                'category': 'faq_seller',
                'question': 'How can I improve my seller rating?',
                'answer': 'Respond quickly, ship on time, describe products accurately, package well, and provide great customer service. Positive reviews boost your rating!',
                'keywords': 'seller rating, reviews, rating up, improve rating',
                'priority': 7
            },

            # ========================
            # PAYMENT & SECURITY
            # ========================
            {
                'category': 'payment',
                'question': 'What payment methods are accepted?',
                'answer': 'We accept: Credit/Debit Card, Mobile Banking (bKash, Nagad, Rocket), Bank Transfer, Wallet. Choose at checkout. All methods are secure.',
                'keywords': 'payment method, pay, credit card, mobile banking, bkash',
                'priority': 9
            },
            {
                'category': 'payment',
                'question': 'Is my payment information secure?',
                'answer': 'Absolutely! Payments use SSL encryption and PCI compliance. Your financial data is never stored on our servers. 100% secure.',
                'keywords': 'secure, safety, encryption, payment security, privacy',
                'priority': 10
            },
            {
                'category': 'payment',
                'question': 'What is your refund policy?',
                'answer': 'Refunds are issued within 5-7 business days of approval. Money is returned to original payment method. Seller return + inspection → admin approval → refund.',
                'keywords': 'refund, return money, refund time',
                'priority': 8
            },
            {
                'category': 'payment',
                'question': 'Can I get an invoice?',
                'answer': 'Yes! You can download invoice from each order. Go to Orders → select order → Download Invoice. Includes all details for your records.',
                'keywords': 'invoice, receipt, bill, download invoice',
                'priority': 6
            },
            {
                'category': 'payment',
                'question': 'What is the buyer protection period?',
                'answer': 'After delivery, you have 7 days to inspect and report issues. You can request return/refund during this time. After 7 days, seller keeps payment.',
                'keywords': 'protection, buyer protection, warranty, 7 days',
                'priority': 9
            },

            # ========================
            # SHIPPING & DELIVERY
            # ========================
            {
                'category': 'shipping',
                'question': 'How long does delivery take?',
                'answer': 'Standard delivery: 3-7 business days depending on location. Urban areas get faster delivery. Express options available (1-2 days for extra fee).',
                'keywords': 'delivery, shipping, how long, days, expedition',
                'priority': 10
            },
            {
                'category': 'shipping',
                'question': 'Do you deliver nationwide?',
                'answer': 'Yes! We ship to all divisions: Dhaka, Chattogram, Khulna, Sylhet, Barishal, Rajshahi, Rangpur, and Mymensingh. Remote areas may take longer.',
                'keywords': 'nationwide, all areas, divisions, region',
                'priority': 8
            },
            {
                'category': 'shipping',
                'question': 'How much does shipping cost?',
                'answer': 'Shipping costs vary by weight and location. Check at checkout before paying. Free shipping often available on orders over set amount.',
                'keywords': 'shipping cost, delivery fee, free shipping',
                'priority': 8
            },
            {
                'category': 'shipping',
                'question': 'Can I track my order?',
                'answer': 'Yes! Go to Orders → Track to see real-time status. You\'ll see: Pending → Confirmed → Shipped → In Transit → Out for Delivery → Delivered.',
                'keywords': 'track order, tracking, order status, where is',
                'priority': 9
            },
            {
                'category': 'shipping',
                'question': 'What if my order is delayed?',
                'answer': 'Check tracking for updates. If delayed beyond estimated date, contact support with order number. We\'ll investigate and compensate if our fault.',
                'keywords': 'delayed, late, delayed delivery, delay',
                'priority': 7
            },
            {
                'category': 'shipping',
                'question': 'Can I change my delivery address after ordering?',
                'answer': 'If not shipped yet, contact support immediately with new address. We\'ll try to update it. Once shipped, address cannot be changed.',
                'keywords': 'change address, delivery address, shipping address',
                'priority': 7
            },
            {
                'category': 'shipping',
                'question': 'What if the item is damaged on delivery?',
                'answer': 'Don\'t accept the delivery or accept but report damage immediately. Contact support with photos. Initiate return under "Item Damaged" reason.',
                'keywords': 'damaged, broken, damage, defective',
                'priority': 8
            },
            {
                'category': 'shipping',
                'question': 'What if I receive the wrong item?',
                'answer': 'Contact seller and support immediately with order number. We\'ll arrange return of wrong item and send correct one at no extra cost.',
                'keywords': 'wrong item, incorrect item, mistake',
                'priority': 8
            },

            # ========================
            # RETURN & QUALITY
            # ========================
            {
                'category': 'policy',
                'question': 'What is the 30-day return policy?',
                'answer': 'Within 30 days of delivery, return any item in original condition with packaging. Inspect quality first. Return shipping cost varies by item size.',
                'keywords': 'return, 30 days, return policy, money back',
                'priority': 10
            },
            {
                'category': 'policy',
                'question': 'How do I start a return?',
                'answer': 'Go to Orders → select order → click Return. Choose reason (damaged, defective, wrong item, not as described). Provide details and submit.',
                'keywords': 'return, start return, initiate return, return process',
                'priority': 9
            },
            {
                'category': 'policy',
                'question': 'What can I return? What cannot be returned?',
                'answer': 'Can return: Most items unopened/unused. Cannot return: Food, consumables, personal items, used items, items without proper packaging.',
                'keywords': 'non-returnable, not returnable, cannot return, refundable',
                'priority': 8
            },
            {
                'category': 'policy',
                'question': 'How long does return processing take?',
                'answer': 'After seller receives return, they have 3-5 days to inspect. Upon approval, refund issued. Total time: 7-10 days from return date.',
                'keywords': 'return time, processing time, how long',
                'priority': 7
            },
            {
                'category': 'policy',
                'question': 'What about warranty?',
                'answer': 'Warranty depends on product. Electronics typically 12 months. Check product page for details. Warranty covers manufacturing defects only.',
                'keywords': 'warranty, guarantee, manufacturer warranty',
                'priority': 7
            },
            {
                'category': 'policy',
                'question': 'How does quality verification work?',
                'answer': 'All sellers are verified for reliability. Products are checked for accuracy. Our AI reviews customer feedback. Low-rated sellers may be removed.',
                'keywords': 'quality, verified, quality check, seller verification',
                'priority': 6
            },

            # ========================
            # ACCOUNT & SECURITY
            # ========================
            {
                'category': 'account',
                'question': 'How do I update my profile?',
                'answer': 'Go to Profile → Edit Profile. Update name, phone, address, profile picture. Changes take effect immediately.',
                'keywords': 'profile, update profile, edit profile, account',
                'priority': 6
            },
            {
                'category': 'account',
                'question': 'How do I add multiple addresses?',
                'answer': 'In Profile → Addresses, click "Add New Address". You can add unlimited addresses (home, office, etc.) for quick checkout.',
                'keywords': 'address, multiple address, add address',
                'priority': 6
            },
            {
                'category': 'account',
                'question': 'Is my data safe with RootReach?',
                'answer': 'Yes! We use encryption, secure servers, and follow data protection laws. Your data is never shared without permission.',
                'keywords': 'data security, privacy, data protection, safe',
                'priority': 8
            },
            {
                'category': 'account',
                'question': 'How do I enable 2-factor authentication?',
                'answer': 'Go to Account Settings → Security → Enable 2FA. We\'ll send verification code to your phone with each login for extra security.',
                'keywords': '2fa, two-factor, security, verification',
                'priority': 6
            },
            {
                'category': 'account',
                'question': 'Can I delete my account?',
                'answer': 'Yes, but accounts with pending orders cannot be deleted. Complete all orders first, then request deletion from Settings → Account → Delete Account.',
                'keywords': 'delete account, close account, remove account',
                'priority': 5
            },

            # ========================
            # SELLER OPTIMIZATION
            # ========================
            {
                'category': 'seller_guide',
                'question': 'How do I improve product visibility?',
                'answer': 'Use clear titles with keywords, detailed descriptions, high-quality 3-4 photos, correct category, competitive pricing, and regular updates.',
                'keywords': 'visibility, ranking, seo, reach, customers',
                'priority': 7
            },
            {
                'category': 'seller_guide',
                'question': 'What is the best product description?',
                'answer': 'Include: what it is, features, specifications, material, dimensions, color options, ideal for (use cases). Be honest and detailed. Use simple language.',
                'keywords': 'description, product details, write description',
                'priority': 7
            },
            {
                'category': 'seller_guide',
                'question': 'How should I price my products?',
                'answer': 'Research similar products on RootReach. Consider costs, profit margin (20-100% typical), market demand, and competition. Competitive pricing sells faster.',
                'keywords': 'price, pricing, competitive price',
                'priority': 7
            },
            {
                'category': 'seller_guide',
                'question': 'How do I handle difficult customers?',
                'answer': 'Stay professional and friendly. Listen to concerns. Offer solutions (replacement, partial refund, etc.). Document everything. Escalate to support if needed.',
                'keywords': 'customer service, complaint, difficult buyer, conflict',
                'priority': 6
            },
            {
                'category': 'seller_guide',
                'question': 'How often should I update my products?',
                'answer': 'Update prices and stock regularly (weekly). Add seasonal items, refresh photos, update descriptions. Active sellers rank higher! Update at least weekly.',
                'keywords': 'update, product update, refresh, active',
                'priority': 6
            },
            {
                'category': 'seller_guide',
                'question': 'Should I offer discounts?',
                'answer': 'Yes! Strategic discounts boost sales: seasonal (20% off), bulk discounts (5+ units = 10% off), loyalty (repeat buyers = 5% off). Check profitability.',
                'keywords': 'discount, offer, promotional, sale',
                'priority': 6
            },

            # ========================
            # TECHNICAL SUPPORT
            # ========================
            {
                'category': 'support',
                'question': 'Why is my account locked?',
                'answer': 'Account locks after multiple failed login attempts (security measure) or fraud detection. Go to Login → "Unlock Account" or contact support.',
                'keywords': 'locked, unlock, locked account, login issue',
                'priority': 7
            },
            {
                'category': 'support',
                'question': 'Why is my product listing hidden?',
                'answer': 'Product may be hidden if: duplicate listing, policy violation, incomplete info, or admin review. Check email for details. Edit and resubmit.',
                'keywords': 'listing, hidden, inactive, not showing',
                'priority': 7
            },
            {
                'category': 'support',
                'question': 'How do I contact customer support?',
                'answer': 'Contact us through: In-app chat (Orders/Messages), email support text, or phone during business hours. Respond within 24 hours guaranteed.',
                'keywords': 'contact, support, help, customer service',
                'priority': 8
            },
            {
                'category': 'support',
                'question': 'Why did my order fail to place?',
                'answer': 'Could be: payment failed, server error, stock unavailable, or address incomplete. Check email for error. Try again or contact support.',
                'keywords': 'order failed, error, problem, issue',
                'priority': 7
            },
            {
                'category': 'support',
                'question': 'Why can\'t I log in?',
                'answer': 'Check: correct email/password, caps lock off, account not locked. Try password reset. Clear browser cache. If still fails, contact support.',
                'keywords': 'login, password, can\'t login, login problem',
                'priority': 8
            },
        ]
