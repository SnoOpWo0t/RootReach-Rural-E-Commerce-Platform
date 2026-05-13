from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg, F
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime
import json

from .forms import CustomUserRegistrationForm, ProfileUpdateForm, SellerApplicationForm, ProductForm, CategoryForm, ReviewForm, ChatMessageForm
from .models import CustomUser, SellerApplication, Order, ORDER_STATUS, Product, Category, CartItem, Review, ChatMessage, Notification
from .ai_assistant import get_shopping_assistant_result
from .huggingface_chatbot import chat_with_huggingface, validate_message, fallback_response

def home(request):
    query = request.GET.get('q', '').strip()
    region = request.GET.get('region', '').strip()
    stock = request.GET.get('stock', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    sort = request.GET.get('sort', '')
    category_id = request.GET.get('category', '')

    # Step 1: Start from the base QuerySet
    base_products = Product.objects.select_related('category', 'seller').prefetch_related('reviews')

    # Step 2: Apply filters
    if query:
        base_products = base_products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if region:
        base_products = base_products.filter(region__icontains=region)

    if stock == "in":
        base_products = base_products.filter(stock__gt=0)
    elif stock == "out":
        base_products = base_products.filter(stock__lte=0)

    if category_id:
        base_products = base_products.filter(category_id=category_id)

    try:
        if min_price:
            base_products = base_products.filter(price__gte=Decimal(min_price))
        if max_price:
            base_products = base_products.filter(price__lte=Decimal(max_price))
    except (ValueError, InvalidOperation):
        pass

    if sort == "asc":
        base_products = base_products.order_by('price')
    elif sort == "desc":
        base_products = base_products.order_by('-price')

    # Step 3: Limit results and apply annotation only at the end
    products = base_products.annotate(avg_rating=Avg('reviews__rating'))[:100]

    # Step 4: Top categories
    categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:5]

    # AI Recommendation Section: Recommended for You
    # Products with highest ratings that user hasn't viewed
    recommended_products = Product.objects.select_related('category', 'seller') \
        .prefetch_related('reviews') \
        .annotate(avg_rating=Avg('reviews__rating')) \
        .filter(stock__gt=0, avg_rating__gte=3) \
        .order_by('-avg_rating', '-created_at')[:6]

    # AI Recommendation Section: Trending in Your Area
    # Get user's region/division - from their profile or query parameter
    user_division = None
    if request.user.is_authenticated and request.user.division:
        user_division = request.user.division
    else:
        user_division = request.GET.get('division', None)
    
    # Trending = Recent products with good ratings and multiple orders from the user's region
    # Count orders as a popularity metric
    from django.db.models import Count as DjangoCount
    
    trending_products = Product.objects.select_related('category', 'seller') \
        .prefetch_related('reviews') \
        .annotate(
            avg_rating=Avg('reviews__rating'),
            order_count=DjangoCount('order', distinct=True),  # How many times ordered
            review_count=DjangoCount('reviews', distinct=True)  # How many reviews
        ) \
        .filter(stock__gt=0) \
        .order_by('-order_count', '-avg_rating', '-created_at')[:6]  # By popularity first, then rating
    
    # If user has a division, prioritize products from that division
    if user_division:
        region_trending = Product.objects.select_related('category', 'seller') \
            .prefetch_related('reviews', 'order_set') \
            .annotate(
                avg_rating=Avg('reviews__rating'),
                order_count=DjangoCount('order', distinct=True),
                review_count=DjangoCount('reviews', distinct=True)
            ) \
            .filter(stock__gt=0, region__icontains=user_division) \
            .order_by('-order_count', '-avg_rating', '-created_at')[:6]
        
        if region_trending.exists():
            trending_products = region_trending

    # AI Recommendation Section: Popular Rural Products
    # Products categorized or described as rural/local with good engagement
    # Enhanced: Check for rural keywords AND solid ratings/orders
    rural_keywords = ['organic', 'handmade', 'rural', 'local', 'artisan', 'natural', 'eco', 'traditional', 'homemade', 'cottage']
    rural_query = Q()
    for keyword in rural_keywords:
        rural_query |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
    
    # Rural products = keyword matches + high engagement (orders, reviews, ratings)
    rural_products = Product.objects.select_related('category', 'seller') \
        .prefetch_related('reviews', 'order_set') \
        .annotate(
            avg_rating=Avg('reviews__rating'),
            order_count=DjangoCount('order', distinct=True),
            review_count=DjangoCount('reviews', distinct=True),
            engagement_score=DjangoCount('order', distinct=True) + DjangoCount('reviews', distinct=True)  # Total engagement
        ) \
        .filter(rural_query, stock__gt=0) \
        .order_by('-engagement_score', '-avg_rating', '-order_count', '-created_at')[:6]

    # If not enough rural products, fill with high-engagement popular ones
    if rural_products.count() < 6:
        more_rural = Product.objects.select_related('category', 'seller') \
            .prefetch_related('reviews', 'order_set') \
            .annotate(
                avg_rating=Avg('reviews__rating'),
                order_count=DjangoCount('order', distinct=True),
                engagement_score=DjangoCount('order', distinct=True) + DjangoCount('reviews', distinct=True)
            ) \
            .filter(stock__gt=0, avg_rating__gte=3.5, engagement_score__gt=0) \
            .exclude(id__in=rural_products.values_list('id', flat=True)) \
            .order_by('-engagement_score', '-avg_rating')[:6 - rural_products.count()]
        rural_products = list(rural_products) + list(more_rural)

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'recommended_products': recommended_products,
        'trending_products': trending_products,
        'rural_products': rural_products,
    })


from django.contrib.auth import login  # 👈 import login

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'buyer'  # Default
            user.save()

            login(request, user)  # 👈 Auto-login after saving the user

            messages.success(request, 'Account created successfully. You are now logged in.')
            return redirect('home')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url or 'home')
        else:
            messages.error(request, 'Invalid credentials.')
    if next_url and request.method != 'POST':
        messages.info(request, 'Please log in or sign up to continue.')
    return render(request, 'login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('login')


from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ProfileUpdateForm

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')  # ← redirects to homepage
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'profile.html', {'form': form})


@login_required
def apply_seller(request):
    if SellerApplication.objects.filter(user=request.user).exists():
        messages.info(request, "You already applied.")
        return redirect('profile')

    if request.method == 'POST':
        form = SellerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, "Application submitted for review.")
            return redirect('home')
    else:
        form = SellerApplicationForm()
    return render(request, 'apply_seller.html', {'form': form})


# Admin view to approve sellers (dashboard will come later)
from django.contrib.admin.views.decorators import staff_member_required
from .models import SellerApplication, CustomUser
@staff_member_required
def seller_requests(request):
    requests = SellerApplication.objects.filter(approved=False)
    return render(request, 'seller_requests.html', {'requests': requests})

