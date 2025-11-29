<template>
  <header class="bg-white shadow-md sticky top-0 z-[100]">
    <div class="max-w-7xl mx-auto px-5">
      <div class="flex items-center justify-between py-5 gap-8 flex-wrap md:flex-nowrap">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2.5 no-underline text-gray-800 font-bold text-2xl whitespace-nowrap cursor-pointer">
          <span class="text-4xl">🔨</span>
          <span class="bg-gradient-to-r from-[#3555e4] to-[#64b5f6] bg-clip-text text-transparent">
            Gvozdara Shop
          </span>
        </router-link>

        <!-- Search Bar -->
        <div class="flex-1 max-w-[600px] flex gap-2.5 w-full md:w-auto order-3 md:order-2">
          <input 
            type="text" 
            v-model="searchQuery"
            @input="$emit('search', searchQuery)"
            placeholder="Pretraži proizvode..."
            class="flex-1 px-5 py-3 border-2 border-gray-200 rounded-full text-base transition-colors focus:outline-none focus:border-[#667eea]"
          />
          <button class="px-5 py-3 bg-gradient-to-r from-[#3555e4] to-[#64b5f6] text-white border-0 rounded-full cursor-pointer text-lg">
            🔍
          </button>
        </div>

        <!-- Actions -->
        <div class="flex gap-4 items-center order-2 md:order-3">
          <router-link to="/cart" class="relative p-3 bg-gray-100 rounded-full w-[50px] h-[50px] flex items-center justify-center no-underline transition-colors hover:bg-gray-200 cursor-pointer">
            <span class="text-2xl">🛒</span>
            <span v-if="cartCount > 0" class="absolute -top-1 -right-1 bg-[#e74c3c] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
              {{ cartCount }}
            </span>
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  cartCount: {
    type: Number,
    default: 0
  }
})

defineEmits(['search'])

const searchQuery = ref('')
</script>