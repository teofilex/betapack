<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { useCartStore } from '@/store/cart'
import { api } from '@/services/api'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()

const product = ref(null)
const loading = ref(true)
const selectedVariant = ref(null)
const selectedImageIndex = ref(0)
const quantity = ref(1)

// Reset quantity to 1 when variant changes
watch(selectedVariant, () => {
  quantity.value = 1
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('sr-RS', {
    style: 'currency',
    currency: 'RSD',
    minimumFractionDigits: 0
  }).format(price)
}

const salePercent = computed(() => {
  if (!product.value || !product.value.on_sale) return 0
  return Math.round(((product.value.price - product.value.sale_price) / product.value.price) * 100)
})

const finalPrice = computed(() => {
  if (!product.value) return 0

  // If variant is selected, use variant's final_price
  if (selectedVariant.value && selectedVariant.value.final_price) {
    return parseFloat(selectedVariant.value.final_price)
  }

  // Otherwise use product's current_price
  return parseFloat(product.value.current_price) || 0
})

const images = computed(() => {
  if (!product.value || !product.value.images || product.value.images.length === 0) {
    return []
  }
  // Sort images: primary first, then by order
  return [...product.value.images].sort((a, b) => {
    if (a.is_primary && !b.is_primary) return -1
    if (!a.is_primary && b.is_primary) return 1
    return (a.order || 0) - (b.order || 0)
  })
})

const fetchProduct = async () => {
  loading.value = true
  try {
    const response = await api.get(`/products/${route.params.id}/`)
    product.value = response.data

    // Auto-select first variant if available
    if (product.value.variants && product.value.variants.length > 0) {
      selectedVariant.value = product.value.variants[0]
    }
  } catch (error) {
    console.error('Error fetching product:', error)
    router.push('/')
  } finally {
    loading.value = false
  }
}

const addToCart = () => {
  const cartItem = {
    ...product.value,
    selectedVariant: selectedVariant.value
  }
  cartStore.add(cartItem, quantity.value)

  // Reset quantity to 1 after adding
  quantity.value = 1
  // Don't redirect - stay on page so user can add more variants or change quantity
}

const selectImage = (index) => {
  selectedImageIndex.value = index
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  fetchProduct()
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <!-- Back Button -->
        <button
          @click="goBack"
          class="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition cursor-pointer"
        >
          <span>←</span>
          <span>Nazad na katalog</span>
        </button>

        <!-- Loading -->
        <div v-if="loading" class="text-center py-20">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#1565c0]"></div>
          <p class="text-gray-600 mt-4">Učitavanje proizvoda...</p>
        </div>

        <!-- Product Detail -->
        <div v-else-if="product" class="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8 lg:items-stretch">

            <!-- Gallery -->
            <div>
              <!-- Main Image -->
              <div class="relative bg-gray-100 rounded-xl overflow-hidden mb-4 aspect-square">
                <img
                  v-if="images.length > 0"
                  :src="`http://localhost:8000${images[selectedImageIndex].image}`"
                  :alt="product.name"
                  class="w-full h-full object-contain"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  <span class="text-8xl">📦</span>
                </div>

                <!-- Sale Badge -->
                <div v-if="product.on_sale" class="absolute top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-full font-bold shadow-lg">
                  -{{ salePercent }}%
                </div>
              </div>

              <!-- Thumbnails -->
              <div v-if="images.length > 1" class="grid grid-cols-4 gap-3">
                <button
                  v-for="(img, index) in images"
                  :key="img.id"
                  @click="selectImage(index)"
                  :class="selectedImageIndex === index ? 'ring-2 ring-[#1976d2]' : 'ring-1 ring-gray-200'"
                  class="aspect-square rounded-lg overflow-hidden hover:ring-2 hover:ring-[#1976d2] transition cursor-pointer bg-gray-100"
                >
                  <img
                    :src="`http://localhost:8000${img.image}`"
                    :alt="product.name"
                    class="w-full h-full object-contain"
                  />
                </button>
              </div>
            </div>

            <!-- Product Info -->
            <div class="flex flex-col min-h-[600px]">
              <!-- Category -->
              <p class="text-sm text-[#1976d2] font-semibold mb-2">{{ product.category_name }}</p>

              <!-- Title -->
              <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ product.name }}</h1>

              <!-- Price -->
              <div class="mb-6">
                <div v-if="product.on_sale" class="flex items-center gap-3">
                  <span class="text-2xl text-gray-400 line-through">{{ formatPrice(product.price) }}</span>
                  <span class="text-4xl font-bold text-red-600">{{ formatPrice(finalPrice) }}</span>
                </div>
                <div v-else>
                  <span class="text-4xl font-bold text-green-700">{{ formatPrice(finalPrice) }}</span>
                </div>
                <p class="text-sm text-gray-500 mt-2">Cena uključuje PDV</p>
              </div>

              <!-- Description -->
              <div class="mb-6">
                <h3 class="font-semibold text-gray-900 mb-2">Opis</h3>
                <p class="text-gray-700 leading-relaxed">{{ product.description }}</p>
              </div>

              <!-- Variants -->
              <div v-if="product.variants && product.variants.length > 0" class="mb-6">
                <h3 class="font-semibold text-gray-900 mb-3">Izaberite dimenziju</h3>
                <div class="grid grid-cols-2 gap-3">
                  <button
                    v-for="variant in product.variants"
                    :key="variant.id"
                    @click="selectedVariant = variant"
                    :class="[
                      selectedVariant?.id === variant.id
                        ? 'bg-[#1976d2] text-white ring-2 ring-[#1976d2]'
                        : 'bg-white text-gray-700 ring-1 ring-gray-300 hover:ring-[#1976d2]'
                    ]"
                    class="px-4 py-3 rounded-lg font-medium transition text-sm cursor-pointer"
                  >
                    <div>{{ variant.name }}</div>
                  </button>
                </div>
              </div>

              <!-- Quantity -->
              <div class="mb-6">
                <h3 class="font-semibold text-gray-900 mb-3">Količina</h3>
                <div class="flex items-center gap-3">
                  <button
                    @click="quantity = Math.max(1, quantity - 1)"
                    class="w-10 h-10 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition cursor-pointer"
                  >
                    -
                  </button>
                  <input
                    v-model.number="quantity"
                    type="number"
                    min="1"
                    class="w-20 text-center border border-gray-300 rounded-lg px-3 py-2 font-semibold"
                  />
                  <button
                    @click="quantity++"
                    class="w-10 h-10 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition cursor-pointer"
                  >
                    +
                  </button>
                </div>
              </div>

              <!-- Additional Info -->
              <div class="mb-6 pb-6 border-b space-y-3 text-sm text-gray-600">
                <div class="flex items-center gap-2">
                  <span>✓</span>
                  <span>Besplatna konsultacija</span>
                </div>
                <div class="flex items-center gap-2">
                  <span>✓</span>
                  <span>Mogućnost prilagođavanja po meri</span>
                </div>
                <div class="flex items-center gap-2">
                  <span>✓</span>
                  <span>Garancija kvaliteta</span>
                </div>
              </div>

              <!-- Spacer to push buttons to bottom -->
              <div class="flex-1"></div>

              <!-- Add to Cart - Fixed at Bottom -->
              <div class="space-y-3">
                <button
                  @click="addToCart"
                  class="w-full bg-[#1976d2] hover:bg-[#1565c0] text-white font-bold py-4 rounded-lg transition text-lg shadow-md hover:shadow-xl cursor-pointer transform hover:scale-[1.02]"
                >
                  🛒 Dodaj u korpu
                </button>
                
                <!-- Link to Cart/Checkout -->
                <router-link
                  to="/cart"
                  class="block w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-bold py-4 rounded-lg transition-all text-lg shadow-md hover:shadow-xl cursor-pointer transform hover:scale-[1.02] text-center"
                >
                  🛍️ Idi na korpu i naruči
                </router-link>

                <button
                  @click="router.push('/kontakt')"
                  class="w-full bg-white hover:bg-gray-50 text-gray-900 font-semibold py-4 rounded-lg border-2 border-gray-300 transition cursor-pointer"
                >
                  📞 Kontaktirajte nas za ponudu
                </button>
              </div>
            </div>

          </div>
        </div>

        <!-- Related Products (Optional - can be added later) -->

      </div>
    </main>

    <TheFooter />
  </div>
</template>