@staff_member_required
def approve_seller(request, pk):
    application = SellerApplication.objects.get(pk=pk)
    user = application.user

    # ✅ Correctly set user to seller
    user.user_type = 'seller'
    user.is_seller_approved = True
    user.save()

    # ✅ Mark the application as approved
    application.approved = True
    application.save()

    return redirect('seller_requests')

@staff_member_required
def reject_seller(request, pk):
    application = SellerApplication.objects.get(pk=pk)
    application.delete()
    return redirect('seller_requests')

from .forms import ProductForm
from .models import Product, Order, Review
from django.contrib import messages

@login_required
def sell_zone(request):
    """Comprehensive seller dashboard with all necessary information"""
    if not request.user.is_authenticated or not request.user.is_seller():
        return redirect('home')

    # Get Products
    products = Product.objects.filter(seller=request.user)
    total_products = products.count()
    out_of_stock_products = products.filter(stock=0).count()
    
    # Get Orders
    orders = Order.objects.filter(product__seller=request.user).select_related('product', 'buyer')
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    confirmed_orders = orders.filter(status='confirmed').count()
    shipped_orders = orders.filter(status='shipped').count()
    delivered_orders = orders.filter(status='delivered').count()
    
    # Get Reviews
    reviews = Review.objects.filter(product__seller=request.user).select_related('product', 'reviewer')
    total_reviews = reviews.count()
    avg_rating = products.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Revenue Calculation (simplified - assuming we have total_price or can calculate from orders)
    total_revenue = 0
    for order in orders.filter(status='delivered'):
        if order.total_price():
            total_revenue += order.total_price()
    
    # Get Messages
    messages_obj = ChatMessage.objects.filter(product__seller=request.user).select_related('product', 'buyer').order_by('-timestamp')
    # Only show messages FROM buyers (exclude seller replies)
    recent_messages = messages_obj.filter(buyer__isnull=False)[:5]
    # Count only unread messages (where seller hasn't opened them yet and from buyers)
    unread_messages = ChatMessage.objects.filter(product__seller=request.user, seller__isnull=True, buyer__isnull=False)
    total_messages = messages_obj.filter(buyer__isnull=False).count()
    new_messages_count = unread_messages.count()
    
    # Recent Activity
    recent_orders = orders.order_by('-ordered_at')[:5]
    recent_products = products.order_by('-created_at')[:5]
    recent_reviews = reviews.order_by('-created_at')[:5]
    
    context = {
        'products': products,
        'total_products': total_products,
        'out_of_stock_products': out_of_stock_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_reviews': recent_reviews,
        'recent_messages': recent_messages,
        'total_messages': total_messages,
        'new_messages_count': new_messages_count,
    }
    
    return render(request, 'sell_zone.html', context)

@login_required
def add_product(request):
    if not request.user.is_seller():
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect('sell_zone')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})

@login_required
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id, seller=request.user)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect('sell_zone')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Order

@login_required
def seller_orders(request):
    if not request.user.is_seller():
        return redirect('home')

    status_filter = request.GET.get('status')  # 'pending', 'confirmed', etc.

    orders = Order.objects.filter(product__seller=request.user).order_by('-ordered_at')

    if status_filter in ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']:
        orders = orders.filter(status=status_filter)

    return render(request, 'seller_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
    })



@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, product__seller=request.user)
    order.status = 'cancelled'
    order.save()
    
    # Create notification for buyer
    Notification.objects.create(
        user=order.buyer,
        notification_type='order_cancelled',
        title='Order Cancelled',
        message=f'Your order #{order.id} for {order.product.name} has been cancelled by the seller.',
        order=order,
        product=order.product,
        link=f'/orders/'
    )
    
    messages.success(request, f"Order #{order.id} cancelled.")
    return redirect('seller_orders')

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, CustomUser, ORDER_STATUS


def update_order_status(request, order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id, product__seller=user)

    if not user.is_seller():
        return JsonResponse({'success': False, 'message': "Unauthorized seller"}, status=403)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ORDER_STATUS):
            order.status = new_status
            order.save()
            
            # Create notification for buyer based on status
            if new_status == 'delivered':
                Notification.objects.create(
                    user=order.buyer,
                    notification_type='order_delivered',
                    title='Order Delivered',
                    message=f'Your order #{order.id} for {order.product.name} has been delivered!',
                    order=order,
                    product=order.product,
                    link=f'/orders/'
                )
                # Also create a review request notification
                Notification.objects.create(
                    user=order.buyer,
                    notification_type='review_request',
                    title='Please Review Your Purchase',
                    message=f'We\'d love to hear your feedback about {order.product.name}. Please leave a review!',
                    order=order,
                    product=order.product,
                    link=f'/product/{order.product.id}/review/'
                )
            elif new_status == 'cancelled':
                Notification.objects.create(
                    user=order.buyer,
                    notification_type='order_cancelled',
                    title='Order Cancelled',
                    message=f'Your order #{order.id} for {order.product.name} has been cancelled.',
                    order=order,
                    product=order.product,
                    link=f'/orders/'
                )
            else:
                Notification.objects.create(
                    user=order.buyer,
                    notification_type='order_status_changed',
                    title='Order Status Updated',
                    message=f'Your order #{order.id} status has been updated to {new_status}.',
                    order=order,
                    product=order.product,
                    link=f'/orders/'
                )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'status': new_status,
                    'message': f"Order #{order.id} status updated to {new_status}."
                })

            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")
        return redirect('seller_orders')


from .models import Product, CartItem, Order, Review, ChatMessage
from .forms import ReviewForm, ChatMessageForm

from django.shortcuts import redirect, get_object_or_404
from .models import Product, CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # ❌ Prevent users from adding their own product
    if request.user == product.seller:
        messages.warning(request, "You cannot add your own product to the cart.")
        return redirect('product_detail', pk=product_id)

    # ❌ Prevent adding out-of-stock products
    if product.stock <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect('product_detail', pk=product_id)

    # ✅ Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, "You've reached the maximum available stock.")
            return redirect('cart')
    else:
        cart_item.quantity = 1
        cart_item.save()

    # ✅ Optionally reduce stock at time of adding to cart (not typical — usually at checkout)
    # product.stock -= 1
    # product.save()

    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def update_cart(request, item_id):
    item = CartItem.objects.get(id=item_id, user=request.user)
    if request.method == 'POST':
        item.quantity = int(request.POST.get('quantity'))
        item.save()
    return redirect('cart')

@login_required
def remove_cart_item(request, item_id):
    CartItem.objects.get(id=item_id, user=request.user).delete()
    return redirect('cart')


