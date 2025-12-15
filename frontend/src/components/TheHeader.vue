<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/store/cart'
import { useAuthStore } from '@/store/auth'
import { getImageUrl } from '@/composables/useImageUrl'

const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const mobileMenuOpen = ref(false)
const showCartPreview = ref(false)

const cartItemCount = computed(() => cartStore.itemCount)
const cartItems = computed(() => cartStore.items)
const cartTotal = computed(() => cartStore.total)
const isAdmin = computed(() => authStore.isAdmin)

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

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white sticky top-0 z-50 shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16 lg:h-18">

        <!-- Logo -->
        <div class="flex items-center gap-3 lg:gap-4 cursor-pointer" @click="navigateTo('/')">
          <img src="/betapack-logo.png" alt="Beta Pack Logo" class="h-10 lg:h-12 w-auto" />
          <div class="text-base lg:text-lg font-bold text-white">
            BETA PACK
          </div>
        </div>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex items-center gap-3 lg:gap-4">
          <button
            @click="navigateTo('/')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-3 lg:px-4 py-1.5 lg:py-2 rounded-lg transition font-semibold text-sm lg:text-base cursor-pointer"
          >
            Prodavnica
          </button>
          <button
            @click="navigateTo('/o-nama')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-3 lg:px-4 py-1.5 lg:py-2 rounded-lg transition font-semibold text-sm lg:text-base cursor-pointer"
          >
            O nama
          </button>
          <button
            @click="navigateTo('/kontakt')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-3 lg:px-4 py-1.5 lg:py-2 rounded-lg transition font-semibold text-sm lg:text-base cursor-pointer"
          >
            Kontakt
          </button>
        </nav>

        <!-- Cart & Actions -->
        <div class="flex items-center gap-4">
          <!-- Admin Link (only for admin users) -->
          <button
            v-if="isAdmin"
            @click="navigateTo('/admin')"
            class="hidden md:flex items-center gap-1 bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded-lg transition font-semibold text-xs cursor-pointer border border-gray-600 hover:border-gray-500"
          >
            <span class="text-sm">⚙️</span>
            <span>Admin</span>
          </button>

          <!-- Logout Button (only for logged in users) -->
          <button
            v-if="authStore.isAuthenticated"
            @click="handleLogout"
            class="hidden md:flex items-center gap-1 bg-red-600 hover:bg-red-700 px-2 py-1 rounded-lg transition font-semibold text-xs cursor-pointer"
          >
            <span class="text-sm">🚪</span>
            <span>Logout</span>
          </button>

          <!-- Cart with hover preview -->
          <div
            class="relative"
            @mouseenter="showCartPreview = true"
            @mouseleave="showCartPreview = false"
          >
            <button
              @click="navigateTo('/cart')"
              class="relative flex items-center gap-1 bg-[#1976d2] hover:bg-[#1565c0] px-2 py-1 rounded-lg transition font-semibold text-xs cursor-pointer"
            >
              <span class="text-lg">🛒</span>
              <span class="hidden sm:inline">Korpa</span>
              <span
                v-if="cartItemCount > 0"
                class="absolute -top-1.5 -right-1.5 bg-red-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center"
              >
                {{ cartItemCount }}
              </span>
            </button>

            <!-- Cart Preview Dropdown -->
            <Transition name="fade-slide">
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
                        :src="getImageUrl(item.images[0].image)"
                        :alt="item.name"
                        class="w-full h-full object-contain"
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
            </Transition>

            <!-- Empty Cart Preview -->
            <Transition name="fade-slide">
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
            </Transition>
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
        <!-- Admin Link (Mobile) -->
        <button
          v-if="isAdmin"
          @click="navigateTo('/admin')"
          class="block w-full text-left text-gray-300 hover:text-white hover:bg-white/10 px-4 py-3 rounded-lg transition font-semibold text-base cursor-pointer border-t border-gray-700 mt-2"
        >
          ⚙️ Admin Panel
        </button>
        <!-- Logout Button (Mobile) -->
        <button
          v-if="authStore.isAuthenticated"
          @click="handleLogout"
          class="block w-full text-left text-red-400 hover:text-white hover:bg-red-600/20 px-4 py-3 rounded-lg transition font-semibold text-base cursor-pointer border-t border-gray-700"
        >
          🚪 Logout
        </button>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.fade-slide-enter-active {
  transition: all 0.2s ease-out;
}

.fade-slide-leave-active {
  transition: all 0.15s ease-in;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
