# Generated migration for AI models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIKnowledgeBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('faq', 'FAQ'), ('policy', 'Policy'), ('product', 'Product'), ('shipping', 'Shipping'), ('payment', 'Payment'), ('seller', 'Seller Info'), ('account', 'Account'), ('general', 'General')], max_length=20)),
                ('question', models.CharField(max_length=500)),
                ('answer', models.TextField()),
                ('keywords', models.CharField(help_text='Comma-separated keywords for matching', max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('priority', models.IntegerField(default=0, help_text='Higher priority shown first')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-priority', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIMessageSuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggestion_type', models.CharField(choices=[('greeting', 'Greeting'), ('product_inquiry', 'Product Inquiry'), ('price_negotiation', 'Price Negotiation'), ('shipping_question', 'Shipping Question'), ('complaint', 'Complaint'), ('order_status', 'Order Status'), ('general', 'General')], max_length=50)),
                ('message_template', models.TextField()),
                ('response_suggestions', models.TextField(help_text='JSON array of suggested responses')),
                ('is_active', models.BooleanField(default=True)),
                ('usage_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ai_suggestions', to='core.product')),
            ],
        ),
    ]