@login_required
def place_order(request):
    cart_items = CartItem.objects.select_related('product').filter(user=request.user)
    subtotal = sum(item.total_price() for item in cart_items)
    shipping_cost = 60
    total = subtotal + shipping_cost

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        # Get shipping details
        shipping_address = f"""
Name: {request.POST.get('full_name')}
Phone: {request.POST.get('phone')}
Email: {request.POST.get('email')}
Address: {request.POST.get('shipping_address')}
Payment Method: {request.POST.get('payment_method', 'Not specified')}
"""
        # Check stock availability
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(
                    request,
                    f"Not enough stock for '{item.product.name}'. Only {item.product.stock} left in stock."
                )
                return redirect('cart')

        # Create orders and update stock
        for item in cart_items:
            order = Order.objects.create(
                buyer=request.user,
                product=item.product,
                quantity=item.quantity,
                shipping_address=shipping_address,
                status='pending',
                payment_status=False
            )
            # ✅ NEW: Notify seller about new order
            Notification.objects.create(
                user=item.product.seller,
                notification_type='order_status_changed',
                title='New Order Received',
                message=f'{request.user.first_name or request.user.username} ordered {item.quantity}x {item.product.name}',
                order=order,
                product=item.product,
                link=f'/sell-zone/orders/'
            )
            # ✅ NEW: Notify buyer their order is confirmed
            Notification.objects.create(
                user=request.user,
                notification_type='order_status_changed',
                title='Order Confirmed',
                message=f'Your order for {item.product.name} has been received and is pending seller confirmation.',
                order=order,
                product=item.product,
                link=f'/orders/'
            )
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart and redirect
        cart_items.delete()
        messages.success(request, "Order placed successfully! Track your order status in the Orders page.")
        return redirect('order_tracking')

    return render(request, 'place_order.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total
    })


@login_required
def order_tracking(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'order_tracking.html', {'orders': orders})

from django.shortcuts import render, get_object_or_404
from .models import Product
from .forms import ReviewForm

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.all().order_by('-created_at')
    review_form = ReviewForm()
    
    # Calculate accurate rating distribution by counting reviews at each rating level
    rating_counts = {}
    for rating in range(5, 0, -1):  # 5, 4, 3, 2, 1
        rating_counts[rating] = reviews.filter(rating=rating).count()
    
    # Get max count to calculate bar widths as percentages
    max_count = max(rating_counts.values()) if rating_counts.values() else 1
    
    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'rating_counts': rating_counts,
        'max_count': max_count,
        'rating_choices': [5, 4, 3, 2, 1]
    })

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Review
from .forms import ReviewForm

