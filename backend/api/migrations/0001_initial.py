import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=40, unique=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name_plural": "categories",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(max_length=11, unique=True)),
                ("nickname", models.CharField(blank=True, max_length=40)),
                ("avatar_url", models.URLField(blank=True)),
                ("points", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("description", models.CharField(blank=True, max_length=300)),
                ("base_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("image_url", models.URLField(blank=True)),
                ("is_sold_out", models.BooleanField(default=False)),
                ("specs", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="api.category",
                    ),
                ),
            ],
            options={
                "ordering": ["category__sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("receiver_name", models.CharField(max_length=40)),
                ("receiver_phone", models.CharField(max_length=11)),
                ("detail", models.CharField(max_length=200)),
                ("is_default", models.BooleanField(default=False)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to="api.customer",
                    ),
                ),
            ],
            options={
                "ordering": ["-is_default", "id"],
            },
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("selected_specs", models.JSONField(blank=True, default=dict)),
                ("spec_text", models.CharField(blank=True, max_length=200)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cart_items",
                        to="api.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cart_items",
                        to="api.product",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="Coupon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=80)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "status",
                    models.CharField(
                        choices=[("unused", "未使用"), ("used", "已使用"), ("expired", "已过期")],
                        default="unused",
                        max_length=20,
                    ),
                ),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="coupons",
                        to="api.customer",
                    ),
                ),
            ],
            options={
                "ordering": ["status", "expires_at"],
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_no", models.CharField(max_length=32, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending_payment", "待支付"),
                            ("making", "制作中"),
                            ("ready", "请取货"),
                            ("completed", "已完成"),
                            ("canceled", "已取消"),
                        ],
                        default="pending_payment",
                        max_length=30,
                    ),
                ),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("remark", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orders",
                        to="api.customer",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=80)),
                ("product_price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("quantity", models.PositiveIntegerField()),
                ("selected_specs", models.JSONField(blank=True, default=dict)),
                ("spec_text", models.CharField(blank=True, max_length=200)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="api.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.product",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "支付成功"), ("failed", "支付失败")],
                        max_length=20,
                    ),
                ),
                ("transaction_no", models.CharField(max_length=40, unique=True)),
                ("paid_at", models.DateTimeField(auto_now_add=True)),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment",
                        to="api.order",
                    ),
                ),
            ],
            options={
                "ordering": ["-paid_at"],
            },
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ]
                    ),
                ),
                ("content", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="api.customer",
                    ),
                ),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review",
                        to="api.order",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
