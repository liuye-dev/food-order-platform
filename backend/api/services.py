import re
from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status

from .exceptions import BusinessError
from .models import CartItem, Customer, Order, OrderItem, Payment, Product, Review


PHONE_RE = re.compile(r"^1[3-9]\d{9}$")
TRUE_VALUES = {True, "true", "1", 1, "success", "yes", "on"}
FALSE_VALUES = {False, "false", "0", 0, "failed", "no", "off"}


def parse_positive_int(value, message="商品数量必须大于 0", code=40004):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise BusinessError(message, code=code)

    if number <= 0:
        raise BusinessError(message, code=code)

    return number


def parse_bool(value, default=False):
    if value is None:
        return default

    normalized = value.lower() if isinstance(value, str) else value
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False

    raise BusinessError("布尔参数格式不正确", code=40011)


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


def get_customer_or_raise(customer_id):
    try:
        return Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        raise BusinessError("用户不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)


def get_product_or_raise(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise BusinessError("商品不存在", code=40402, http_status=status.HTTP_404_NOT_FOUND)


def get_order_or_raise(order_id):
    try:
        return Order.objects.prefetch_related("items").select_related("customer").get(id=order_id)
    except Order.DoesNotExist:
        raise BusinessError("订单不存在", code=40404, http_status=status.HTTP_404_NOT_FOUND)


def login_with_phone(phone, code):
    phone = str(phone or "").strip()
    code = str(code or "").strip()

    if not PHONE_RE.match(phone):
        raise BusinessError("请输入合法的 11 位手机号", code=40001)

    if code != "123456":
        raise BusinessError("验证码错误，MVP 固定验证码为 123456", code=40002)

    return Customer.objects.get_or_create(
        phone=phone,
        defaults={
            "nickname": f"用户{phone[-4:]}",
            "points": 120,
        },
    )


def update_customer_profile(customer_id, data):
    customer = get_customer_or_raise(customer_id)
    customer.nickname = data.get("nickname", customer.nickname)
    customer.avatar_url = data.get("avatar_url", customer.avatar_url)
    customer.save(update_fields=["nickname", "avatar_url", "updated_at"])
    return customer


def list_products(category_id=None, search=None, include_sold_out=False):
    queryset = Product.objects.select_related("category").all()

    if category_id:
        queryset = queryset.filter(category_id=category_id)

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

    if not include_sold_out:
        queryset = queryset.filter(is_sold_out=False)

    return queryset


def get_cart_summary(customer_id):
    if not customer_id:
        raise BusinessError("缺少 customer_id", code=40003)

    queryset = CartItem.objects.select_related("customer", "product", "product__category").filter(
        customer_id=customer_id
    )
    total_count = sum(item.quantity for item in queryset)
    total_amount = sum((item.subtotal for item in queryset), Decimal("0.00"))

    return queryset, total_count, f"{total_amount:.2f}"


def add_cart_item(customer_id, product_id, quantity=1, selected_specs=None):
    quantity = parse_positive_int(quantity)
    selected_specs = selected_specs or {}
    customer = get_customer_or_raise(customer_id)
    product = get_product_or_raise(product_id)

    if product.is_sold_out:
        raise BusinessError("商品已售罄，无法加入购物车", code=40005)

    return CartItem.objects.create(
        customer=customer,
        product=product,
        quantity=quantity,
        selected_specs=selected_specs,
        spec_text=format_spec_text(selected_specs),
        unit_price=product.price_for_specs(selected_specs),
    )


def get_cart_item_or_raise(item_id):
    try:
        return CartItem.objects.select_related("product").get(id=item_id)
    except CartItem.DoesNotExist:
        raise BusinessError("购物车项不存在", code=40403, http_status=status.HTTP_404_NOT_FOUND)


def update_cart_item(item_id, quantity=None, selected_specs=None):
    item = get_cart_item_or_raise(item_id)
    quantity = parse_positive_int(item.quantity if quantity is None else quantity)
    selected_specs = item.selected_specs if selected_specs is None else selected_specs

    if item.product.is_sold_out:
        raise BusinessError("商品已售罄，无法修改购物车项", code=40005)

    item.quantity = quantity
    item.selected_specs = selected_specs
    item.spec_text = format_spec_text(selected_specs)
    item.unit_price = item.product.price_for_specs(selected_specs)
    item.save()
    return item


def delete_cart_item(item_id):
    item = get_cart_item_or_raise(item_id)
    item.delete()


def list_orders(customer_id=None):
    queryset = Order.objects.prefetch_related("items").select_related("customer").all()
    if customer_id:
        queryset = queryset.filter(customer_id=customer_id)
    return queryset


def create_order_from_cart(customer_id, remark=""):
    customer = get_customer_or_raise(customer_id)

    with transaction.atomic():
        cart_queryset = (
            CartItem.objects.select_related("product", "product__category")
            .filter(customer=customer)
            .select_for_update()
        )
        cart_items = list(cart_queryset)

        if not cart_items:
            raise BusinessError("购物车为空，无法提交订单", code=40006)

        for item in cart_items:
            if item.product.is_sold_out:
                raise BusinessError(f"{item.product.name} 已售罄，请从购物车移除", code=40005)

        total_amount = sum((item.subtotal for item in cart_items), Decimal("0.00")).quantize(
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
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart_queryset.delete()

    return get_order_or_raise(order.id)


def mock_pay_order(order_id, success=True):
    order = get_order_or_raise(order_id)
    success = parse_bool(success, default=True)

    if order.status != Order.STATUS_PENDING_PAYMENT:
        raise BusinessError("只有待支付订单可以发起支付", code=40007)

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

    return get_order_or_raise(order.id), payment


def get_reviewable_order(order_id):
    order = get_order_or_raise(order_id)

    if order.status != Order.STATUS_COMPLETED:
        raise BusinessError("只有已完成订单可以评价", code=40008)

    if Review.objects.filter(order=order).exists():
        raise BusinessError("该订单已经评价过", code=40009)

    return order


def set_product_sold_out(product_id, value=True):
    product = get_product_or_raise(product_id)
    product.is_sold_out = parse_bool(value, default=True)
    product.save(update_fields=["is_sold_out", "updated_at"])
    return product


def list_admin_orders(order_status=None):
    queryset = Order.objects.prefetch_related("items").select_related("customer").all()
    if order_status:
        queryset = queryset.filter(status=order_status)
    return queryset


def advance_order_status(order_id, target_status):
    order = get_order_or_raise(order_id)
    allowed = {
        Order.STATUS_MAKING: [Order.STATUS_READY, Order.STATUS_CANCELED],
        Order.STATUS_READY: [Order.STATUS_COMPLETED],
    }

    if target_status not in allowed.get(order.status, []):
        raise BusinessError("订单状态流转非法", code=40010, data={"current_status": order.status})

    order.status = target_status
    order.save(update_fields=["status", "updated_at"])
    return get_order_or_raise(order.id)
