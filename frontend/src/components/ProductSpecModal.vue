<script setup>
import { ShoppingCart } from "lucide-vue-next";


const props = defineProps({
  product: { type: Object, required: true },
  specDraft: { type: Object, required: true },
});

const emit = defineEmits(["add-to-cart", "close", "select-spec"]);

function specPrice() {
  let price = Number(props.product.base_price || 0);
  for (const group of props.product.specs?.groups || []) {
    const selected = props.specDraft[group.name];
    const selectedList = Array.isArray(selected) ? selected : [selected];
    for (const option of group.options || []) {
      if (selectedList.includes(option.name)) {
        price += Number(option.price_delta || 0);
      }
    }
  }
  return price.toFixed(2);
}
</script>

<template>
  <div class="modal-mask" @click.self="emit('close')">
    <section class="spec-modal">
      <img :src="product.image_url" :alt="product.name" />
      <div class="spec-content">
        <h2>{{ product.name }}</h2>
        <p>{{ product.description }}</p>
        <div v-for="group in product.specs?.groups || []" :key="group.name" class="spec-group">
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
              @click="emit('select-spec', group, option.name)"
            >
              {{ option.name }}
              <span v-if="option.price_delta">+￥{{ option.price_delta }}</span>
            </button>
          </div>
        </div>
        <div class="modal-footer">
          <strong>￥{{ specPrice() }}</strong>
          <button class="primary-btn" @click="emit('add-to-cart')">
            <ShoppingCart :size="18" />
            加入购物车
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