@login_required
def submit_review(request, pk):
    product = get_object_or_404(Product, id=pk)

    # ✅ Only allow review if buyer purchased the product
    if not Order.objects.filter(buyer=request.user, product=product).exists():
        return redirect('product_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)

        # 🔥 Extract rating from hidden input (JS-powered)
        rating = request.POST.get('rating')

        # ✅ Validate rating is 1–5
        if form.is_valid() and rating in ['1', '2', '3', '4', '5']:
            review = form.save(commit=False)
            review.reviewer = request.user
            review.product = product
            review.rating = int(rating)  # ← set manually from hidden input
            review.save()
            
            # ✅ NEW: Notify seller about new review
            Notification.objects.create(
                user=product.seller,
                notification_type='review_request',
                title='New Review Posted',
                message=f'{request.user.first_name or request.user.username} left a {rating}-star review on {product.name}',
                product=product,
                link=f'/product/{pk}/'
            )

    return redirect('product_detail', pk=pk)




from django.http import HttpResponse
from django.db.models import Q
from .models import ChatMessage, Product
from .forms import ChatMessageForm

@login_required
def product_chat(request, pk):
    product = get_object_or_404(Product, id=pk)
    form = ChatMessageForm(request.POST or None)

    # Get buyer ID from URL parameters or determine it
    buyer_id = request.GET.get('buyer_id')
    
    # Determine who the other user is (ensure consistent pairing)
    if request.user == product.seller:
        # If buyer_id is provided, use it
        if buyer_id:
            try:
                buyer_user = CustomUser.objects.get(id=buyer_id)
            except CustomUser.DoesNotExist:
                buyer_user = None
        else:
            # Otherwise get the most recent buyer for this product
            buyer = ChatMessage.objects.filter(product=product).exclude(buyer=None).order_by('-timestamp').first()
            buyer_user = buyer.buyer if buyer else None
    else:
        buyer_user = request.user

    if form.is_valid():
        msg = form.save(commit=False)
        msg.product = product

        # Prevent contact info sharing
        if any(word in msg.message.lower() for word in ['phone', 'email', '@', 'contact']):
            return HttpResponse("Sharing contact info is not allowed.")

        if request.user == product.seller:
            # Seller is replying to a buyer - include buyer so they see the message
            msg.seller = request.user
            msg.buyer = buyer_user  # Set buyer so message is visible to them
            
            # Create notification for buyer only if buyer_user exists
            if buyer_user:
                Notification.objects.create(
                    user=buyer_user,
                    notification_type='seller_reply',
                    title='Seller Reply',
                    message=f'The seller of {product.name} has replied to your message!',
                    product=product,
                    link=f'/orders/messages/'
                )
        else:
            # Buyer is sending a message to seller
            msg.buyer = request.user
            msg.seller = None  # Leave seller as None until seller reads it

        msg.save()
        
        # ✅ NEW: Notify seller when buyer sends initial message
        if request.user != product.seller:  # Only notify if buyer is not seller
            Notification.objects.create(
                user=product.seller,
                notification_type='seller_reply',
                title='New Buyer Message',
                message=f'{request.user.first_name or request.user.username} sent you a message about {product.name}',
                product=product,
                link=f'/product/{pk}/chat/?buyer_id={request.user.id}'
            )
        
        return redirect('product_chat', pk=pk)

    # Show messages related to this product between this seller and buyer
    if request.user == product.seller and buyer_user:
        # Seller viewing: show messages between this specific buyer and seller
        messages = ChatMessage.objects.filter(
            product=product,
            buyer=buyer_user
        ).order_by("timestamp")
    else:
        # Buyer viewing: show only messages where BUYER is the initiating user
        # IMPORTANT: Do NOT include messages where seller=request.user (buyer should never be in seller field)
        messages = ChatMessage.objects.filter(
            product=product,
            buyer=request.user
        ).order_by("timestamp")

    # Add display information for each message
    seller_name = f"{product.seller.first_name} {product.seller.last_name}".strip() or product.seller.username
    
    messages_list = []
    for msg in messages:
        # EXPLICIT: Determine WHO sent this message based on ChatMessage fields
        # msg.buyer = always present (the initiating buyer in conversation)
        # msg.seller = set ONLY when seller replies
        # 
        # Message is from SELLER only if seller field is explicitly set
        is_from_seller = (msg.seller is not None and msg.seller is not False)
        
        # Determine if THIS message should appear on LEFT (receiver) or RIGHT (sender) for current viewer
        is_from_current_user = False
        if request.user == product.seller:
            # SELLER viewing: show on RIGHT if SELLER sent it
            is_from_current_user = (msg.seller == request.user)
        else:
            # BUYER viewing: show on RIGHT if BUYER sent it (seller field is None/not set)
            is_from_current_user = (msg.seller is None or msg.seller is False)
        
        # Determine WHO to show as sender (for label/name display)
        if is_from_seller:
            # SELLER sent this - show "You" if viewer is seller, else show seller name
            if request.user == product.seller:
                display_sender_name = "You"
            else:
                display_sender_name = seller_name
        else:
            # BUYER sent this - show "You" if viewer is buyer, else show buyer name
            if request.user == msg.buyer:
                display_sender_name = "You"
            else:
                display_sender_name = (msg.buyer.first_name or msg.buyer.username)
        
        msg_data = {
            'message': msg,
            'is_from_seller': is_from_seller,
            'is_from_current_user': is_from_current_user,
            'sender_name': display_sender_name
        }
        messages_list.append(msg_data)

    return render(request, 'product_chat.html', {
        'product': product,
        'form': form,
        'messages': messages_list,
        'buyer_user': buyer_user,
        'seller_name': seller_name,
        'user': request.user
    })


from decimal import Decimal, InvalidOperation

def search_products(request):
    products = Product.objects.all()

    query = request.GET.get('q', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    region = request.GET.get('region', '')
    stock = request.GET.get('stock', '')
    sort = request.GET.get('sort', '')

    # Search filter
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    # Price filter (safely parse to decimal)
    try:
        if min_price:
            products = products.filter(price__gte=Decimal(min_price))
        if max_price:
            products = products.filter(price__lte=Decimal(max_price))
    except InvalidOperation:
        pass  # Invalid input skipped silently (you could flash an error message instead)

    # Region filter
    if region:
        products = products.filter(region__icontains=region)

    # Stock filter
    if stock == 'in':
        products = products.filter(stock__gt=0)
    elif stock == 'out':
        products = products.filter(stock=0)

    # Sort
    if sort == 'low':
        products = products.order_by('price')
    elif sort == 'high':
        products = products.order_by('-price')

    # Pagination: 50 products per page
    from django.core.paginator import Paginator
    from urllib.parse import urlencode
    
    paginator = Paginator(products, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build clean query string without page parameter for pagination links
    query_params = {}
    if query:
        query_params['q'] = query
    if min_price:
        query_params['min'] = min_price
    if max_price:
        query_params['max'] = max_price
    if region:
        query_params['region'] = region
    if stock:
        query_params['stock'] = stock
    if sort:
        query_params['sort'] = sort
    
    query_string = urlencode(query_params) if query_params else ''

    return render(request, 'search.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'region': region,
        'stock': stock,
        'sort': sort,
        'query_string': query_string,
    })

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from .forms import ProductForm, CategoryForm

@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('sell_zone')
    else:
        form = ProductForm(instance=product)
    return render(request, 'update_product.html', {'form': form})

@login_required
def seller_manage_products(request):
    """View to manage all seller products"""
    if not request.user.is_authenticated or not request.user.is_seller():
        return redirect('home')
    
    # Get all products for current seller
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    # Search/filter functionality
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    stock_filter = request.GET.get('stock', '').strip()
    
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if stock_filter == 'out':
        products = products.filter(stock=0)
    elif stock_filter == 'low':
        products = products.filter(stock__gt=0, stock__lt=10)
    elif stock_filter == 'in':
        products = products.filter(stock__gte=10)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'search_query': search_query,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'categories': categories,
        'total_products': Product.objects.filter(seller=request.user).count(),
        'out_of_stock_count': Product.objects.filter(seller=request.user, stock=0).count(),
        'low_stock_count': Product.objects.filter(seller=request.user, stock__gt=0, stock__lt=10).count(),
    }
    
    return render(request, 'seller_manage_products.html', context)

from django.utils.http import urlencode

@login_required
def add_category(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('sell_zone')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(next_url)
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {
        'form': form,
        'next': next_url
    })


def about(request):
    return render(request, 'about.html')
def all_policies(request):
    return render(request, 'All_policy.html')

def terms_conditions(request):
        return render(request, 'terms_conditions.html')

def categories(request):
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')

    if search_query:
        categories = categories.filter(name__icontains=search_query)

    # Annotate categories with product count
    categories = categories.annotate(product_count=Count('product')).order_by('name')

    return render(request, 'all_categories.html', {
        'categories': categories,
        'search_query': search_query
    })

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.select_related('seller').filter(category=category)

    # Apply any filters from the request
    query = request.GET.get('q', '')
    min_price = request.GET.get('min', '')
    max_price = request.GET.get('max', '')
    region = request.GET.get('region', '')
    stock = request.GET.get('stock', '')
    sort = request.GET.get('sort', '')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except (ValueError, InvalidOperation):
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except (ValueError, InvalidOperation):
            pass

    if region:
        products = products.filter(region__icontains=region)

    if stock == "in":
        products = products.filter(stock__gt=0)
    elif stock == "out":
        products = products.filter(stock__lte=0)

    # Default sorting by newest if no sort parameter
    if sort == "asc":
        products = products.order_by('price', '-id')
    elif sort == "desc":
        products = products.order_by('-price', '-id')
    else:
        products = products.order_by('-id')

    context = {
        'category': category,
        'products': products,
        'product_count': products.count(),
    }
    return render(request, 'category_products.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def cancel_user_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    if order.status.lower() in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        
        # ✅ NEW: Notify seller when buyer cancels order
        Notification.objects.create(
            user=order.product.seller,
            notification_type='order_cancelled',
            title='Order Cancelled by Buyer',
            message=f'{request.user.first_name or request.user.username} cancelled their order for {order.product.name}',
            order=order,
            product=order.product,
            link=f'/sell-zone/orders/'
        )
        
        messages.success(request, f"Order #{order.id} has been cancelled.")
    else:
        messages.warning(request, "This order can no longer be cancelled.")

    return redirect('order_tracking')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatMessage, Product


@login_required
def seller_messages(request):
    if not request.user.is_seller():
        return redirect('home')

    # Get all messages related to seller's products, filtered to only buyer messages
    messages_obj = ChatMessage.objects.filter(
        product__seller=request.user,
        buyer__isnull=False
    ).select_related('product', 'buyer').order_by('-timestamp')
    
    # NOTE: We do NOT mark messages as read by setting seller field!
    # The seller field is CRITICAL for identifying who sent the message:
    # - seller=None means BUYER sent it (initial message)
    # - seller=request.user means SELLER sent it (reply)
    # Modifying seller field corrupts sender identification across the app
    
    # Group messages by buyer + product combination
    conversations = {}
    for message in messages_obj:
        key = f"{message.buyer.id}_{message.product.id}"
        if key not in conversations:
            conversations[key] = {
                'buyer': message.buyer,
                'product': message.product,
                'messages': [],
                'recent_message': message
            }
        conversations[key]['messages'].append(message)
    
    # Sort messages chronologically within each conversation
    product_messages = []
    for key in sorted(conversations.keys(), key=lambda k: conversations[k]['recent_message'].timestamp, reverse=True):
        conv = conversations[key]
        conv['messages'].reverse()  # Oldest first
        product_messages.append(conv)
    
    # Count totals
    total_messages = messages_obj.count()
    new_messages_count = ChatMessage.objects.filter(
        product__seller=request.user,
        seller__isnull=True,
        buyer__isnull=False
    ).count()
    
    # Prepare JSON data for JavaScript
    import json
    from django.utils import timezone
    
    all_conversations_json = []
    seller_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    
    for conversation in product_messages:
        conv_data = {
            'product': {
                'id': conversation['product'].id,
                'name': conversation['product'].name
            },
            'buyer': conversation['buyer'].username,
            'buyer_id': conversation['buyer'].id,
            'recent_message': {
                'id': conversation['recent_message'].id,
                'message': conversation['recent_message'].message,
                'seller': conversation['recent_message'].seller_id is not None,
                'buyer': conversation['recent_message'].buyer.username if conversation['recent_message'].buyer else None,
                'timestamp': conversation['recent_message'].timestamp.strftime('%b %d, %Y %H:%M')
            },
            'messages': [
                {
                    'id': msg.id,
                    'message': msg.message,
                    'buyer_name': msg.buyer.first_name or msg.buyer.username if msg.buyer else None,
                    'seller_name': seller_name if not msg.buyer else None,
                    'is_buyer_message': msg.buyer is not None,
                    'timestamp': msg.timestamp.strftime('%b %d, %Y %H:%M'),
                    'seller_read': msg.seller_id is not None
                }
                for msg in conversation['messages']
            ]
        }
        all_conversations_json.append(conv_data)
    
    # Handle AJAX requests for polling
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'total_messages': total_messages,
            'new_messages_count': new_messages_count,
        })
    
    context = {
        'products': Product.objects.filter(seller=request.user),
        'product_messages': product_messages,
        'messages': messages_obj,
        'new_messages_count': new_messages_count,
        'total_messages': total_messages,
        'all_conversations_json': json.dumps(all_conversations_json)
    }
    
    return render(request, 'seller_messages.html', context)


