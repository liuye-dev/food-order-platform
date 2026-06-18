<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { LogOut, Store, UserRound } from "lucide-vue-next";

import { api } from "./api";
import AdminWorkspace from "./components/AdminWorkspace.vue";
import CustomerWorkspace from "./components/CustomerWorkspace.vue";
import LoginPage from "./components/LoginPage.vue";
import ProductSpecModal from "./components/ProductSpecModal.vue";


const sessionRole = ref("");
const loading = ref(false);
const message = ref("");
const error = ref("");

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
const roleLabel = computed(() => (sessionRole.value === "admin" ? "商家端" : "顾客端"));
const accountLabel = computed(() => {
  if (sessionRole.value === "admin") {
    return "商家管理员";
  }
  return customer.value?.nickname || "顾客";
});

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

async function loginCustomer(loginForm) {
  await runTask(async () => {
    const data = await api.login(loginForm);
    customer.value = data.customer;
    sessionRole.value = "customer";
    await Promise.all([refreshCart(), refreshOrders()]);
  }, "登录成功");
}

async function loginAdmin(adminForm) {
  await runTask(async () => {
    if (adminForm.username !== "admin" || adminForm.password !== "123456") {
      throw new Error("商家账号或密码错误，演示账号为 admin / 123456");
    }

    sessionRole.value = "admin";
    await Promise.all([refreshAdminProducts(), refreshAdminOrders()]);
  }, "商家登录成功");
}

function logout() {
  sessionRole.value = "";
  activeProduct.value = null;
  message.value = "";
  error.value = "";
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

onMounted(async () => {
  try {
    await loadBaseData();
  } catch (err) {
    setError(err.message);
  }
});
</script>

<template>
  <LoginPage
    v-if="!sessionRole"
    :error="error"
    :loading="loading"
    :message="message"
    @admin-login="loginAdmin"
    @customer-login="loginCustomer"
  />

  <main v-else class="app-shell">
    <header v-if="sessionRole" class="topbar">
      <div>
        <h1>在线点餐平台</h1>
      </div>
      <div class="account-bar">
        <span class="role-chip">
          <UserRound v-if="sessionRole === 'customer'" :size="16" />
          <Store v-else :size="16" />
          {{ roleLabel }}
        </span>
        <strong>{{ accountLabel }}</strong>
        <button class="icon-text-btn" @click="logout">
          <LogOut :size="16" />
          退出
        </button>
      </div>
    </header>

    <template v-if="sessionRole">
      <div v-if="message" class="notice success">{{ message }}</div>
      <div v-if="error" class="notice error">{{ error }}</div>
    </template>

    <CustomerWorkspace
      v-if="sessionRole === 'customer'"
      v-model:search-text="searchText"
      v-model:selected-category-id="selectedCategoryId"
      :cart="cart"
      :categories="categories"
      :loading="loading"
      :orders="orders"
      :products="products"
      :status-steps="statusSteps"
      @refresh-orders="refreshOrders"
      @refresh-products="refreshProducts"
      @select-product="selectProduct"
      @submit-order="submitOrder"
      @submit-review="submitReview"
      @update-cart-quantity="updateCartQuantity"
    />

    <AdminWorkspace
      v-else-if="sessionRole === 'admin'"
      :categories="categories"
      :orders="adminOrders"
      :product-form="productForm"
      :products="adminProducts"
      @advance-order="advanceOrder"
      @create-product="createProduct"
      @refresh-orders="refreshAdminOrders"
      @refresh-products="refreshAdminProducts"
      @toggle-sold-out="toggleSoldOut"
    />

    <ProductSpecModal
      v-if="sessionRole === 'customer' && activeProduct"
      :product="activeProduct"
      :spec-draft="specDraft"
      @add-to-cart="addToCart"
      @close="activeProduct = null"
      @select-spec="selectSpec"
    />
  </main>
</template>
