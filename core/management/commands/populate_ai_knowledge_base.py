"""Management command to populate AI knowledge base with FAQ and policies"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import AIKnowledgeBase
import json


class Command(BaseCommand):
    help = 'Populate AI knowledge base with FAQs, policies, and helpful information'

    def handle(self, *args, **options):
        """Populate knowledge base"""
        
        # Clear existing knowledge base if requested
        if AIKnowledgeBase.objects.exists():
            self.stdout.write(self.style.WARNING('Knowledge base already exists. Skipping population.'))
            return
        
        knowledge_items = [
            # FAQs
            {
                'category': 'faq',
                'question': 'What is RootReach?',
                'answer': 'RootReach is an e-commerce marketplace that connects buyers and sellers. We provide a platform for buying and selling products with secure payments, reliable shipping, and buyer protection.',
                'keywords': 'what is rootreach, platform, marketplace',
                'priority': 10
            },
            {
                'category': 'faq',
                'question': 'How do I create an account?',
                'answer': 'Click "Sign Up" or "Register" on the homepage. Fill in your email, create a password, and complete your profile. You\'ll be able to start shopping immediately!',
                'keywords': 'register, signup, account, create account',
                'priority': 9
            },
            {
                'category': 'faq',
                'question': 'How do I become a seller?',
                'answer': 'Go to "Sell Zone" and click "Apply to Sell". Fill out the seller application with your shop details, business information, and verification documents. Our team will review and approve your application within 2-3 business days.',
                'keywords': 'seller, become seller, apply seller, how to sell',
                'priority': 9
            },
            {
                'category': 'faq',
                'question': 'How can I track my order?',
                'answer': 'Once you place an order, you can track it from your "Orders" page. You\'ll see the current status (pending, confirmed, shipped, or delivered) and estimated delivery date.',
                'keywords': 'order tracking, track order, where is my order',
                'priority': 8
            },
            
            # Payment
            {
                'category': 'payment',
                'question': 'What payment methods do you accept?',
                'answer': 'We accept multiple payment methods including credit cards, debit cards, mobile banking, and online payment gateways for your convenience and security.',
                'keywords': 'payment, pay, payment method, credit card, debit',
                'priority': 8
            },
            {
                'category': 'payment',
                'question': 'Is my payment secure?',
                'answer': 'Yes! All payments are encrypted and processed through secure payment gateways. Your financial information is protected with the latest security standards.',
                'keywords': 'secure, safety, encryption, payment secure',
                'priority': 7
            },
            
            # Shipping
            {
                'category': 'shipping',
                'question': 'How long does delivery take?',
                'answer': 'Delivery typically takes 3-7 business days depending on your location. Express shipping options may be available for an additional fee.',
                'keywords': 'shipping, delivery, how long, days',
                'priority': 8
            },
            {
                'category': 'shipping',
                'question': 'Do you offer free shipping?',
                'answer': 'Free shipping is often available on orders above certain amounts. Check the specific product page or your cart to see shipping costs before checkout.',
                'keywords': 'free shipping, shipping cost, shipping fee',
                'priority': 7
            },
            {
                'category': 'shipping',
                'question': 'Can I change my delivery address after placing an order?',
                'answer': 'Yes, if your order hasn\'t been shipped yet. Contact our support team immediately through the order details page to change your address.',
                'keywords': 'change address, delivery address, shipping address',
                'priority': 6
            },
            
            # Returns & Refunds
            {
                'category': 'policy',
                'question': 'What is your return policy?',
                'answer': 'We offer a 30-day return guarantee. If you\'re not satisfied with your purchase, you can initiate a return within 30 days of delivery. The product must be in original condition.',
                'keywords': 'return, refund, money back, 30 days',
                'priority': 10
            },
            {
                'category': 'policy',
                'question': 'How do I process a return?',
                'answer': 'Go to your Orders page, find the product, and click "Return". Follow the return process, arrange pickup with our logistics partner, and your refund will be processed within 3-5 business days of receipt.',
                'keywords': 'return process, how to return, return steps',
                'priority': 8
            },
            
            # Account & Security
            {
                'category': 'account',
                'question': 'How do I update my profile?',
                'answer': 'Click on your profile icon and select "Edit Profile". You can update your personal information, profile picture, address, and contact details.',
                'keywords': 'profile, update, edit, settings',
                'priority': 6
            },
            {
                'category': 'account',
                'question': 'How do I reset my password?',
                'answer': 'Click "Forgot Password" on the login page. Enter your email and follow the instructions to reset your password. You\'ll receive a reset link in your email.',
                'keywords': 'password, forgot password, reset',
                'priority': 7
            },
            {
                'category': 'account',
                'question': 'How do I delete my account?',
                'answer': 'You can request account deletion from your account settings. Once deleted, your data cannot be recovered. Contact support if you have any questions.',
                'keywords': 'delete account, close account, remove account',
                'priority': 5
            },
            
            # Product Information
            {
                'category': 'product',
                'question': 'How do I search for products?',
                'answer': 'Use the search bar at the top of the page or browse by category. You can filter results by price, region, availability, and sort by various criteria.',
                'keywords': 'search, find product, product search',
                'priority': 7
            },
            {
                'category': 'product',
                'question': 'Can I compare products?',
                'answer': 'Yes! Add products to the comparison list and you\'ll be able to see side-by-side comparison of features, prices, and specifications.',
                'keywords': 'compare, product comparison',
                'priority': 6
            },
            {
                'category': 'product',
                'question': 'How do I leave a review?',
                'answer': 'After receiving your order, go to your Orders page and click "Leave Review" on the product. Rate the product and share your feedback to help other buyers.',
                'keywords': 'review, rating, feedback, rate product',
                'priority': 6
            },
            
            # Seller Info
            {
                'category': 'seller',
                'question': 'What do I need to become a seller?',
                'answer': 'You need an active account, valid business information, NID/tax ID, and a shop photo. Submit via the seller application and we\'ll verify your details.',
                'keywords': 'seller requirements, become seller, seller verification',
                'priority': 8
            },
            {
                'category': 'seller',
                'question': 'How do I manage my products as a seller?',
                'answer': 'Go to "Sell Zone" and use "Manage Products" to add, edit, or delete products. You can also track inventory, set prices, and manage discounts.',
                'keywords': 'manage products, seller dashboard, add product',
                'priority': 7
            },
            {
                'category': 'seller',
                'question': 'How do I respond to buyer messages?',
                'answer': 'Visit "Seller Messages" in your Sell Zone to see all buyer inquiries. Click on a message to respond directly to the buyer.',
                'keywords': 'messages, buyer messages, seller messages',
                'priority': 7
            },
            
            # General
            {
                'category': 'general',
                'question': 'Is there a customer service team available?',
                'answer': 'Yes! Our support team is available 24/7 through the contact form on each product page or order. We typically respond within 24 hours.',
                'keywords': 'support, help, customer service, contact',
                'priority': 8
            },
            {
                'category': 'general',
                'question': 'What should I do if I have an issue with my order?',
                'answer': 'Contact the seller directly through the product messaging system first. If the issue isn\'t resolved, contact our support team for assistance.',
                'keywords': 'issue, problem, complaint, help',
                'priority': 8
            },
        ]
        
        created_count = 0
        for item in knowledge_items:
            kb, created = AIKnowledgeBase.objects.get_or_create(
                question=item['question'],
                defaults={
                    'category': item['category'],
                    'answer': item['answer'],
                    'keywords': item['keywords'],
                    'priority': item['priority'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {item["question"][:50]}...'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully created {created_count} knowledge base entries!'))
        self.stdout.write(self.style.SUCCESS('AI Knowledge Base is now populated and ready to use.'))