# ============================================================================
# Chatbot API Endpoint - Using HuggingFace Free Inference (100% Free Forever)
# ============================================================================

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .huggingface_chatbot import validate_message
from .ai_manager import get_ai_response, get_ai_stats


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def chatbot_message_api(request):
    """
    API endpoint for processing chatbot messages with Smart AI Manager.
    Automatically switches between:
    1. Gemini (free tier) - Primary
    2. HuggingFace (free inference) - Backup
    3. Local pattern matching - Fallback
    
    Never costs money and always responds!
    
    Expected POST body:
    {
        "message": "user message",
        "conversation_history": [] (optional)
    }
    
    Response:
    {
        "success": true/false,
        "response": "AI generated response",
        "service": "gemini|huggingface|fallback",
        "error": "error message if any"
    }
    """
    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        # Parse request body
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        # Validate message
        if not validate_message(user_message):
            return JsonResponse({
                'success': False,
                'error': 'Invalid message. Please provide a valid message.',
                'response': None,
                'service': None
            }, status=400)
        
        # Get response from Smart AI Manager (tries Gemini, then HuggingFace, then fallback)
        ai_response, service_used = get_ai_response(user_message)
        
        return JsonResponse({
            'success': True,
            'response': ai_response,
            'service': service_used,
            'error': None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body',
            'response': None,
            'service': None
        }, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Chatbot API error: {str(e)}")
        
        # Still try to return a response from fallback
        try:
            from .ai_manager import get_ai_manager
            manager = get_ai_manager()
            fallback_response, service = manager._get_fallback_response(user_message)
            return JsonResponse({
                'success': True,
                'response': fallback_response,
                'service': 'fallback',
                'error': None
            })
        except:
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}',
                'response': None,
                'service': None
            }, status=500)
    product_messages = []

    # For each product, get its messages
    for product in products:
        # Get messages related to the product and order by timestamp
        messages = ChatMessage.objects.filter(
            product=product
        ).filter(
            Q(seller=request.user) | Q(buyer__isnull=False, product__seller=request.user)
        ).order_by('timestamp')

        if messages.exists():
            product_messages.append({
                'product': product,
                'messages': messages
            })

    return render(request, 'seller_messages.html', {
        'product_messages': product_messages
    })


from django.shortcuts import render, get_object_or_404
from .models import Order, ChatMessage

@login_required
def view_messages(request):
    if request.user.is_authenticated:
        # Get all messages for the logged-in user (buyer/seller)
        messages = ChatMessage.objects.filter(
            Q(buyer=request.user) | Q(seller=request.user)
        ).order_by('-timestamp')  # You can modify sorting as needed

        return render(request, 'view_messages.html', {'messages': messages})
    else:
        return redirect('login')  # Or handle as per your app flow

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, ChatMessage

