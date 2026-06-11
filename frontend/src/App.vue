<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  ClipboardList,
  CookingPot,
  CreditCard,
  Minus,
  PackageCheck,
  Plus,
  RefreshCw,
  Search,
  ShoppingCart,
  Store,
  UserRound,
} from "lucide-vue-next";

import { api } from "./api";


const activeRole = ref("customer");
const loading = ref(false);
const message = ref("");
const error = ref("");

const loginForm = reactive({
  phone: "13800000000",
  code: "123456",
});

const customer = ref(null);
const categories = ref([]);
const products = ref([]);
const cart = ref({ items: [], total_count: 0, total_amount: "0.00" });
const orders = ref([]);
const selectedCategoryId = ref("");
const searchText = ref("");
const activeProduct = ref(null);
const specDraft = reactive({});

const adminProducts = ref([]);
const adminOrders = ref([]);
const productForm = reactive({
  category: "",
  name: "",
  description: "",
  base_price: "",
  image_url: "",
});

const statusSteps = [
  { value: "pending_payment", label: "待支付" },
  { value: "making", label: "制作中" },
  { value: "ready", label: "请取货" },
  { value: "completed", label: "已完成" },
];

const customerId = computed(() => customer.value?.id);
const visibleProducts = computed(() => products.value);

function setMessage(text) {
  message.value = text;
  error.value = "";
}

function setError(text) {
  error.value = text;
  message.value = "";
}

async function runTask(task, successText) {
  loading.value = true;
  error.value = "";

  try {
    const result = await task();
    if (successText) {
      setMessage(successText);
    }
    return result;
  } catch (err) {
    setError(err.message);
    return null;
  } finally {
    loading.value = false;
  }
}

async function loadBaseData() {
  const [categoryData, productData] = await Promise.all([
    api.getCategories(),
    api.getProducts({ include_sold_out: 1 }),
  ]);
  categories.value = categoryData;
  products.value = productData;
  adminProducts.value = productData;
}

async function refreshProducts() {
  const params = {
    include_sold_out: 1,
  };
  if (selectedCategoryId.value) {
    params.category = selectedCategoryId.value;
  }
  if (searchText.value.trim()) {
    params.search = searchText.value.trim();
  }
  products.value = await api.getProducts(params);
}

async function login() {
  await runTask(async () => {
    const data = await api.login(loginForm);
    customer.value = data.customer;
    await Promise.all([refreshCart(), refreshOrders()]);
  }, "登录成功");
}

function selectProduct(product) {
  activeProduct.value = product;
  Object.keys(specDraft).forEach((key) => delete specDraft[key]);

  for (const group of product.specs?.groups || []) {
    if (group.type === "multi") {
      specDraft[group.name] = [];
    } else {
      specDraft[group.name] = group.options?.[0]?.name || "";
    }
  }
}

function toggleMultiSpec(groupName, optionName) {
  const selected = specDraft[groupName] || [];
  if (selected.includes(optionName)) {
    specDraft[groupName] = selected.filter((item) => item !== optionName);
  } else {
    specDraft[groupName] = [...selected, optionName];
  }
}

function selectSpec(group, optionName) {
  if (group.type === "multi") {
    toggleMultiSpec(group.name, optionName);
  } else {
    specDraft[group.name] = optionName;
  }
}

function specPrice(product, selectedSpecs) {
  let price = Number(product.base_price || 0);
  for (const group of product.specs?.groups || []) {
    const selected = selectedSpecs[group.name];
    const selectedList = Array.isArray(selected) ? selected : [selected];
    for (const option of group.options || []) {
      if (selectedList.includes(option.name)) {
        price += Number(option.price_delta || 0);
      }
    }
  }
  return price.toFixed(2);
}

async function addToCart(product = activeProduct.value) {
  if (!customerId.value) {
    setError("请先登录再点餐");
    return;
  }
  if (!product || product.is_sold_out) {
    setError("商品不可加入购物车");
    return;
  }

  await runTask(async () => {
    await api.addCartItem({
      customer_id: customerId.value,
      product_id: product.id,
      quantity: 1,
      selected_specs: { ...specDraft },
    });
    activeProduct.value = null;
    await refreshCart();
  }, "已加入购物车");
}

async function refreshCart() {
  if (!customerId.value) {
    return;
  }
  cart.value = await api.getCart(customerId.value);
}

async function updateCartQuantity(item, nextQuantity) {
  if (nextQuantity <= 0) {
    await removeCartItem(item);
    return;
  }

  await runTask(async () => {
    await api.updateCartItem(item.id, {
      quantity: nextQuantity,
      selected_specs: item.selected_specs,
    });
    await refreshCart();
  });
}

