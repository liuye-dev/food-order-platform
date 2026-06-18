<script setup>
import { reactive, ref } from "vue";
import { LogIn, Store, UserRound } from "lucide-vue-next";


defineProps({
  error: { type: String, default: "" },
  loading: { type: Boolean, default: false },
  message: { type: String, default: "" },
});

const emit = defineEmits(["admin-login", "customer-login"]);

const selectedRole = ref("customer");
const customerForm = reactive({
  phone: "",
  code: "",
});
const adminForm = reactive({
  username: "",
  password: "",
});

function submit() {
  if (selectedRole.value === "customer") {
    emit("customer-login", { ...customerForm });
    return;
  }

  emit("admin-login", { ...adminForm });
}
</script>

<template>
  <main class="login-page">
    <section class="login-card">
      <div class="login-heading">
        <h1>在线点餐平台</h1>
      </div>

      <div class="login-role-tabs" aria-label="登录角色">
        <button :class="{ active: selectedRole === 'customer' }" @click="selectedRole = 'customer'">
          <UserRound :size="18" />
          顾客登录
        </button>
        <button :class="{ active: selectedRole === 'admin' }" @click="selectedRole = 'admin'">
          <Store :size="18" />
          商家登录
        </button>
      </div>

      <div v-if="message" class="notice success">{{ message }}</div>
      <div v-if="error" class="notice error">{{ error }}</div>

      <form class="login-form" @submit.prevent="submit">
        <template v-if="selectedRole === 'customer'">
          <label>
            手机号
            <input v-model="customerForm.phone" maxlength="11" />
          </label>
          <label>
            验证码
            <input v-model="customerForm.code" maxlength="6" />
          </label>
        </template>

        <template v-else>
          <label>
            商家账号
            <input v-model="adminForm.username" />
          </label>
          <label>
            密码
            <input v-model="adminForm.password" type="password" />
          </label>
        </template>

        <button class="primary-btn" :disabled="loading" type="submit">
          <LogIn :size="18" />
          进入{{ selectedRole === "customer" ? "顾客端" : "商家端" }}
        </button>
      </form>
    </section>
  </main>
</template>