@login_required
def buyer_messages_in_orders(request):
    if not request.user.is_buyer():  # Ensure only buyers can access this view
        return redirect('home')

    # Get all orders related to the buyer
    orders = Order.objects.filter(buyer=request.user).select_related('product__seller')
    conversations = {}

    # Organize messages by product (conversation)
    for order in orders:
        product = order.product
        # Get messages specific to this product WHERE THIS BUYER IS INVOLVED
        # Filter by: product AND buyer must be current user
        messages = ChatMessage.objects.filter(
            product=product,
            buyer=request.user
        ).order_by('timestamp').select_related('buyer', 'seller')
        
        if messages.exists():
            seller_name = f"{product.seller.first_name} {product.seller.last_name}".strip() or product.seller.username
            
            # Prepare messages with correct sender identification
            messages_with_sender = []
            for msg in messages:
                # EXPLICIT: Message is from SELLER only if seller field is set
                # msg.seller = None means BUYER sent this
                # msg.seller = user means SELLER sent this
                is_from_seller = (msg.seller is not None and msg.seller is not False)
                
                # For BUYER viewing: always show "You" for buyer messages, seller name for seller replies
                if is_from_seller:
                    display_sender = seller_name  # Seller sent it
                else:
                    display_sender = "You"  # Buyer (current user) sent it
                
                messages_with_sender.append({
                    'message': msg,
                    'is_from_seller': is_from_seller,
                    'sender_name': display_sender
                })
            
            # Get latest message for preview
            latest_msg = messages.last()
            
            conversations[product.id] = {
                'order': order,
                'product': product,
                'seller_name': seller_name,
                'message_count': messages.count(),
                'latest_message': latest_msg.message[:100] if latest_msg else '',
                'latest_timestamp': latest_msg.timestamp if latest_msg else None,
                'messages': messages_with_sender
            }

    # Sort conversations by latest message timestamp (newest first)
    sorted_conversations = sorted(
        conversations.values(),
        key=lambda x: x['latest_timestamp'] or x['order'].ordered_at,
        reverse=True
    )

    return render(request, 'buyer_order_messages.html', {
        'conversations': sorted_conversations,
        'total_conversations': len(sorted_conversations)
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ChatMessage
from django.contrib import messages

@login_required
def reply_to_message(request, product_id):
    # Get the product to which the message belongs
    product = get_object_or_404(Product, id=product_id)

    # Check if user is seller
    if product.seller != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        return redirect('home')

    if request.method == 'POST':
        reply_content = request.POST.get('reply', '').strip()
        buyer_id = request.POST.get('buyer_id', '').strip()
        
        if not reply_content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Reply cannot be empty'})
            messages.error(request, 'Reply cannot be empty.')
            return redirect('seller_messages')

        # Get the buyer from buyer_id
        buyer = None
        if buyer_id:
            try:
                buyer = CustomUser.objects.get(id=buyer_id)
            except CustomUser.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Invalid buyer'})
                messages.error(request, 'Invalid buyer.')
                return redirect('seller_messages')

        # Create a new message in the ChatMessage model
        new_message = ChatMessage(
            product=product,
            seller=request.user,  # Seller is replying
            buyer=buyer,  # Link to the buyer so they can see the reply
            message=reply_content
        )
        new_message.save()
        
        # Create notification for buyer
        if buyer:
            Notification.objects.create(
                user=buyer,
                notification_type='seller_reply',
                title='Seller Reply',
                message=f'The seller of {product.name} has replied to your message!',
                product=product,
                link=f'/orders/messages/'
            )

        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Reply sent successfully'})
        
        # Handle form submissions
        messages.success(request, 'Your reply has been sent.')
        return redirect('seller_messages')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, ChatMessage
from django.contrib import messages

@login_required
def buyer_reply_to_message(request, product_id):
    # Ensure the user is a buyer
    if not request.user.is_buyer():
        return redirect('home')

    # Get the product to which the message belongs
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        reply_content = request.POST.get('reply')  # The reply from the buyer

        # Create a new message in the ChatMessage model
        new_message = ChatMessage(
            product=product,
            buyer=request.user,  # Assuming the buyer is replying
            message=reply_content
        )
        new_message.save()

        # Create notification for seller
        Notification.objects.create(
            user=product.seller,
            notification_type='seller_reply',
            title='Buyer Message',
            message=f'{request.user.first_name or request.user.username} has replied to your message about {product.name}!',
            product=product,
            link=f'/product/{product_id}/chat/'
        )

        # Optionally, you can send a success message
        messages.success(request, 'Your reply has been sent.')

        return redirect('buyer_messages_in_orders')  # Redirect back to the buyer's messages page for that order

@login_required
def delete_seller_messages(request, product_id):
    """Delete all messages for a product conversation (seller side)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    product = get_object_or_404(Product, id=product_id)
    
    # Verify seller owns this product
    if product.seller != request.user:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
    
    try:
        # Delete all messages for this product
        deleted_count, _ = ChatMessage.objects.filter(product=product).delete()
        return JsonResponse({'success': True, 'message': f'Deleted {deleted_count} messages', 'deleted_count': deleted_count})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def delete_buyer_messages(request, product_id):
    """Delete all messages for a product conversation (buyer side)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    product = get_object_or_404(Product, id=product_id)
    
    # Verify buyer has conversations with this product
    has_messages = ChatMessage.objects.filter(product=product, buyer=request.user).exists()
    if not has_messages:
        return JsonResponse({'success': False, 'message': 'No messages found'}, status=403)
    
    try:
        # Delete all messages for this product involving this buyer
        deleted_count, _ = ChatMessage.objects.filter(product=product, buyer=request.user).delete()
        return JsonResponse({'success': True, 'message': f'Deleted {deleted_count} messages', 'deleted_count': deleted_count})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


# =============================================
# NOTIFICATIONS API
# =============================================

@login_required
def get_notifications(request):
    """Fetch all unread notifications for the user"""
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]
    
    notification_list = []
    for notif in notifications:
        notification_list.append({
            'id': notif.id,
            'type': notif.notification_type,
            'title': notif.title,
            'message': notif.message,
            'link': notif.link,
            'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'time_ago': format_time_ago(notif.created_at),
        })
    
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return JsonResponse({
        'success': True,
        'notifications': notification_list,
        'unread_count': unread_count
    })


@login_required
def mark_notification_as_read(request, notification_id):
    """Mark a notification as read"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'success': True, 'unread_count': unread_count})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Notification not found'}, status=404)


@login_required
def mark_all_notifications_as_read(request):
    """Mark all notifications as read"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True, 'unread_count': 0})


def format_time_ago(dt):
    """Format datetime to 'X minutes ago' format"""
    from django.utils import timezone
    now = timezone.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} min' if minutes == 1 else f'{minutes} mins'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour' if hours == 1 else f'{hours} hours'
    else:
        days = int(seconds / 86400)
        return f'{days} day' if days == 1 else f'{days} days'

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser  # Ensure you import your CustomUser model

@login_required
def apply_seller_status(request):
    # Check if the user is already a seller
    if request.user.user_type == 'seller':
        # If the user is already a seller, render the 'already_seller' template
        return render(request, 'already_seller.html')
    else:
        # Redirect to the seller application page if the user is not a seller
        return redirect('apply_seller')  # Replace 'apply_seller' with your actual seller application page URL name


# =============================================
# 🤖 AI SERVICE STATISTICS
# =============================================

@login_required
def ai_service_stats(request):
    """View AI service statistics - Admin only"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    from .ai_manager import get_ai_stats
    stats = get_ai_stats()
    
    return JsonResponse({
        'success': True,
        'stats': stats,
        'timestamp': str(datetime.now())
    })


@login_required
def reset_ai_stats(request):
    """Reset AI service statistics - Admin only"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Admin access required'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=400)
    
    from .ai_manager import reset_ai_stats as reset_stats
    reset_stats()
    
    return JsonResponse({
        'success': True,
        'message': 'AI statistics reset'
    })


def ai_shopping_assistant(request):
    query = ""
    assistant_reply = "Tell me what you want to buy, and I will recommend products."
    recommendations = []
    used_llm = False

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        result = get_shopping_assistant_result(query)
        assistant_reply = result.reply
        recommendations = result.recommendations
        used_llm = result.used_llm

    return render(request, 'ai_assistant.html', {
        'query': query,
        'assistant_reply': assistant_reply,
        'recommendations': recommendations,
        'used_llm': used_llm,
    })


