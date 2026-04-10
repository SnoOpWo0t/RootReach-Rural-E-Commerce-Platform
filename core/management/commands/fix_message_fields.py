"""
Management command to fix corrupted ChatMessage sender fields.

Issue: The old seller_messages view was setting seller field on buyer's messages,
which corrupts the sender identification logic used throughout the app.

Fix: For each (buyer, product) conversation, the first (earliest) message 
should have seller=None (it's the buyer's initial message).
"""

from django.core.management.base import BaseCommand
from django.db.models import Min
from core.models import ChatMessage


class Command(BaseCommand):
    help = 'Fix corrupted ChatMessage sender fields (first message in each conversation should have seller=None)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting fix for corrupted ChatMessage fields...'))
        
        # Get all unique (buyer, product) combinations
        conversations = ChatMessage.objects.filter(
            buyer__isnull=False
        ).values('buyer', 'product').distinct()
        
        total_fixed = 0
        
        for conv in conversations:
            buyer_id = conv['buyer']
            product_id = conv['product']
            
            # Get all messages in this conversation
            messages = ChatMessage.objects.filter(
                buyer_id=buyer_id,
                product_id=product_id
            ).order_by('timestamp')
            
            if not messages.exists():
                continue
            
            # The FIRST message in each conversation should be the buyer's initial message
            # So it should have seller=None
            first_message = messages.first()
            
            if first_message.seller is not None:
                self.stdout.write(
                    f'Fixing: Buyer {buyer_id}, Product {product_id}, '
                    f'Message ID {first_message.id} - Clearing seller field'
                )
                first_message.seller = None
                first_message.save()
                total_fixed += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Fixed {total_fixed} corrupted messages!')
        )
