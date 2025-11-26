<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'

const router = useRouter()
const cartStore = useCartStore()

const mobileMenuOpen = ref(false)
const showCartPreview = ref(false)

const cartItemCount = computed(() => cartStore.itemCount)
const cartItems = computed(() => cartStore.items)
const cartTotal = computed(() => cartStore.total)

const formatPrice = (price) => {
  return new Intl.NumberFormat('sr-RS', {
    style: 'currency',
    currency: 'RSD',
    minimumFractionDigits: 0
  }).format(price)
}

const navigateTo = (route) => {
  router.push(route)
  mobileMenuOpen.value = false
  showCartPreview.value = false
}

const updateQuantity = (item, newQuantity) => {
  if (newQuantity < 1) return
  cartStore.updateQuantity(item.cartId || item.id, newQuantity)
}

const removeItem = (item) => {
  cartStore.remove(item.cartId || item.id)
}
</script>

<template>
  <header class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white sticky top-0 z-50 shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-20 lg:h-24">

        <!-- Logo -->
        <div class="flex items-center gap-3 lg:gap-4 cursor-pointer" @click="navigateTo('/')">
          <img src="/logo.png" alt="Beta Pack Logo" class="h-14 lg:h-16 w-auto" />
          <div class="text-xl lg:text-2xl font-bold text-white">
            BETA PACK
          </div>
        </div>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex items-center gap-6 lg:gap-8">
          <button
            @click="navigateTo('/')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-4 lg:px-5 py-2 lg:py-2.5 rounded-lg transition font-semibold text-base lg:text-lg cursor-pointer"
          >
            Prodavnica
          </button>
          <button
            @click="navigateTo('/o-nama')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-4 lg:px-5 py-2 lg:py-2.5 rounded-lg transition font-semibold text-base lg:text-lg cursor-pointer"
          >
            O nama
          </button>
          <button
            @click="navigateTo('/kontakt')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-4 lg:px-5 py-2 lg:py-2.5 rounded-lg transition font-semibold text-base lg:text-lg cursor-pointer"
          >
            Kontakt
          </button>
        </nav>

        <!-- Cart & Actions -->
        <div class="flex items-center gap-4">
          <!-- Cart with hover preview -->
          <div 
            class="relative"
            @mouseenter="showCartPreview = true"
            @mouseleave="showCartPreview = false"
          >
            <button
              @click="navigateTo('/cart')"
              class="relative flex items-center gap-2 bg-[#1976d2] hover:bg-[#1565c0] px-5 lg:px-6 py-2.5 lg:py-3 rounded-lg transition font-semibold text-base lg:text-lg cursor-pointer"
            >
              <span class="text-xl lg:text-2xl">🛒</span>
              <span class="hidden sm:inline">Korpa</span>
              <span
                v-if="cartItemCount > 0"
                class="absolute -top-2 -right-2 bg-red-600 text-white text-xs lg:text-sm font-bold w-6 h-6 lg:w-7 lg:h-7 rounded-full flex items-center justify-center"
              >
                {{ cartItemCount }}
              </span>
            </button>

            <!-- Cart Preview Dropdown -->
            <div
              v-if="showCartPreview && cartItems.length > 0"
              class="absolute right-0 top-full pt-1 w-96 bg-transparent z-[100]"
              @mouseenter="showCartPreview = true"
              @mouseleave="showCartPreview = false"
            >
              <div class="bg-white rounded-xl shadow-2xl border border-gray-200 max-h-[600px] overflow-hidden flex flex-col">
                <!-- Header -->
                <div class="p-4 border-b bg-gray-50">
                  <h3 class="font-bold text-lg text-gray-900">Korpa ({{ cartItemCount }})</h3>
                </div>

                <!-- Items List -->
                <div class="flex-1 overflow-y-auto p-4 space-y-3">
                  <div
                    v-for="item in cartItems"
                    :key="item.cartId || item.id"
                    class="flex gap-3 pb-3 border-b last:border-0"
                  >
                    <!-- Image -->
                    <div class="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                      <img
                        v-if="item.images && item.images.length > 0"
                        :src="`http://localhost:8000${item.images[0].image}`"
                        :alt="item.name"
                        class="w-full h-full object-cover"
                      />
                      <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                        <span class="text-2xl">📦</span>
                      </div>
                    </div>

                    <!-- Info -->
                    <div class="flex-1 min-w-0">
                      <h4 class="font-semibold text-sm text-gray-900 line-clamp-1">{{ item.name }}</h4>
                      <p v-if="item.selectedVariant" class="text-xs text-gray-600">
                        {{ item.selectedVariant.name }}
                      </p>
                      <p class="text-sm font-bold text-green-700 mt-1">{{ formatPrice(item.current_price) }}</p>

                      <!-- Quantity Controls -->
                      <div class="flex items-center gap-2 mt-2">
                        <button
                          @click.stop="updateQuantity(item, item.quantity - 1)"
                          class="w-6 h-6 bg-gray-200 hover:bg-gray-300 rounded text-xs font-semibold cursor-pointer"
                        >
                          -
                        </button>
                        <span class="text-sm font-semibold text-gray-900 w-6 text-center">{{ item.quantity }}</span>
                        <button
                          @click.stop="updateQuantity(item, item.quantity + 1)"
                          class="w-6 h-6 bg-gray-200 hover:bg-gray-300 rounded text-xs font-semibold cursor-pointer"
                        >
                          +
                        </button>
                        <button
                          @click.stop="removeItem(item)"
                          class="ml-auto text-red-600 hover:text-red-700 text-xs font-semibold cursor-pointer"
                        >
                          Ukloni
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Footer -->
                <div class="p-4 border-t bg-gray-50 space-y-3">
                  <div class="flex justify-between items-center">
                    <span class="font-bold text-gray-900">Ukupno:</span>
                    <span class="text-xl font-bold text-green-700">{{ formatPrice(cartTotal) }}</span>
                  </div>
                  <button
                    @click="navigateTo('/cart')"
                    class="w-full bg-[#1976d2] hover:bg-[#1565c0] text-white font-semibold py-2.5 rounded-lg transition cursor-pointer"
                  >
                    Pogledaj korpu
                  </button>
                </div>
              </div>
            </div>

            <!-- Empty Cart Preview -->
            <div
              v-if="showCartPreview && cartItems.length === 0"
              class="absolute right-0 top-full pt-1 w-80 bg-transparent z-[100]"
              @mouseenter="showCartPreview = true"
              @mouseleave="showCartPreview = false"
            >
              <div class="bg-white rounded-xl shadow-2xl border border-gray-200 p-6 text-center">
                <span class="text-5xl text-gray-300 mb-3 block">🛒</span>
                <p class="text-gray-600 font-medium">Korpa je prazna</p>
              </div>
            </div>
          </div>

          <!-- Mobile menu button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden text-gray-300 hover:text-white p-2 cursor-pointer"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                v-if="!mobileMenuOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <div
      v-if="mobileMenuOpen"
      class="md:hidden bg-gray-800 border-t border-gray-700"
    >
      <nav class="px-4 py-4 space-y-2">
        <button
          @click="navigateTo('/')"
          class="block w-full text-left text-gray-300 hover:text-white hover:bg-white/10 px-4 py-3 rounded-lg transition font-semibold text-base cursor-pointer"
        >
          Prodavnica
        </button>
        <button
          @click="navigateTo('/o-nama')"
          class="block w-full text-left text-gray-300 hover:text-white hover:bg-white/10 px-4 py-3 rounded-lg transition font-semibold text-base cursor-pointer"
        >
          O nama
        </button>
        <button
          @click="navigateTo('/kontakt')"
          class="block w-full text-left text-gray-300 hover:text-white hover:bg-white/10 px-4 py-3 rounded-lg transition font-semibold text-base cursor-pointer"
        >
          Kontakt
        </button>
      </nav>
    </div>
  </header>
</template>
