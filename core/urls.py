from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('apply-seller/', views.apply_seller, name='apply_seller'),
    path('seller-requests/', views.seller_requests, name='seller_requests'),
    path('seller-requests/<int:pk>/approve/', views.approve_seller, name='approve_seller'),
    path('seller-requests/<int:pk>/reject/', views.reject_seller, name='reject_seller'),
    path('sell-zone/', views.sell_zone, name='sell_zone'),
    path('sell-zone/manage-products/', views.seller_manage_products, name='seller_manage_products'),
    path('sell-zone/add-product/', views.add_product, name='add_product'),
    path('sell-zone/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('sell-zone/orders/', views.seller_orders, name='seller_orders'),
    path('sell-zone/cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('sell-zone/update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('place-order/', views.place_order, name='place_order'),
    path('orders/', views.order_tracking, name='order_tracking'),
    path('product/<int:pk>/review/', views.submit_review, name='submit_review'),
    path('product/<int:pk>/chat/', views.product_chat, name='product_chat'),
    path('search/', views.search_products, name='search_products'),
    path('product/update/<int:pk>/', views.update_product, name='update_product'),
    path('category/add/', views.add_category, name='add_category'),
    path('categories/', views.categories, name='categories'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('about/', views.about, name='about'),
    path('policies/', views.all_policies, name='all_policies'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('orders/cancel/<int:order_id>/', views.cancel_user_order, name='cancel_user_order'),
    path('sell-zone/messages/', views.seller_messages, name='seller_messages'),
    path('orders/messages/', views.buyer_messages_in_orders, name='buyer_messages_in_orders'),
    path('sell-zone/messages/reply/<int:product_id>/', views.reply_to_message, name='reply_to_message'),
    path('orders/messages/reply/buyer/<int:product_id>/', views.buyer_reply_to_message, name='buyer_reply_to_message'),
    path('sell-zone/messages/delete/<int:product_id>/', views.delete_seller_messages, name='delete_seller_messages'),
    path('orders/messages/delete/<int:product_id>/', views.delete_buyer_messages, name='delete_buyer_messages'),
    path('apply-seller-status/', views.apply_seller_status, name='apply_seller_status'),
    path('ai-assistant/', views.ai_shopping_assistant, name='ai_assistant'),
    path('api/chatbot/', views.chatbot_message_api, name='chatbot_message_api'),
    path('compare/', views.compare_products, name='compare_products'),
    path('compare/add/<int:product_id>/', views.add_to_comparison, name='add_to_comparison'),
    path('compare/remove/<int:product_id>/', views.remove_from_comparison, name='remove_from_comparison'),
    path('compare/clear/', views.clear_comparison, name='clear_comparison'),
    
    # =============================================
    # ADMIN DASHBOARD ROUTES
    # =============================================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/users-by-location/', views.admin_users_by_location, name='admin_users_by_location'),
    path('admin-dashboard/products/', views.admin_products, name='admin_products'),
    path('admin-dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('admin-dashboard/seller-applications/', views.admin_seller_applications, name='admin_seller_applications'),
    path('admin-dashboard/reviews/', views.admin_reviews, name='admin_reviews'),
    
    # Admin Actions
    path('admin-dashboard/seller-applications/<int:application_id>/approve/', views.admin_approve_seller, name='admin_approve_seller'),
    path('admin-dashboard/seller-applications/<int:application_id>/reject/', views.admin_reject_seller, name='admin_reject_seller'),
    path('admin-dashboard/users/<int:user_id>/deactivate/', views.admin_deactivate_user, name='admin_deactivate_user'),
    path('admin-dashboard/users/<int:user_id>/activate/', views.admin_activate_user, name='admin_activate_user'),
    path('admin-dashboard/products/<int:product_id>/delete/', views.admin_delete_product, name='admin_delete_product'),
    path('admin-dashboard/reviews/<int:review_id>/delete/', views.admin_delete_review, name='admin_delete_review'),
    
    # Admin Details
    path('admin-dashboard/orders/<int:order_id>/', views.admin_order_details, name='admin_order_details'),
    path('admin-dashboard/orders/<int:order_id>/update-status/', views.admin_update_order_status, name='admin_update_order_status'),
    path('admin-dashboard/orders/<int:order_id>/mark-paid/', views.admin_mark_payment, name='admin_mark_payment'),
    path('admin-dashboard/users/<int:user_id>/', views.admin_user_details, name='admin_user_details'),
    path('admin-dashboard/products/<int:product_id>/', views.admin_product_details, name='admin_product_details'),
    
    # Notification API
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('api/notifications/read-all/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    
    # AI Message Suggestions API
    path('api/message-suggestions/', views.get_message_suggestions_api, name='get_message_suggestions'),
    
    # AI Service Statistics API
    path('api/ai-stats/', views.ai_service_stats, name='ai_service_stats'),
    path('api/ai-stats/reset/', views.reset_ai_stats, name='reset_ai_stats'),
]
