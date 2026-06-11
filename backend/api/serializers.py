from rest_framework import serializers

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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "receiver_name", "receiver_phone", "detail", "is_default"]


class CouponSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Coupon
        fields = ["id", "title", "amount", "status", "status_display", "expires_at"]


class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    coupons = CouponSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "phone",
            "nickname",
            "avatar_url",
            "points",
            "addresses",
            "coupons",
            "created_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "sort_order"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "description",
            "base_price",
            "image_url",
            "is_sold_out",
            "specs",
            "created_at",
            "updated_at",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "customer",
            "product",
            "quantity",
            "selected_specs",
            "spec_text",
            "unit_price",
            "subtotal",
            "created_at",
            "updated_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "selected_specs",
            "spec_text",
            "subtotal",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "amount", "status", "status_display", "transaction_no", "paid_at"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "customer", "order", "rating", "content", "created_at"]
        read_only_fields = ["customer", "order", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    review = ReviewSerializer(read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    customer_nickname = serializers.CharField(source="customer.nickname", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_no",
            "customer",
            "customer_phone",
            "customer_nickname",
            "status",
            "status_display",
            "total_amount",
            "remark",
            "items",
            "payment",
            "review",
            "created_at",
            "paid_at",
            "updated_at",
        ]
