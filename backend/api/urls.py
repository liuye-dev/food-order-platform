from django.urls import path

from . import views


urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("login/", views.login, name="login"),
    path("customers/<int:customer_id>/", views.customer_detail, name="customer-detail"),
    path("categories/", views.categories, name="categories"),
    path("products/", views.products, name="products"),
    path("cart/items/", views.cart_items, name="cart-items"),
    path("cart/items/<int:item_id>/", views.cart_item_detail, name="cart-item-detail"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:order_id>/", views.order_detail, name="order-detail"),
    path("orders/<int:order_id>/review/", views.create_review, name="create-review"),
    path("payments/mock/", views.mock_payment, name="mock-payment"),
    path("admin/products/", views.admin_products, name="admin-products"),
    path("admin/products/<int:product_id>/", views.admin_product_detail, name="admin-product-detail"),
    path("admin/products/<int:product_id>/sold-out/", views.admin_product_sold_out, name="admin-product-sold-out"),
    path("admin/orders/", views.admin_orders, name="admin-orders"),
    path("admin/orders/<int:order_id>/status/", views.admin_order_status, name="admin-order-status"),
]