async function removeCartItem(item) {
  await runTask(async () => {
    await api.deleteCartItem(item.id);
    await refreshCart();
  }, "已移除购物车项");
}

async function submitOrder() {
  if (!customerId.value) {
    setError("请先登录再提交订单");
    return;
  }

  const order = await runTask(async () => {
    return await api.createOrder({
      customer_id: customerId.value,
      remark: "门店自取",
    });
  });

  if (!order) {
    return;
  }

  await runTask(async () => {
    await api.payOrder({ order_id: order.id, success: true });
    await Promise.all([refreshCart(), refreshOrders(), refreshAdminOrders()]);
  }, "模拟支付成功，订单已进入制作中");
}

async function refreshOrders() {
  if (!customerId.value) {
    return;
  }
  orders.value = await api.getOrders(customerId.value);
}

async function submitReview(order, rating) {
  await runTask(async () => {
    await api.createReview(order.id, {
      rating,
      content: "商品口味不错，取餐流程顺畅",
    });
    await refreshOrders();
  }, "评价提交成功");
}

async function refreshAdminProducts() {
  adminProducts.value = await api.getAdminProducts();
}

async function refreshAdminOrders() {
  adminOrders.value = await api.getAdminOrders();
}

async function createProduct() {
  await runTask(async () => {
    await api.createProduct({
      category: Number(productForm.category),
      name: productForm.name,
      description: productForm.description,
      base_price: productForm.base_price,
      image_url: productForm.image_url,
      specs: { groups: [] },
    });
    Object.assign(productForm, {
      category: "",
      name: "",
      description: "",
      base_price: "",
      image_url: "",
    });
    await Promise.all([loadBaseData(), refreshAdminProducts()]);
  }, "商品已新增");
}

async function toggleSoldOut(product) {
  await runTask(async () => {
    await api.setProductSoldOut(product.id, !product.is_sold_out);
    await Promise.all([refreshProducts(), refreshAdminProducts()]);
  }, "商品状态已更新");
}

function nextOrderStatus(order) {
  if (order.status === "making") {
    return "ready";
  }
  if (order.status === "ready") {
    return "completed";
  }
  return "";
}

async function advanceOrder(order) {
  const nextStatus = nextOrderStatus(order);
  if (!nextStatus) {
    return;
  }

  await runTask(async () => {
    await api.updateOrderStatus(order.id, nextStatus);
    await Promise.all([refreshAdminOrders(), refreshOrders()]);
  }, "订单状态已推进");
}

function statusIndex(status) {
  return statusSteps.findIndex((step) => step.value === status);
}

