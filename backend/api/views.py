import re
from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CartItem, Category, Customer, Order, OrderItem, Payment, Product, Review
from .serializers import (
    CartItemSerializer,
    CategorySerializer,
    CustomerSerializer,
    OrderSerializer,
    ProductSerializer,
    ReviewSerializer,
)


PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


def api_response(data=None, message="success", code=0, http_status=status.HTTP_200_OK):
    return Response({"code": code, "message": message, "data": data}, status=http_status)


def error_response(message, code=40000, http_status=status.HTTP_400_BAD_REQUEST, data=None):
    return api_response(data=data, message=message, code=code, http_status=http_status)


def format_spec_text(selected_specs):
    if not selected_specs:
        return ""

    parts = []
    for key, value in selected_specs.items():
        if isinstance(value, list):
            value_text = "、".join(str(item) for item in value)
        else:
            value_text = str(value)
        parts.append(f"{key}: {value_text}")
    return "；".join(parts)


def generate_order_no():
    return f"FO{timezone.now():%Y%m%d%H%M%S}{uuid4().hex[:6].upper()}"


def generate_transaction_no():
    return f"PAY{timezone.now():%Y%m%d%H%M%S}{uuid4().hex[:8].upper()}"


@api_view(["GET"])
def health_check(request):
    return api_response({"service": "online-food-order-platform", "status": "ok"})


@api_view(["POST"])
def login(request):
    phone = str(request.data.get("phone", "")).strip()
    code = str(request.data.get("code", "")).strip()

    if not PHONE_RE.match(phone):
        return error_response("请输入合法的 11 位手机号", code=40001)

    if code != "123456":
        return error_response("验证码错误，MVP 固定验证码为 123456", code=40002)

    customer, created = Customer.objects.get_or_create(
        phone=phone,
        defaults={
            "nickname": f"用户{phone[-4:]}",
            "points": 120,
        },
    )

    return api_response(
        {
            "customer": CustomerSerializer(customer).data,
            "is_new_user": created,
        }
    )


