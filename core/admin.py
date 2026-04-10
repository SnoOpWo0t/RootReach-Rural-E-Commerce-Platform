from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Q, F
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CustomUser, Category, Product, CartItem,
    Order, Review, ChatMessage, SellerApplication, Notification,
    AIKnowledgeBase, AIMessageSuggestion
)
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

# ========================
# CUSTOM USER ADMIN
# ========================
class CustomUserAdmin(DjangoUserAdmin):
    model = CustomUser
    
    list_display = ['username', 'email', 'user_type_badge', 'is_seller_approved', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_seller_approved', 'is_active', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'phone', 'location']
    ordering = ['-date_joined']
    
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('phone', 'location', 'address', 'gender', 'profile_image'),
            'classes': ('wide',)
        }),
        ('Account Type', {
            'fields': ('user_type', 'is_seller_approved'),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    actions = ['approve_sellers', 'reject_sellers', 'deactivate_users', 'activate_users']
    
    def user_type_badge(self, obj):
        colors = {
            'admin': '#e74c3c',
            'seller': '#3498db',
            'buyer': '#2ecc71'
        }
        color = colors.get(obj.user_type, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_user_type_display()
        )
    user_type_badge.short_description = 'User Type'
    
    def approve_sellers(self, request, queryset):
        updated = queryset.filter(user_type='seller').update(is_seller_approved=True)
        self.message_user(request, f'{updated} seller(s) approved')
    approve_sellers.short_description = 'Approve selected sellers'
    
    def reject_sellers(self, request, queryset):
        updated = queryset.filter(user_type='seller').update(is_seller_approved=False)
        self.message_user(request, f'{updated} seller(s) rejected')
    reject_sellers.short_description = 'Reject selected sellers'
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated')
    deactivate_users.short_description = 'Deactivate users'
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated')
    activate_users.short_description = 'Activate users'

# ========================
# CATEGORY ADMIN
# ========================
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count']
    search_fields = ['name']
    ordering = ['name']
    
    def product_count(self, obj):
        count = Product.objects.filter(category=obj).count()
        return format_html(
            '<span style="background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px;">{} products</span>',
            count
        )
    product_count.short_description = 'Products'

# ========================
# PRODUCT ADMIN
# ========================
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['reviewer', 'rating', 'comment', 'created_at']
    can_delete = True
    fields = ['reviewer', 'rating', 'comment', 'created_at']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'category', 'price_display', 'stock_status', 'rating', 'created_at']
    list_filter = ['category', 'created_at', 'stock', 'rating', 'seller']
    search_fields = ['name', 'description', 'seller__username']
    readonly_fields = ['created_at', 'average_rating']
    inlines = [ReviewInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'seller', 'category', 'description'),
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discounted_price', 'stock'),
        }),
        ('Media', {
            'fields': ('image',),
        }),
        ('Location', {
            'fields': ('region',),
        }),
        ('Ratings', {
            'fields': ('rating', 'average_rating'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['restock_products', 'apply_discount']
    
    def price_display(self, obj):
        if obj.discounted_price:
            return format_html(
                '${} <span style="color: #e74c3c; text-decoration: line-through;">${}</span>',
                obj.discounted_price,
                obj.price
            )
        return f'${obj.price}'
    price_display.short_description = 'Price'
    
    def stock_status(self, obj):
        if obj.stock > 10:
            color = '#2ecc71'
            status = 'In Stock'
        elif obj.stock > 0:
            color = '#f39c12'
            status = 'Low Stock'
        else:
            color = '#e74c3c'
            status = 'Out of Stock'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{} ({})</span>',
            color,
            status,
            obj.stock
        )
    stock_status.short_description = 'Stock'
    
    def average_rating(self, obj):
        return f'{obj.rating}/5'
    average_rating.short_description = 'Average Rating'
    
    def restock_products(self, request, queryset):
        updated = queryset.update(stock=50)
        self.message_user(request, f'{updated} product(s) restocked')
    restock_products.short_description = 'Restock (50 units)'
    
    def apply_discount(self, request, queryset):
        queryset.update(discounted_price=F('price') * 0.8)
        self.message_user(request, f'Discount applied to {queryset.count()} product(s) (20 percent off)')
    apply_discount.short_description = 'Apply 20 percent discount'

# ========================
# CART ITEM ADMIN
# ========================
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'total_price']
    list_filter = ['user', 'product__category']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['total_price']
    
    def total_price(self, obj):
        return f'${obj.total_price()}'
    total_price.short_description = 'Total Price'

# ========================
# ORDER ADMIN
# ========================
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'buyer', 'product', 'quantity', 'status_badge', 'payment_status_badge', 'ordered_at']
    list_filter = ['status', 'payment_status', 'ordered_at']
    search_fields = ['buyer__username', 'product__name', 'id']
    readonly_fields = ['id', 'ordered_at', 'total_price_display']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'buyer', 'product', 'quantity'),
        }),
        ('Payment', {
            'fields': ('payment_status', 'total_price_display'),
        }),
        ('Shipping', {
            'fields': ('shipping_address',),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Metadata', {
            'fields': ('ordered_at',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered', 'mark_cancelled', 'mark_paid']
    
    def order_id(self, obj):
        return f'Order #{obj.id}'
    order_id.short_description = 'Order'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#f39c12',
            'confirmed': '#3498db',
            'shipped': '#9b59b6',
            'delivered': '#2ecc71',
            'cancelled': '#e74c3c'
        }
        color = colors.get(obj.status, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        color = '#2ecc71' if obj.payment_status else '#e74c3c'
        text = 'Paid' if obj.payment_status else 'Pending'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    payment_status_badge.short_description = 'Payment'
    
    def total_price_display(self, obj):
        return f'${obj.total_price()}'
    total_price_display.short_description = 'Total Price'
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} order(s) confirmed')
    mark_confirmed.short_description = 'Mark as Confirmed'
    
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) shipped')
    mark_shipped.short_description = 'Mark as Shipped'
    
    def mark_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} order(s) delivered')
    mark_delivered.short_description = 'Mark as Delivered'
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} order(s) cancelled')
    mark_cancelled.short_description = 'Mark as Cancelled'
    
    def mark_paid(self, request, queryset):
        updated = queryset.update(payment_status=True)
        self.message_user(request, f'{updated} order(s) marked as paid')
    mark_paid.short_description = 'Mark as Paid'

