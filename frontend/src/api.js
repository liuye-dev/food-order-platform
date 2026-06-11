const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";


async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const payload = await response.json();

  if (!response.ok || payload.code !== 0) {
    throw new Error(payload.message || "请求失败");
  }

  return payload.data;
}


export const api = {
  login(data) {
    return request("/login/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  getCustomer(customerId) {
    return request(`/customers/${customerId}/`);
  },
  getCategories() {
    return request("/categories/");
  },
  getProducts(params = {}) {
    const search = new URLSearchParams(params);
    return request(`/products/?${search}`);
  },
  getCart(customerId) {
    return request(`/cart/items/?customer_id=${customerId}`);
  },
  addCartItem(data) {
    return request("/cart/items/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  updateCartItem(itemId, data) {
    return request(`/cart/items/${itemId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
  deleteCartItem(itemId) {
    return request(`/cart/items/${itemId}/`, {
      method: "DELETE",
    });
  },
  createOrder(data) {
    return request("/orders/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  payOrder(data) {
    return request("/payments/mock/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  getOrders(customerId) {
    return request(`/orders/?customer_id=${customerId}`);
  },
  createReview(orderId, data) {
    return request(`/orders/${orderId}/review/`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  getAdminProducts() {
    return request("/admin/products/");
  },
  createProduct(data) {
    return request("/admin/products/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
  updateProduct(productId, data) {
    return request(`/admin/products/${productId}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },
  setProductSoldOut(productId, isSoldOut) {
    return request(`/admin/products/${productId}/sold-out/`, {
      method: "PATCH",
      body: JSON.stringify({ is_sold_out: isSoldOut }),
    });
  },
  getAdminOrders() {
    return request("/admin/orders/");
  },
  updateOrderStatus(orderId, nextStatus) {
    return request(`/admin/orders/${orderId}/status/`, {
      method: "PATCH",
      body: JSON.stringify({ status: nextStatus }),
    });
  },
};