# =============================================
# 🔄 PRODUCT COMPARISON FEATURE
# =============================================

def add_to_comparison(request, product_id):
    """Add a product to comparison list"""
    product = get_object_or_404(Product, id=product_id)
    
    # Initialize comparison list in session if it doesn't exist
    if 'compare_products' not in request.session:
        request.session['compare_products'] = []
    
    compare_list = request.session['compare_products']
    
    # Limit to 2 products for comparison
    if len(compare_list) < 2 and product_id not in compare_list:
        compare_list.append(product_id)
        request.session['compare_products'] = compare_list
        request.session.modified = True
        messages.success(request, f'{product.name} added to comparison.')
    elif product_id in compare_list:
        messages.warning(request, f'{product.name} is already in comparison.')
    else:
        messages.warning(request, 'You can only compare 2 products at a time.')
    
    return redirect('product_detail', pk=product_id)


def remove_from_comparison(request, product_id):
    """Remove a product from comparison list"""
    if 'compare_products' in request.session:
        compare_list = request.session['compare_products']
        if product_id in compare_list:
            compare_list.remove(product_id)
            request.session['compare_products'] = compare_list
            request.session.modified = True
            product = get_object_or_404(Product, id=product_id)
            messages.success(request, f'{product.name} removed from comparison.')
    
    return redirect('compare_products')


def clear_comparison(request):
    """Clear all products from comparison"""
    if 'compare_products' in request.session:
        del request.session['compare_products']
        request.session.modified = True
        messages.success(request, 'Comparison list cleared.')
    
    return redirect('compare_products')


def compare_products(request):
    """Display comparison of two products"""
    compare_list = request.session.get('compare_products', [])
    products = []
    
    if compare_list:
        products = Product.objects.filter(id__in=compare_list).select_related('category', 'seller').prefetch_related('reviews')
    
    # Get comparison attributes
    comparison_data = []
    if len(products) == 2:
        product1, product2 = products[0], products[1]
        
        comparison_data = [
            {'label': 'Name', 'product1': product1.name, 'product2': product2.name},
            {'label': 'Category', 'product1': product1.category.name if product1.category else 'N/A', 'product2': product2.category.name if product2.category else 'N/A'},
            {'label': 'Price', 'product1': f"${product1.price}", 'product2': f"${product2.price}"},
            {'label': 'Discounted Price', 'product1': f"${product1.discounted_price}" if product1.discounted_price else 'N/A', 'product2': f"${product2.discounted_price}" if product2.discounted_price else 'N/A'},
            {'label': 'Stock', 'product1': f"{product1.stock} units", 'product2': f"{product2.stock} units"},
            {'label': 'Region', 'product1': product1.region, 'product2': product2.region},
            {'label': 'Seller', 'product1': product1.seller.username, 'product2': product2.seller.username},
            {'label': 'Rating', 'product1': f"{product1.rating}/5", 'product2': f"{product2.rating}/5"},
            {'label': 'Created', 'product1': product1.created_at.strftime('%Y-%m-%d'), 'product2': product2.created_at.strftime('%Y-%m-%d')},
        ]
    
    return render(request, 'compare_products.html', {
        'products': products,
        'comparison_data': comparison_data,
        'compare_list': compare_list,
    })


# =============================================
# 🎛️ ADMIN DASHBOARD FEATURES
# =============================================

def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.user_type == 'admin'

@login_required
def admin_dashboard(request):
    """Main Admin Dashboard with Statistics"""
    if not is_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Statistics
    total_users = CustomUser.objects.count()
    total_sellers = CustomUser.objects.filter(user_type='seller').count()
    total_buyers = CustomUser.objects.filter(user_type='buyer').count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_reviews = Review.objects.count()
    pending_seller_applications = SellerApplication.objects.filter(approved=False).count()
    
    # Recent activity
    recent_orders = Order.objects.select_related('buyer', 'product').order_by('-ordered_at')[:5]
    recent_products = Product.objects.select_related('seller').order_by('-created_at')[:5]
    recent_reviews = Review.objects.select_related('product', 'reviewer').order_by('-created_at')[:5]
    
    # Out of stock products
    out_of_stock = Product.objects.filter(stock=0).count()
    
    context = {
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_buyers': total_buyers,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_reviews': total_reviews,
        'pending_seller_applications': pending_seller_applications,
        'out_of_stock': out_of_stock,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_users(request):
    """Manage all users"""
    if not is_admin(request.user):
        return redirect('home')
    
    user_type_filter = request.GET.get('type', '')
    search = request.GET.get('search', '')
    
    users = CustomUser.objects.all()
    
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))
    
    users = users.order_by('-date_joined')
    
    context = {'users': users, 'user_type_filter': user_type_filter, 'search': search}
    return render(request, 'admin_users.html', context)

@login_required
def admin_users_by_location(request):
    """View users organized by Bangladesh divisions (locations)"""
    if not is_admin(request.user):
        return redirect('home')
    
    # Bangladesh divisions
    divisions = [
        'Dhaka', 'Chattogram', 'Barishal', 'Khulna', 
        'Mymensingh', 'Rajshahi', 'Rangpur', 'Sylhet'
    ]
    
    selected_division = request.GET.get('division', '')
    division_data = {}
    
    # Get data for all divisions
    for division in divisions:
        div_users = CustomUser.objects.filter(location__icontains=division)
        buyers = div_users.filter(user_type='buyer')
        sellers = div_users.filter(user_type='seller', is_seller_approved=True)
        
        division_data[division] = {
            'total_users': div_users.count(),
            'total_buyers': buyers.count(),
            'total_sellers': sellers.count(),
            'buyers_list': buyers.order_by('-date_joined'),
            'sellers_list': sellers.order_by('-date_joined'),
        }
    
    # Get details for selected division if provided
    selected_data = None
    if selected_division in divisions:
        selected_data = {
            'division': selected_division,
            'stats': division_data[selected_division]
        }
    
    context = {
        'divisions': divisions,
        'division_data': division_data,
        'selected_division': selected_division,
        'selected_data': selected_data,
    }
    return render(request, 'admin_users_by_location.html', context)

@login_required
def admin_products(request):
    """Manage all products"""
    if not is_admin(request.user):
        return redirect('home')
    
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    products = Product.objects.select_related('seller', 'category').annotate(avg_rating=Avg('reviews__rating'))
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if status_filter == 'low_stock':
        products = products.filter(stock__lte=10, stock__gt=0)
    elif status_filter == 'out_of_stock':
        products = products.filter(stock=0)
    elif status_filter == 'in_stock':
        products = products.filter(stock__gt=0)
    
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    products = products.order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'search': search
    }
    return render(request, 'admin_products.html', context)

