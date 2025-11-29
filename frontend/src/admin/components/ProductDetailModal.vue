<script setup>
import { ref, computed } from 'vue'
import ProductVariantManager from './ProductVariantManager.vue'
import ProductImageManager from './ProductImageManager.vue'

const props = defineProps({
  product: Object,
  show: Boolean
})

const emit = defineEmits(['close', 'updated'])

const activeTab = ref('variants')

const tabs = [
  { id: 'variants', label: 'Varijante' },
  { id: 'images', label: 'Slike' }
]

const close = () => {
  emit('close')
}

const handleUpdate = () => {
  emit('updated')
}
</script>

<template>
  <Transition name="modal">
    <div
      v-if="show && product"
      @click.self="close"
      class="fixed inset-0 bg-black/50 backdrop-blur-md flex justify-center items-center p-4 z-[1500]"
    >
      <div class="bg-white rounded-lg w-full max-w-[550px] h-[90vh] shadow-xl overflow-hidden flex flex-col transform transition-all">
      
      <!-- Header -->
      <div class="px-6 py-5 bg-gradient-to-r from-blue-600 via-blue-500 to-blue-600 flex justify-between items-center shadow-md">
        <div>
          <h2 class="text-base font-bold text-white mb-2">{{ product.name }}</h2>
          <p class="text-sm opacity-90 text-white">{{ product.category_name }}</p>
        </div>
        <button 
          @click="close" 
          class="text-white text-2xl leading-none hover:scale-110 transition-all duration-200 cursor-pointer w-7 h-7 flex items-center justify-center rounded-full hover:bg-white/20"
        >
          &times;
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex border-b bg-gray-50 shadow-sm">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="activeTab === tab.id
            ? 'bg-white text-blue-600 border-b-2 border-blue-600 shadow-sm'
            : 'text-gray-600 hover:bg-gray-100'"
          class="px-6 py-3 font-semibold text-sm transition-all duration-200 cursor-pointer relative"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6">
        <ProductVariantManager
          v-if="activeTab === 'variants' && product && product.id"
          :product-id="Number(product.id)"
          @updated="handleUpdate"
        />

        <ProductImageManager
          v-if="activeTab === 'images' && product && product.id"
          :product-id="Number(product.id)"
          @updated="handleUpdate"
        />
      </div>

      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.9) translateY(-20px);
  opacity: 0;
}

.modal-enter-to > div,
.modal-leave-from > div {
  transform: scale(1) translateY(0);
  opacity: 1;
}
</style>
