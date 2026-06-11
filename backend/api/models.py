from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Customer(models.Model):
    phone = models.CharField(max_length=11, unique=True)
    nickname = models.CharField(max_length=40, blank=True)
    avatar_url = models.URLField(blank=True)
    points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.nickname or self.phone


class Address(models.Model):
    customer = models.ForeignKey(Customer, related_name="addresses", on_delete=models.CASCADE)
    receiver_name = models.CharField(max_length=40)
    receiver_phone = models.CharField(max_length=11)
    detail = models.CharField(max_length=200)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "id"]

    def __str__(self):
        return f"{self.receiver_name} {self.detail}"


class Coupon(models.Model):
    STATUS_UNUSED = "unused"
    STATUS_USED = "used"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_UNUSED, "未使用"),
        (STATUS_USED, "已使用"),
        (STATUS_EXPIRED, "已过期"),
    ]

    customer = models.ForeignKey(Customer, related_name="coupons", on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UNUSED)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "expires_at"]

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=40, unique=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT)
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=300, blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True)
    is_sold_out = models.BooleanField(default=False)
    specs = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category__sort_order", "id"]

    def __str__(self):
        return self.name

    def price_for_specs(self, selected_specs):
        price = Decimal(self.base_price)
        selected_specs = selected_specs or {}
        groups = self.specs.get("groups", [])

        for group in groups:
            selected = selected_specs.get(group.get("name"))
            if selected is None:
                continue

            if not isinstance(selected, list):
                selected = [selected]

            for option in group.get("options", []):
                if option.get("name") in selected:
                    price += Decimal(str(option.get("price_delta", 0)))

        return price.quantize(Decimal("0.01"))


class CartItem(models.Model):
    customer = models.ForeignKey(Customer, related_name="cart_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    selected_specs = models.JSONField(default=dict, blank=True)
    spec_text = models.CharField(max_length=200, blank=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    @property
    def subtotal(self):
        return (self.unit_price * self.quantity).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_PENDING_PAYMENT = "pending_payment"
    STATUS_MAKING = "making"
    STATUS_READY = "ready"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_PENDING_PAYMENT, "待支付"),
        (STATUS_MAKING, "制作中"),
        (STATUS_READY, "请取货"),
        (STATUS_COMPLETED, "已完成"),
        (STATUS_CANCELED, "已取消"),
    ]

    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.PROTECT)
    order_no = models.CharField(max_length=32, unique=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING_PAYMENT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remark = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_no

    def mark_paid(self):
        self.status = self.STATUS_MAKING
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=80)
    product_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    selected_specs = models.JSONField(default=dict, blank=True)
    spec_text = models.CharField(max_length=200, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Payment(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "支付成功"),
        (STATUS_FAILED, "支付失败"),
    ]

    order = models.OneToOneField(Order, related_name="payment", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    transaction_no = models.CharField(max_length=40, unique=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return self.transaction_no


class Review(models.Model):
    customer = models.ForeignKey(Customer, related_name="reviews", on_delete=models.CASCADE)
    order = models.OneToOneField(Order, related_name="review", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.order_no} {self.rating}星"