@login_required
def admin_orders(request):
    """Manage all orders"""
    if not is_admin(request.user):
        return redirect('home')
    
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    search = request.GET.get('search', '')
    
    orders = Order.objects.select_related('buyer', 'product').order_by('-ordered_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if payment_filter == 'paid':
        orders = orders.filter(payment_status=True)
    elif payment_filter == 'unpaid':
        orders = orders.filter(payment_status=False)
    
    if search:
        orders = orders.filter(Q(buyer__username__icontains=search) | Q(product__name__icontains=search))
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'search': search
    }
    return render(request, 'admin_orders.html', context)

@login_required
def admin_seller_applications(request):
    """Manage seller applications"""
    if not is_admin(request.user):
        return redirect('home')
    
    approval_filter = request.GET.get('approval', '')
    search = request.GET.get('search', '')
    
    applications = SellerApplication.objects.select_related('user').order_by('-submitted_at')
    
    if approval_filter == 'pending':
        applications = applications.filter(approved=False)
    elif approval_filter == 'approved':
        applications = applications.filter(approved=True)
    
    if search:
        applications = applications.filter(Q(user__username__icontains=search) | Q(shop_name__icontains=search))
    
    context = {
        'applications': applications,
        'approval_filter': approval_filter,
        'search': search
    }
    return render(request, 'admin_seller_applications.html', context)

@login_required
def admin_reviews(request):
    """Manage and moderate reviews"""
    if not is_admin(request.user):
        return redirect('home')
    
    rating_filter = request.GET.get('rating', '')
    product_filter = request.GET.get('product', '')
    search = request.GET.get('search', '')
    
    reviews = Review.objects.select_related('product', 'reviewer').order_by('-created_at')
    
    if rating_filter:
        reviews = reviews.filter(rating=rating_filter)
    
    if product_filter:
        reviews = reviews.filter(product_id=product_filter)
    
    if search:
        reviews = reviews.filter(Q(reviewer__username__icontains=search) | Q(product__name__icontains=search) | Q(comment__icontains=search))
    
    products = Product.objects.all()
    
    context = {
        'reviews': reviews,
        'products': products,
        'rating_filter': rating_filter,
        'product_filter': product_filter,
        'search': search
    }
    return render(request, 'admin_reviews.html', context)

@login_required
def admin_approve_seller(request, application_id):
    """Approve a seller application"""
    if not is_admin(request.user):
        return redirect('home')
    
    application = get_object_or_404(SellerApplication, id=application_id)
    user = application.user
    
    user.user_type = 'seller'
    user.is_seller_approved = True
    user.save()
    
    application.approved = True
    application.save()
    
    messages.success(request, f"Seller application from {user.username} approved.")
    return redirect('admin_seller_applications')

@login_required
def admin_reject_seller(request, application_id):
    """Reject a seller application"""
    if not is_admin(request.user):
        return redirect('home')
    
    application = get_object_or_404(SellerApplication, id=application_id)
    
    application.delete()
    messages.success(request, "Seller application rejected.")
    return redirect('admin_seller_applications')

@login_required
def admin_deactivate_user(request, user_id):
    """Deactivate a user"""
    if not is_admin(request.user):
        return redirect('home')
    
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    
    messages.success(request, f"User {user.username} has been deactivated.")
    return redirect('admin_users')

@login_required
def admin_activate_user(request, user_id):
    """Activate a user"""
    if not is_admin(request.user):
        return redirect('home')
    
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    
    messages.success(request, f"User {user.username} has been activated.")
    return redirect('admin_users')

@login_required
def admin_delete_product(request, product_id):
    """Delete a product"""
    if not is_admin(request.user):
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    
    messages.success(request, f"Product '{product_name}' has been deleted.")
    return redirect('admin_products')

@login_required
def admin_delete_review(request, review_id):
    """Delete a review (moderation)"""
    if not is_admin(request.user):
        return redirect('home')
    
    review = get_object_or_404(Review, id=review_id)
    product_name = review.product.name
    review.delete()
    
    messages.success(request, f"Review for '{product_name}' has been deleted.")
    return redirect('admin_reviews')

@login_required
def admin_order_details(request, order_id):
    """View order details"""
    if not is_admin(request.user):
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    
    context = {'order': order}
    return render(request, 'admin_order_details.html', context)

@login_required
def admin_update_order_status(request, order_id):
    """Update order status"""
    if not is_admin(request.user):
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ORDER_STATUS):
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status.")
    
    return redirect('admin_order_details', order_id=order_id)

@login_required
def admin_mark_payment(request, order_id):
    """Mark order as paid"""
    if not is_admin(request.user):
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = True
    order.save()
    
    messages.success(request, f"Order #{order.id} marked as paid.")
    return redirect('admin_order_details', order_id=order_id)

@login_required
def admin_user_details(request, user_id):
    """View user details"""
    if not is_admin(request.user):
        return redirect('home')
    
    user = get_object_or_404(CustomUser, id=user_id)
    user_orders = Order.objects.filter(buyer=user).count()
    user_products = Product.objects.filter(seller=user).count() if user.user_type == 'seller' else 0
    user_reviews = Review.objects.filter(reviewer=user).count()
    
    context = {
        'user': user,
        'user_orders': user_orders,
        'user_products': user_products,
        'user_reviews': user_reviews,
    }
    return render(request, 'admin_user_details.html', context)

@login_required
def admin_product_details(request, product_id):
    """View product details"""
    if not is_admin(request.user):
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    orders = Order.objects.filter(product=product).count()
    
    context = {
        'product': product,
        'reviews': reviews,
        'orders': orders,
    }
    return render(request, 'admin_product_details.html', context)


# =============================================
# 🤖 AI MESSAGE SUGGESTIONS API
# =============================================

@login_required
@require_http_methods(["POST"])
def get_message_suggestions_api(request):
    """
    API endpoint for getting AI-powered message suggestions
    Usage: POST to /api/message-suggestions/ with JSON body containing 'message' and optionally 'product_id'
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        product_id = data.get('product_id')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty',
                'suggestions': []
            }, status=400)
        
        # Get suggestions from AI
        from .ai_assistant import get_message_suggestions
        suggestions_data = get_message_suggestions(message, product_id)
        
        # Increment usage count if product_id exists
        if product_id:
            try:
                from .models import AIMessageSuggestion
                AIM = AIMessageSuggestion.objects.filter(product_id=product_id).first()
                if AIM:
                    AIM.usage_count += 1
                    AIM.save()
            except:
                pass
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions_data.get('suggestions', []),
            'template_matches': suggestions_data.get('template_matches', [])
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
            'suggestions': []
        }, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Message suggestions API error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Server error',  
            'suggestions': []
        }, status=500)


