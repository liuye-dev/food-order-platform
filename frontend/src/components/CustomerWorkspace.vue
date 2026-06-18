<script setup>
import { computed } from "vue";
import {
  ClipboardList,
  CreditCard,
  Minus,
  Plus,
  RefreshCw,
  Search,
  ShoppingCart,
} from "lucide-vue-next";


const props = defineProps({
  cart: { type: Object, required: true },
  categories: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  orders: { type: Array, required: true },
  products: { type: Array, required: true },
  searchText: { type: String, default: "" },
  selectedCategoryId: { type: [String, Number], default: "" },
  statusSteps: { type: Array, required: true },
});

const emit = defineEmits([
  "refresh-orders",
  "refresh-products",
  "select-product",
  "submit-order",
  "submit-review",
  "update-cart-quantity",
  "update:searchText",
  "update:selectedCategoryId",
]);

const searchValue = computed({
  get: () => props.searchText,
  set: (value) => emit("update:searchText", value),
});

function chooseCategory(categoryId) {
  emit("update:selectedCategoryId", categoryId);
  emit("refresh-products");
}

function statusIndex(status) {
  return props.statusSteps.findIndex((step) => step.value === status);
}
</script>

<template>
  <section class="workspace customer-layout">
    <section class="menu-area">
      <div class="toolbar">
        <div class="search-box">
          <Search :size="18" />
          <input v-model="searchValue" placeholder="搜索商品" @keyup.enter="emit('refresh-products')" />
        </div>
        <button class="icon-btn" title="刷新菜单" @click="emit('refresh-products')">
          <RefreshCw :size="18" />
        </button>
      </div>

      <div class="category-strip">
        <button :class="{ active: selectedCategoryId === '' }" @click="chooseCategory('')">
          全部
        </button>
        <button
          v-for="category in categories"
          :key="category.id"
          :class="{ active: String(category.id) === String(selectedCategoryId) }"
          @click="chooseCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </div>

      <div class="product-grid">
        <article v-for="product in products" :key="product.id" class="product-card">
          <img :src="product.image_url" :alt="product.name" />
          <div class="product-info">
            <div>
              <span class="tag">{{ product.category_name }}</span>
              <h3>{{ product.name }}</h3>
              <p>{{ product.description }}</p>
            </div>
            <div class="product-actions">
              <strong>￥{{ product.base_price }}</strong>
              <button :disabled="product.is_sold_out" @click="emit('select-product', product)">
                <Plus :size="16" />
                {{ product.is_sold_out ? "售罄" : "选规格" }}
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>

    <aside class="panel cart-panel">
      <div class="panel-heading">
        <ShoppingCart :size="20" />
        <h2>购物车</h2>
      </div>
      <div v-if="cart.items.length === 0" class="empty-state">暂无商品</div>
      <div v-for="item in cart.items" :key="item.id" class="cart-item">
        <div>
          <strong>{{ item.product.name }}</strong>
          <p>{{ item.spec_text || "默认规格" }}</p>
          <span>￥{{ item.unit_price }}</span>
        </div>
        <div class="quantity">
          <button title="减少数量" @click="emit('update-cart-quantity', item, item.quantity - 1)">
            <Minus :size="14" />
          </button>
          <span>{{ item.quantity }}</span>
          <button title="增加数量" @click="emit('update-cart-quantity', item, item.quantity + 1)">
            <Plus :size="14" />
          </button>
        </div>
      </div>
      <div class="cart-total">
        <span>{{ cart.total_count }} 件</span>
        <strong>￥{{ cart.total_amount }}</strong>
      </div>
      <button class="primary-btn" :disabled="loading || cart.items.length === 0" @click="emit('submit-order')">
        <CreditCard :size="18" />
        提交订单并模拟支付
      </button>
    </aside>

    <section class="panel orders-panel">
      <div class="panel-heading">
        <ClipboardList :size="20" />
        <h2>我的订单</h2>
        <button class="icon-btn" title="刷新订单" @click="emit('refresh-orders')">
          <RefreshCw :size="16" />
        </button>
      </div>
      <div v-if="orders.length === 0" class="empty-state">暂无订单</div>
      <article v-for="order in orders" :key="order.id" class="order-row">
        <div>
          <strong>{{ order.order_no }}</strong>
          <p>{{ order.items.map((item) => `${item.product_name} x${item.quantity}`).join("，") }}</p>
        </div>
        <div class="status-line">
          <span
            v-for="(step, index) in statusSteps"
            :key="step.value"
            :class="{ done: index <= statusIndex(order.status) }"
          >
            {{ step.label }}
          </span>
        </div>
        <div class="order-tail">
          <strong>￥{{ order.total_amount }}</strong>
          <button v-if="order.status === 'completed' && !order.review" @click="emit('submit-review', order, 5)">
            五星评价
          </button>
        </div>
      </article>
    </section>
  </section>
</template>
