from rest_framework import status
from rest_framework.decorators import api_view

from . import services
from .models import Category
from .responses import api_response, handle_business_errors
from .serializers import (
    CartItemSerializer,
    CategorySerializer,
    CustomerSerializer,
    OrderSerializer,
    ProductSerializer,
    ReviewSerializer,
)


@api_view(["GET"])
def health_check(request):
    return api_response({"service": "online-food-order-platform", "status": "ok"})


@api_view(["POST"])
@handle_business_errors
def login(request):
    customer, created = services.login_with_phone(
        phone=request.data.get("phone"),
        code=request.data.get("code"),
    )
    return api_response(
        {
            "customer": CustomerSerializer(customer).data,
            "is_new_user": created,
        }
    )


@api_view(["GET", "PATCH"])
@handle_business_errors
def customer_detail(request, customer_id):
    if request.method == "PATCH":
        customer = services.update_customer_profile(customer_id, request.data)
    else:
        customer = services.get_customer_or_raise(customer_id)

    return api_response(CustomerSerializer(customer).data)


@api_view(["GET"])
def categories(request):
    queryset = Category.objects.all()
    return api_response(CategorySerializer(queryset, many=True).data)


@api_view(["GET"])
@handle_business_errors
def products(request):
    queryset = services.list_products(
        category_id=request.query_params.get("category"),
        search=request.query_params.get("search"),
        include_sold_out=services.parse_bool(
            request.query_params.get("include_sold_out"),
            default=False,
        ),
    )
    return api_response(ProductSerializer(queryset, many=True).data)


@api_view(["GET", "POST"])
@handle_business_errors
def cart_items(request):
    if request.method == "GET":
        queryset, total_count, total_amount = services.get_cart_summary(
            request.query_params.get("customer_id")
        )
        return api_response(
            {
                "items": CartItemSerializer(queryset, many=True).data,
                "total_count": total_count,
                "total_amount": total_amount,
            }
        )

    item = services.add_cart_item(
        customer_id=request.data.get("customer_id"),
        product_id=request.data.get("product_id"),
        quantity=request.data.get("quantity", 1),
        selected_specs=request.data.get("selected_specs", {}) or {},
    )
    return api_response(CartItemSerializer(item).data, http_status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@handle_business_errors
def cart_item_detail(request, item_id):
    if request.method == "DELETE":
        services.delete_cart_item(item_id)
        return api_response({"deleted": True})

    item = services.update_cart_item(
        item_id=item_id,
        quantity=request.data.get("quantity"),
        selected_specs=request.data.get("selected_specs"),
    )
    return api_response(CartItemSerializer(item).data)


@api_view(["GET", "POST"])
@handle_business_errors
def orders(request):
    if request.method == "GET":
        queryset = services.list_orders(customer_id=request.query_params.get("customer_id"))
        return api_response(OrderSerializer(queryset, many=True).data)

    order = services.create_order_from_cart(
        customer_id=request.data.get("customer_id"),
        remark=request.data.get("remark", ""),
    )
    return api_response(OrderSerializer(order).data, http_status=status.HTTP_201_CREATED)


@api_view(["GET"])
@handle_business_errors
def order_detail(request, order_id):
    order = services.get_order_or_raise(order_id)
    return api_response(OrderSerializer(order).data)


@api_view(["POST"])
@handle_business_errors
def mock_payment(request):
    order, payment = services.mock_pay_order(
        order_id=request.data.get("order_id"),
        success=request.data.get("success", True),
    )
    return api_response({"order": OrderSerializer(order).data, "payment_id": payment.id})


@api_view(["POST"])
@handle_business_errors
def create_review(request, order_id):
    order = services.get_reviewable_order(order_id)
    serializer = ReviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    review = serializer.save(customer=order.customer, order=order)
    return api_response(ReviewSerializer(review).data, http_status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
def admin_products(request):
    if request.method == "GET":
        queryset = services.list_products(include_sold_out=True)
        return api_response(ProductSerializer(queryset, many=True).data)

    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save()
    return api_response(ProductSerializer(product).data, http_status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@handle_business_errors
def admin_product_detail(request, product_id):
    product = services.get_product_or_raise(product_id)
    serializer = ProductSerializer(product, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return api_response(serializer.data)


@api_view(["PATCH"])
@handle_business_errors
def admin_product_sold_out(request, product_id):
    product = services.set_product_sold_out(
        product_id=product_id,
        value=request.data.get("is_sold_out", True),
    )
    return api_response(ProductSerializer(product).data)


@api_view(["GET"])
def admin_orders(request):
    queryset = services.list_admin_orders(order_status=request.query_params.get("status"))
    return api_response(OrderSerializer(queryset, many=True).data)


@api_view(["PATCH"])
@handle_business_errors
def admin_order_status(request, order_id):
    order = services.advance_order_status(
        order_id=order_id,
        target_status=request.data.get("status"),
    )
    return api_response(OrderSerializer(order).data)