@api_view(["GET", "PATCH"])
def customer_detail(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return error_response("用户不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        customer.nickname = request.data.get("nickname", customer.nickname)
        customer.avatar_url = request.data.get("avatar_url", customer.avatar_url)
        customer.save(update_fields=["nickname", "avatar_url", "updated_at"])

    return api_response(CustomerSerializer(customer).data)


@api_view(["GET"])
def categories(request):
    queryset = Category.objects.all()
    return api_response(CategorySerializer(queryset, many=True).data)


@api_view(["GET"])
def products(request):
    queryset = Product.objects.select_related("category").all()
    category_id = request.query_params.get("category")
    search = request.query_params.get("search")
    include_sold_out = request.query_params.get("include_sold_out") == "1"

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

    if not include_sold_out:
        queryset = queryset.filter(is_sold_out=False)

    return api_response(ProductSerializer(queryset, many=True).data)


@api_view(["GET", "POST"])
def cart_items(request):
    if request.method == "GET":
        customer_id = request.query_params.get("customer_id")
        if not customer_id:
            return error_response("缺少 customer_id", code=40003)

        queryset = CartItem.objects.select_related("customer", "product", "product__category").filter(
            customer_id=customer_id
        )
        total_count = sum(item.quantity for item in queryset)
        total_amount = sum((item.subtotal for item in queryset), Decimal("0.00"))
        return api_response(
            {
                "items": CartItemSerializer(queryset, many=True).data,
                "total_count": total_count,
                "total_amount": f"{total_amount:.2f}",
            }
        )

    customer_id = request.data.get("customer_id")
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    selected_specs = request.data.get("selected_specs", {}) or {}

    if quantity <= 0:
        return error_response("商品数量必须大于 0", code=40004)

    try:
        customer = Customer.objects.get(id=customer_id)
        product = Product.objects.get(id=product_id)
    except Customer.DoesNotExist:
        return error_response("用户不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return error_response("商品不存在", code=40402, http_status=status.HTTP_404_NOT_FOUND)

    if product.is_sold_out:
        return error_response("商品已售罄，无法加入购物车", code=40005)

    item = CartItem.objects.create(
        customer=customer,
        product=product,
        quantity=quantity,
        selected_specs=selected_specs,
        spec_text=format_spec_text(selected_specs),
        unit_price=product.price_for_specs(selected_specs),
    )

    return api_response(CartItemSerializer(item).data, http_status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
def cart_item_detail(request, item_id):
    try:
        item = CartItem.objects.select_related("product").get(id=item_id)
    except CartItem.DoesNotExist:
        return error_response("购物车项不存在", code=40403, http_status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        item.delete()
        return api_response({"deleted": True})

    quantity = int(request.data.get("quantity", item.quantity))
    selected_specs = request.data.get("selected_specs", item.selected_specs)

    if quantity <= 0:
        return error_response("商品数量必须大于 0", code=40004)

    if item.product.is_sold_out:
        return error_response("商品已售罄，无法修改购物车项", code=40005)

    item.quantity = quantity
    item.selected_specs = selected_specs
    item.spec_text = format_spec_text(selected_specs)
    item.unit_price = item.product.price_for_specs(selected_specs)
    item.save()
    return api_response(CartItemSerializer(item).data)


@api_view(["GET", "POST"])
def orders(request):
    if request.method == "GET":
        customer_id = request.query_params.get("customer_id")
        queryset = Order.objects.prefetch_related("items").select_related("customer").all()
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return api_response(OrderSerializer(queryset, many=True).data)

    customer_id = request.data.get("customer_id")
    remark = request.data.get("remark", "")

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return error_response("用户不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        cart_queryset = (
            CartItem.objects.select_related("product", "product__category")
            .filter(customer=customer)
            .select_for_update()
        )
        cart_items_list = list(cart_queryset)

        if not cart_items_list:
            return error_response("购物车为空，无法提交订单", code=40006)

        for item in cart_items_list:
            if item.product.is_sold_out:
                return error_response(f"{item.product.name} 已售罄，请从购物车移除", code=40005)

        total_amount = sum((item.subtotal for item in cart_items_list), Decimal("0.00")).quantize(
            Decimal("0.01")
        )
        order = Order.objects.create(
            customer=customer,
            order_no=generate_order_no(),
            status=Order.STATUS_PENDING_PAYMENT,
            total_amount=total_amount,
            remark=remark,
        )

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.unit_price,
                quantity=item.quantity,
                selected_specs=item.selected_specs,
                spec_text=item.spec_text,
                subtotal=item.subtotal,
            )
            for item in cart_items_list
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_queryset.delete()

    return api_response(OrderSerializer(order).data, http_status=status.HTTP_201_CREATED)


@api_view(["GET"])
def order_detail(request, order_id):
    try:
        order = Order.objects.prefetch_related("items").select_related("customer").get(id=order_id)
    except Order.DoesNotExist:
        return error_response("订单不存在", code=40404, http_status=status.HTTP_404_NOT_FOUND)

    return api_response(OrderSerializer(order).data)


@api_view(["POST"])
def mock_payment(request):
    order_id = request.data.get("order_id")
    success = request.data.get("success", True)
    success = success in [True, "true", "1", 1, "success"]

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return error_response("订单不存在", code=40404, http_status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.STATUS_PENDING_PAYMENT:
        return error_response("只有待支付订单可以发起支付", code=40007)

    with transaction.atomic():
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            status=Payment.STATUS_SUCCESS if success else Payment.STATUS_FAILED,
            transaction_no=generate_transaction_no(),
        )
        if success:
            order.mark_paid()
        else:
            order.status = Order.STATUS_CANCELED
            order.save(update_fields=["status", "updated_at"])

    return api_response({"order": OrderSerializer(order).data, "payment_id": payment.id})


@api_view(["POST"])
def create_review(request, order_id):
    try:
        order = Order.objects.select_related("customer").get(id=order_id)
    except Order.DoesNotExist:
        return error_response("订单不存在", code=40404, http_status=status.HTTP_404_NOT_FOUND)

    if order.status != Order.STATUS_COMPLETED:
        return error_response("只有已完成订单可以评价", code=40008)

    if hasattr(order, "review"):
        return error_response("该订单已经评价过", code=40009)

    serializer = ReviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    review = serializer.save(customer=order.customer, order=order)
    return api_response(ReviewSerializer(review).data, http_status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
def admin_products(request):
    if request.method == "GET":
        queryset = Product.objects.select_related("category").all()
        return api_response(ProductSerializer(queryset, many=True).data)

    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save()
    return api_response(ProductSerializer(product).data, http_status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
def admin_product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return error_response("商品不存在", code=40402, http_status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return api_response(serializer.data)


@api_view(["PATCH"])
def admin_product_sold_out(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return error_response("商品不存在", code=40402, http_status=status.HTTP_404_NOT_FOUND)

    product.is_sold_out = bool(request.data.get("is_sold_out", True))
    product.save(update_fields=["is_sold_out", "updated_at"])
    return api_response(ProductSerializer(product).data)


@api_view(["GET"])
def admin_orders(request):
    order_status = request.query_params.get("status")
    queryset = Order.objects.prefetch_related("items").select_related("customer").all()
    if order_status:
        queryset = queryset.filter(status=order_status)
    return api_response(OrderSerializer(queryset, many=True).data)


@api_view(["PATCH"])
def admin_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return error_response("订单不存在", code=40404, http_status=status.HTTP_404_NOT_FOUND)

    target_status = request.data.get("status")
    allowed = {
        Order.STATUS_MAKING: [Order.STATUS_READY, Order.STATUS_CANCELED],
        Order.STATUS_READY: [Order.STATUS_COMPLETED],
    }

    if target_status not in allowed.get(order.status, []):
        return error_response("订单状态流转非法", code=40010, data={"current_status": order.status})

    order.status = target_status
    order.save(update_fields=["status", "updated_at"])
    return api_response(OrderSerializer(order).data)
