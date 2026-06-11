from django.contrib import admin

from .models import (
    Address,
    CartItem,
    Category,
    Coupon,
    Customer,
    Order,
    OrderItem,
    Payment,
    Product,
    Review,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "product_price", "quantity", "spec_text", "subtotal"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "phone", "nickname", "points", "created_at"]
    search_fields = ["phone", "nickname"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "sort_order"]
    ordering = ["sort_order", "id"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "category", "base_price", "is_sold_out"]
    list_filter = ["category", "is_sold_out"]
    search_fields = ["name", "description"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "product", "quantity", "unit_price", "updated_at"]
    list_filter = ["product__category"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "order_no", "customer", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order_no", "customer__phone"]
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction_no", "order", "amount", "status", "paid_at"]
    list_filter = ["status"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "customer", "rating", "created_at"]
    list_filter = ["rating"]


admin.site.register(Address)
admin.site.register(Coupon)
