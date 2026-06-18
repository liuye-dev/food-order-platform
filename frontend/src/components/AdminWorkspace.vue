<script setup>
import { CookingPot, PackageCheck, RefreshCw, Store } from "lucide-vue-next";


defineProps({
  categories: { type: Array, required: true },
  orders: { type: Array, required: true },
  productForm: { type: Object, required: true },
  products: { type: Array, required: true },
});

const emit = defineEmits([
  "advance-order",
  "create-product",
  "refresh-orders",
  "refresh-products",
  "toggle-sold-out",
]);

function nextOrderStatus(order) {
  if (order.status === "making") {
    return "ready";
  }
  if (order.status === "ready") {
    return "completed";
  }
  return "";
}
</script>

<template>
  <section class="workspace admin-layout">
    <section class="panel">
      <div class="panel-heading">
        <Store :size="20" />
        <h2>商品管理</h2>
        <button class="icon-btn" title="刷新商品" @click="emit('refresh-products')">
          <RefreshCw :size="16" />
        </button>
      </div>

      <form class="product-form" @submit.prevent="emit('create-product')">
        <select v-model="productForm.category" required>
          <option value="">选择分类</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <input v-model="productForm.name" required placeholder="商品名称" />
        <input v-model="productForm.base_price" required type="number" min="0" step="0.01" placeholder="价格" />
        <input v-model="productForm.image_url" placeholder="图片 URL" />
        <input v-model="productForm.description" placeholder="商品描述" />
        <button class="primary-btn" type="submit">新增商品</button>
      </form>

      <div class="admin-list">
        <article v-for="product in products" :key="product.id" class="admin-product">
          <img :src="product.image_url" :alt="product.name" />
          <div>
            <strong>{{ product.name }}</strong>
            <p>{{ product.category_name }} / ￥{{ product.base_price }}</p>
          </div>
          <button :class="{ danger: !product.is_sold_out }" @click="emit('toggle-sold-out', product)">
            {{ product.is_sold_out ? "恢复销售" : "设为售罄" }}
          </button>
        </article>
      </div>
    </section>

    <section class="panel">
      <div class="panel-heading">
        <CookingPot :size="20" />
        <h2>订单处理</h2>
        <button class="icon-btn" title="刷新订单" @click="emit('refresh-orders')">
          <RefreshCw :size="16" />
        </button>
      </div>

      <div v-if="orders.length === 0" class="empty-state">暂无订单</div>
      <article v-for="order in orders" :key="order.id" class="admin-order">
        <div>
          <span class="tag">{{ order.status_display }}</span>
          <strong>{{ order.order_no }}</strong>
          <p>{{ order.customer_nickname || order.customer_phone }}</p>
          <p>{{ order.items.map((item) => `${item.product_name} x${item.quantity}`).join("，") }}</p>
        </div>
        <div class="order-tail">
          <strong>￥{{ order.total_amount }}</strong>
          <button v-if="nextOrderStatus(order)" @click="emit('advance-order', order)">
            <PackageCheck :size="16" />
            推进状态
          </button>
        </div>
      </article>
    </section>
  </section>
</template>