# ========================
# REVIEW ADMIN
# ========================
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'reviewer', 'rating_stars', 'is_verified_buyer', 'created_at']
    list_filter = ['rating', 'created_at', 'product__category']
    search_fields = ['product__name', 'reviewer__username', 'comment']
    readonly_fields = ['created_at', 'is_verified_buyer']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'reviewer', 'rating'),
        }),
        ('Content', {
            'fields': ('comment', 'image'),
        }),
        ('Verification', {
            'fields': ('is_verified_buyer',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def rating_stars(self, obj):
        stars = '*' * obj.rating + '-' * (5 - obj.rating)
        return format_html(
            '<span style="color: #f39c12; font-size: 1.2em;">{}</span> ({}/5)',
            stars,
            obj.rating
        )
    rating_stars.short_description = 'Rating'

# ========================
# CHAT MESSAGE ADMIN
# ========================
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['product', 'sender', 'message_preview', 'timestamp']
    list_filter = ['product__category', 'timestamp']
    search_fields = ['product__name', 'message', 'buyer__username', 'seller__username']
    readonly_fields = ['timestamp']
    
    def sender(self, obj):
        return obj.buyer.username if obj.buyer else obj.seller.username
    sender.short_description = 'Sender'
    
    def message_preview(self, obj):
        preview = obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        return preview
    message_preview.short_description = 'Message'

# ========================
# SELLER APPLICATION ADMIN
# ========================
class SellerApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'shop_name', 'approval_status', 'submitted_at']
    list_filter = ['approved', 'submitted_at', 'category']
    search_fields = ['user__username', 'shop_name', 'email']
    readonly_fields = ['submitted_at', 'user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',),
        }),
        ('Shop Details', {
            'fields': ('shop_name', 'shop_address', 'location', 'category', 'shop_image'),
        }),
        ('Contact Information', {
            'fields': ('email',),
        }),
        ('Verification', {
            'fields': ('nid_number', 'tax_id'),
        }),
        ('Application Text', {
            'fields': ('application_text',),
        }),
        ('Approval Status', {
            'fields': ('approved',),
        }),
        ('Metadata', {
            'fields': ('submitted_at',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['approve_applications', 'reject_applications']
    
    def approval_status(self, obj):
        color = '#2ecc71' if obj.approved else '#e74c3c'
        text = 'Approved' if obj.approved else 'Pending'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            text
        )
    approval_status.short_description = 'Status'
    
    def approve_applications(self, request, queryset):
        updated = queryset.update(approved=True)
        # Also approve the sellers
        CustomUser.objects.filter(sellerApplication__in=queryset).update(is_seller_approved=True)
        self.message_user(request, f'{updated} seller application(s) approved')
    approve_applications.short_description = 'Approve selected applications'
    
    def reject_applications(self, request, queryset):
        updated = queryset.update(approved=False)
        # Also reject the sellers
        CustomUser.objects.filter(sellerApplication__in=queryset).update(is_seller_approved=False)
        self.message_user(request, f'{updated} seller application(s) rejected')
    reject_applications.short_description = 'Reject selected applications'


# ========================
# NOTIFICATION ADMIN
# ========================
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marked as read')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marked as unread')
    mark_as_unread.short_description = 'Mark selected notifications as unread'


# ========================
# AI KNOWLEDGE BASE ADMIN
# ========================
class AIKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['question', 'category_badge', 'priority', 'is_active', 'updated_at']
    list_filter = ['category', 'is_active', 'priority', 'updated_at']
    search_fields = ['question', 'answer', 'keywords']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Knowledge Content', {
            'fields': ('category', 'question', 'answer'),
        }),
        ('Optimization', {
            'fields': ('keywords', 'priority'),
            'description': 'Keywords help AI find relevant answers (comma-separated)',
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['activate_items', 'deactivate_items', 'increase_priority', 'decrease_priority']
    
    def category_badge(self, obj):
        colors = {
            'faq': '#3498db',
            'policy': '#e74c3c',
            'product': '#2ecc71',
            'shipping': '#f39c12',
            'payment': '#9b59b6',
            'seller': '#1abc9c',
            'account': '#34495e',
            'general': '#95a5a6',
        }
        color = colors.get(obj.category, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def activate_items(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} item(s) activated')
    activate_items.short_description = 'Activate selected items'
    
    def deactivate_items(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} item(s) deactivated')
    deactivate_items.short_description = 'Deactivate selected items'
    
    def increase_priority(self, request, queryset):
        for item in queryset:
            item.priority += 1
            item.save()
        self.message_user(request, f'{queryset.count()} item(s) priority increased')
    increase_priority.short_description = 'Increase priority'
    
    def decrease_priority(self, request, queryset):
        for item in queryset:
            item.priority = max(0, item.priority - 1)
            item.save()
        self.message_user(request, f'{queryset.count()} item(s) priority decreased')
    decrease_priority.short_description = 'Decrease priority'


# ========================
# AI MESSAGE SUGGESTION ADMIN
# ========================
class AIMessageSuggestionAdmin(admin.ModelAdmin):
    list_display = ['suggestion_type', 'product', 'is_active', 'usage_count', 'created_at']
    list_filter = ['suggestion_type', 'is_active', 'created_at']
    search_fields = ['message_template', 'product__name']
    readonly_fields = ['created_at', 'usage_count']
    
    fieldsets = (
        ('Suggestion Details', {
            'fields': ('suggestion_type', 'product'),
        }),
        ('Templates', {
            'fields': ('message_template', 'response_suggestions'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Analytics', {
            'fields': ('usage_count', 'created_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['activate_suggestions', 'deactivate_suggestions', 'reset_usage_count']
    
    def activate_suggestions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} suggestion(s) activated')
    activate_suggestions.short_description = 'Activate suggestions'
    
    def deactivate_suggestions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} suggestion(s) deactivated')
    deactivate_suggestions.short_description = 'Deactivate suggestions'
    
    def reset_usage_count(self, request, queryset):
        queryset.update(usage_count=0)
        self.message_user(request, 'Usage counts reset')
    reset_usage_count.short_description = 'Reset usage count'


# ========================
# ADMIN SITE CUSTOMIZATION
# ========================
admin.site.site_header = 'RootReach Admin Dashboard'
admin.site.site_title = 'RootReach Admin'
admin.site.index_title = 'Welcome to RootReach Administration Panel'

# ========================
# REGISTER MODELS
# ========================
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(SellerApplication, SellerApplicationAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(AIKnowledgeBase, AIKnowledgeBaseAdmin)
admin.site.register(AIMessageSuggestion, AIMessageSuggestionAdmin)