onMounted(async () => {
  await runTask(async () => {
    await loadBaseData();
    await refreshAdminOrders();
  });
});
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Django + Vue + MySQL</p>
        <h1>在线点餐平台</h1>
      </div>
      <div class="role-tabs" aria-label="角色切换">
        <button :class="{ active: activeRole === 'customer' }" @click="activeRole = 'customer'">
          <UserRound :size="18" />
          顾客端
        </button>
        <button :class="{ active: activeRole === 'admin' }" @click="activeRole = 'admin'">
          <Store :size="18" />
          商家端
        </button>
      </div>
    </header>

    <div v-if="message" class="notice success">{{ message }}</div>
    <div v-if="error" class="notice error">{{ error }}</div>

    <section v-if="activeRole === 'customer'" class="workspace customer-layout">
      <aside class="panel login-panel">
        <div class="panel-heading">
          <UserRound :size="20" />
          <h2>顾客登录</h2>
        </div>
        <label>
          手机号
          <input v-model="loginForm.phone" maxlength="11" />
        </label>
        <label>
          验证码
          <input v-model="loginForm.code" maxlength="6" />
        </label>
        <button class="primary-btn" :disabled="loading" @click="login">登录 / 注册</button>
        <div v-if="customer" class="profile-line">
          <strong>{{ customer.nickname }}</strong>
          <span>{{ customer.phone }}</span>
          <span>{{ customer.points }} 积分</span>
        </div>
      </aside>

      <section class="menu-area">
        <div class="toolbar">
          <div class="search-box">
            <Search :size="18" />
            <input v-model="searchText" placeholder="搜索商品" @keyup.enter="refreshProducts" />
          </div>
          <button class="icon-btn" title="刷新菜单" @click="refreshProducts">
            <RefreshCw :size="18" />
          </button>
        </div>

        <div class="category-strip">
          <button :class="{ active: selectedCategoryId === '' }" @click="selectedCategoryId = ''; refreshProducts()">
            全部
          </button>
          <button
            v-for="category in categories"
            :key="category.id"
            :class="{ active: String(category.id) === String(selectedCategoryId) }"
            @click="selectedCategoryId = category.id; refreshProducts()"
          >
            {{ category.name }}
          </button>
        </div>

        <div class="product-grid">
          <article v-for="product in visibleProducts" :key="product.id" class="product-card">
            <img :src="product.image_url" :alt="product.name" />
            <div class="product-info">
              <div>
                <span class="tag">{{ product.category_name }}</span>
                <h3>{{ product.name }}</h3>
                <p>{{ product.description }}</p>
              </div>
              <div class="product-actions">
                <strong>￥{{ product.base_price }}</strong>
                <button :disabled="product.is_sold_out" @click="selectProduct(product)">
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
            <button title="减少数量" @click="updateCartQuantity(item, item.quantity - 1)">
              <Minus :size="14" />
            </button>
            <span>{{ item.quantity }}</span>
            <button title="增加数量" @click="updateCartQuantity(item, item.quantity + 1)">
              <Plus :size="14" />
            </button>
          </div>
        </div>
        <div class="cart-total">
          <span>{{ cart.total_count }} 件</span>
          <strong>￥{{ cart.total_amount }}</strong>
        </div>
        <button class="primary-btn" :disabled="loading || cart.items.length === 0" @click="submitOrder">
          <CreditCard :size="18" />
          提交订单并模拟支付
        </button>
      </aside>

      <section class="panel orders-panel">
        <div class="panel-heading">
          <ClipboardList :size="20" />
          <h2>我的订单</h2>
          <button class="icon-btn" title="刷新订单" @click="refreshOrders">
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
            <button v-if="order.status === 'completed' && !order.review" @click="submitReview(order, 5)">
              五星评价
            </button>
          </div>
        </article>
      </section>
    </section>

    <section v-else class="workspace admin-layout">
      <section class="panel">
        <div class="panel-heading">
          <Store :size="20" />
          <h2>商品管理</h2>
          <button class="icon-btn" title="刷新商品" @click="refreshAdminProducts">
            <RefreshCw :size="16" />
          </button>
        </div>

        <form class="product-form" @submit.prevent="createProduct">
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
          <article v-for="product in adminProducts" :key="product.id" class="admin-product">
            <img :src="product.image_url" :alt="product.name" />
            <div>
              <strong>{{ product.name }}</strong>
              <p>{{ product.category_name }} / ￥{{ product.base_price }}</p>
            </div>
            <button :class="{ danger: !product.is_sold_out }" @click="toggleSoldOut(product)">
              {{ product.is_sold_out ? "恢复销售" : "设为售罄" }}
            </button>
          </article>
        </div>
      </section>

      <section class="panel">
        <div class="panel-heading">
          <CookingPot :size="20" />
          <h2>订单处理</h2>
          <button class="icon-btn" title="刷新订单" @click="refreshAdminOrders">
            <RefreshCw :size="16" />
          </button>
        </div>

        <div v-if="adminOrders.length === 0" class="empty-state">暂无订单</div>
        <article v-for="order in adminOrders" :key="order.id" class="admin-order">
          <div>
            <span class="tag">{{ order.status_display }}</span>
            <strong>{{ order.order_no }}</strong>
            <p>{{ order.customer_nickname || order.customer_phone }}</p>
            <p>{{ order.items.map((item) => `${item.product_name} x${item.quantity}`).join("，") }}</p>
          </div>
          <div class="order-tail">
            <strong>￥{{ order.total_amount }}</strong>
            <button v-if="nextOrderStatus(order)" @click="advanceOrder(order)">
              <PackageCheck :size="16" />
              推进状态
            </button>
          </div>
        </article>
      </section>
    </section>

    <div v-if="activeProduct" class="modal-mask" @click.self="activeProduct = null">
      <section class="spec-modal">
        <img :src="activeProduct.image_url" :alt="activeProduct.name" />
        <div class="spec-content">
          <h2>{{ activeProduct.name }}</h2>
          <p>{{ activeProduct.description }}</p>
          <div v-for="group in activeProduct.specs?.groups || []" :key="group.name" class="spec-group">
            <h3>{{ group.name }}</h3>
            <div class="spec-options">
              <button
                v-for="option in group.options"
                :key="option.name"
                :class="{
                  active: group.type === 'multi'
                    ? specDraft[group.name]?.includes(option.name)
                    : specDraft[group.name] === option.name,
                }"
                @click="selectSpec(group, option.name)"
              >
                {{ option.name }}
                <span v-if="option.price_delta">+￥{{ option.price_delta }}</span>
              </button>
            </div>
          </div>
          <div class="modal-footer">
            <strong>￥{{ specPrice(activeProduct, specDraft) }}</strong>
            <button class="primary-btn" @click="addToCart()">
              <ShoppingCart :size="18" />
              加入购物车
            </button>
          </div>
        </div>
      </section>
    </div>
  </main>
</template>
