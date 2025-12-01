<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { useProductStore } from '@/store/products'
import { useCategoryStore } from '@/store/categories'
import { useCartStore } from '@/store/cart'
import { getImageUrl } from '@/composables/useImageUrl'

const router = useRouter()
const productStore = useProductStore()
const categoryStore = useCategoryStore()
const cartStore = useCartStore()

// Carousel state
const carouselIndex = ref(0)
const carouselContainer = ref(null)

// Filters
const selectedCategory = ref(null)
const searchQuery = ref('')
const showOnlyOnSale = ref(false)

const formatPrice = (price) => {
  return new Intl.NumberFormat('sr-RS', {
    style: 'currency',
    currency: 'RSD',
    minimumFractionDigits: 0
  }).format(price)
}

const salePercent = (oldPrice, newPrice) => {
  return Math.round(((oldPrice - newPrice) / oldPrice) * 100)
}

const filteredProducts = computed(() => {
  let products = productStore.products || []

  // Filter by category
  if (selectedCategory.value) {
    products = products.filter(p => p.category === selectedCategory.value)
  }

  // Filter by search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    products = products.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.description.toLowerCase().includes(query)
    )
  }

  // Filter by on_sale - include products with sale variants
  if (showOnlyOnSale.value) {
    products = products.filter(p => p.on_sale || p.has_sale_variants)
  }

  return products
})

// Helper function to get primary image or first image
const getProductImage = (product) => {
  if (!product.images || product.images.length === 0) return null
  // Try to find primary image first
  const primaryImage = product.images.find(img => img.is_primary)
  if (primaryImage) return primaryImage
  // Otherwise return first image
  return product.images[0]
}

const featuredProducts = computed(() => {
  return (productStore.products || []).filter(p => p.featured)
})

// Carousel slides (4 products per slide, 2 rows)
const carouselSlides = computed(() => {
  const products = featuredProducts.value
  const slides = []
  const itemsPerSlide = 4
  
  for (let i = 0; i < products.length; i += itemsPerSlide) {
    slides.push(products.slice(i, i + itemsPerSlide))
  }
  
  return slides
})

const nextSlide = () => {
  if (carouselIndex.value < carouselSlides.value.length - 1) {
    carouselIndex.value++
  }
}

const prevSlide = () => {
  if (carouselIndex.value > 0) {
    carouselIndex.value--
  }
}

const viewProductDetail = (productId) => {
  router.push(`/proizvod/${productId}`)
}

// Product quantities (key = product.id, value = quantity)
const productQuantities = ref({})

// Selected variants per product (key = product.id, value = variant or null)
const selectedVariants = ref({})

// Get quantity for a product (default 1)
const getQuantity = (productId) => {
  return productQuantities.value[productId] || 1
}

// Set quantity for a product
const setQuantity = (productId, quantity) => {
  if (quantity < 1) quantity = 1
  productQuantities.value[productId] = quantity
}

// Get selected variant for a product
const getSelectedVariant = (product) => {
  // If already selected, return it
  if (selectedVariants.value[product.id]) {
    return selectedVariants.value[product.id]
  }
  // Otherwise, auto-select variant
  if (product.variants && product.variants.length > 0) {
    let variantToSelect = null
    
    // If filter "Samo na akciji" is active, try to find a variant on sale
    if (showOnlyOnSale.value) {
      variantToSelect = product.variants.find(v => v.on_sale) || product.variants[0]
    } else {
      // Otherwise, select first variant
      variantToSelect = product.variants[0]
    }
    
    selectedVariants.value[product.id] = variantToSelect
    return variantToSelect
  }
  return null
}

// Set selected variant for a product
const setSelectedVariant = (productId, variant) => {
  selectedVariants.value[productId] = variant
  // Reset quantity to 1 when variant changes
  setQuantity(productId, 1)
}

// Get price for a product (considering selected variant)
const getProductPrice = (product) => {
  const variant = getSelectedVariant(product)
  if (variant) {
    return parseFloat(variant.current_price || variant.price)
  }
  return parseFloat(product.current_price) || 0
}

// Check if selected variant is on sale
const isVariantOnSale = (product) => {
  const variant = getSelectedVariant(product)
  if (variant) {
    return variant.on_sale
  }
  return product.on_sale
}

// Get original price of selected variant (before sale)
const getVariantOriginalPrice = (product) => {
  const variant = getSelectedVariant(product)
  if (variant) {
    return parseFloat(variant.price)
  }
  return parseFloat(product.price)
}

// Add product to cart directly from card
const addToCartFromCard = (product) => {
  const quantity = getQuantity(product.id)
  const variant = getSelectedVariant(product)

  const productToAdd = {
    ...product,
    selectedVariant: variant
  }

  cartStore.add(productToAdd, quantity)
  // Don't redirect - stay on shop page so user can add more variants
  // Reset quantity to 1 after adding
  setQuantity(product.id, 1)
}

// Watch for changes in showOnlyOnSale filter and reset selected variants
watch(showOnlyOnSale, () => {
  // Reset all selected variants so they will be re-selected with the new logic
  selectedVariants.value = {}
})

// Watch for changes in category or search to reset variants
watch([selectedCategory, searchQuery], () => {
  // Reset all selected variants when filters change
  selectedVariants.value = {}
})

// Watch for changes in filtered products and reset variants for products that are no longer visible
watch(filteredProducts, () => {
  // Remove selected variants for products that are no longer in the filtered list
  const visibleProductIds = new Set(filteredProducts.value.map(p => p.id))
  Object.keys(selectedVariants.value).forEach(productId => {
    if (!visibleProductIds.has(parseInt(productId))) {
      delete selectedVariants.value[productId]
    }
  })
}, { deep: true })

onMounted(async () => {
  await categoryStore.fetchCategories()
  await productStore.fetchProducts()
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1">

      <!-- Hero Image -->
      <div class="relative overflow-hidden" style="height: 450px;">
        <!-- Background Image -->
        <img
          src="/Betapack-hero-image-edited-2.png"
          alt="BetaPack - Kovano gvožđe i bravarijski proizvodi"
          class="absolute inset-0 w-full h-full object-cover"
        />

        <!-- Text Overlay -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="text-center text-white px-6 py-8 max-w-4xl rounded-xl" style="background-color: rgba(0, 0, 0, 0.65); backdrop-filter: blur(4px);">
            <h1 class="text-3xl lg:text-5xl xl:text-6xl font-bold mb-4 uppercase" style="text-shadow: 2px 2px 8px rgba(0,0,0,0.9);">
              Kovano gvožđe i bravarijski proizvodi
            </h1>
            <p class="text-base lg:text-xl text-white" style="text-shadow: 2px 2px 6px rgba(0,0,0,0.9);">
              Širok asortiman kvalitetnih proizvoda - profili, ograde, ukrasni elementi i mnogo više
            </p>
          </div>
        </div>

        <!-- Buttons positioned at bottom -->
        <div class="absolute inset-0 flex items-end justify-center pb-12">
          <div class="flex gap-3 px-4">
            <a
              href="#products"
              class="bg-white hover:bg-gray-100 text-gray-900 font-semibold px-6 py-3 rounded-lg transition cursor-pointer shadow-lg text-sm lg:text-base"
            >
              Pogledaj katalog
            </a>
            <router-link
              to="/kontakt"
              class="bg-[#1976d2] hover:bg-[#1565c0] text-white font-semibold px-6 py-3 rounded-lg transition cursor-pointer shadow-lg text-sm lg:text-base"
            >
              Kontaktiraj nas
            </router-link>
          </div>
        </div>
      </div>

      <!-- Recommended Products with Carousel -->
      <div v-if="featuredProducts.length > 0" class="bg-gradient-to-b from-gray-50 to-white py-10 border-y-2 border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-6">
            <h2 class="text-xl lg:text-2xl font-bold text-gray-900 mb-2">Preporučujemo</h2>
            <p class="text-sm lg:text-base text-gray-600">Naši najpopularniji proizvodi</p>
          </div>

          <!-- Carousel Container -->
          <div class="relative">
            <!-- Carousel Wrapper -->
            <div class="overflow-hidden">
              <div
                ref="carouselContainer"
                class="flex transition-transform duration-300 ease-in-out"
                :style="{ transform: `translateX(-${carouselIndex * 100}%)` }"
              >
                <!-- Carousel Slide (2 rows, 4 columns per slide) -->
                <div
                  v-for="(slide, slideIndex) in carouselSlides"
                  :key="slideIndex"
                  class="min-w-full"
                >
                  <div class="grid grid-cols-2 lg:grid-cols-4 gap-6">
                    <div
                      v-for="product in slide"
                      :key="product.id"
                      @click="viewProductDetail(product.id)"
                      class="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-xl transition cursor-pointer group"
                    >
                      <div class="relative h-48 bg-gray-100 overflow-hidden">
                        <img
                          v-if="getProductImage(product)"
                          :src="getImageUrl(getProductImage(product).image)"
                          :alt="product.name"
                          class="w-full h-full object-contain group-hover:scale-105 transition duration-300"
                        />
                        <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                          <span class="text-4xl">📦</span>
                        </div>

                        <div v-if="product.on_sale" class="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                          -{{ salePercent(product.price, product.sale_price) }}%
                        </div>
                      </div>

                      <div class="p-6">
                        <p class="text-sm text-[#1565c0] font-bold mb-2 uppercase tracking-wide">{{ product.category_name }}</p>
                        <h3 class="font-bold text-gray-900 mb-3 text-lg line-clamp-1">{{ product.name }}</h3>

                        <div class="flex items-center justify-between mt-3">
                          <div>
                            <p v-if="product.on_sale || (product.has_sale_variants)" class="text-base text-gray-400 line-through mb-1">
                              {{ formatPrice(product.price) }}
                            </p>
                            <p class="text-xl font-bold" :class="(product.on_sale || product.has_sale_variants) ? 'text-red-600' : 'text-green-700'">
                              <span v-if="product.variants && product.variants.length > 0" class="text-sm text-gray-500">od </span>
                              {{ formatPrice(product.min_price || product.current_price) }}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Navigation Buttons -->
            <button
              v-if="carouselSlides.length > 1"
              @click="prevSlide"
              :disabled="carouselIndex === 0"
              class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 bg-white rounded-full p-3 shadow-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer z-10"
            >
              <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <button
              v-if="carouselSlides.length > 1"
              @click="nextSlide"
              :disabled="carouselIndex >= carouselSlides.length - 1"
              class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 bg-white rounded-full p-3 shadow-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer z-10"
            >
              <svg class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Carousel Indicators -->
          <div v-if="carouselSlides.length > 1" class="flex justify-center gap-2 mt-6">
            <button
              v-for="(slide, index) in carouselSlides"
              :key="index"
              @click="carouselIndex = index"
              :class="carouselIndex === index ? 'bg-[#1976d2]' : 'bg-gray-300'"
              class="w-2 h-2 rounded-full transition cursor-pointer"
            />
          </div>
        </div>
      </div>

      <!-- Products Section -->
      <div id="products" class="py-8 bg-white">
        <div class="min-w-[90vw] max-w-[95vw] mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid grid-cols-1 lg:grid-cols-5 gap-4 lg:gap-6">

            <!-- Sidebar -->
            <aside class="lg:col-span-1">
              <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-4 sticky top-20">
                <h3 class="font-bold text-base lg:text-lg mb-4 text-gray-900 border-b border-gray-200 pb-2">Filteri</h3>

                <!-- Search -->
                <div class="mb-4">
                  <label class="block text-xs lg:text-sm font-bold text-gray-700 mb-1">Pretraga</label>
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Pretraži proizvode..."
                    class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-1 focus:ring-[#1976d2] focus:border-[#1976d2] transition"
                  />
                </div>

                <!-- Categories -->
                <div class="mb-4">
                  <h4 class="font-bold text-sm lg:text-base text-gray-800 mb-2">Kategorije</h4>

                  <button
                    @click="selectedCategory = null"
                    :class="selectedCategory === null ? 'bg-gradient-to-r from-[#1976d2] to-[#1565c0] text-white font-semibold shadow-md' : 'text-gray-700 hover:bg-gray-100'"
                    class="w-full text-left px-3 py-2 text-sm rounded-lg transition mb-1 cursor-pointer font-semibold"
                  >
                    Sve kategorije
                  </button>

                  <button
                    v-for="cat in categoryStore.categories"
                    :key="cat.id"
                    @click="selectedCategory = cat.id"
                    :class="selectedCategory === cat.id ? 'bg-gradient-to-r from-[#1976d2] to-[#1565c0] text-white font-semibold shadow-md' : 'text-gray-700 hover:bg-gray-100'"
                    class="w-full text-left px-3 py-2 text-sm rounded-lg transition mb-1 cursor-pointer font-semibold"
                  >
                    {{ cat.name }}
                  </button>
                </div>

                <!-- On Sale Filter -->
                <div class="pt-3 border-t border-gray-200">
                  <label class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 px-2 py-2 rounded-lg transition">
                    <input
                      v-model="showOnlyOnSale"
                      type="checkbox"
                      class="w-4 h-4 text-[#1565c0] rounded focus:ring-[#1976d2] cursor-pointer"
                    />
                    <span class="text-sm font-semibold text-gray-700 cursor-pointer">Samo na akciji</span>
                  </label>
                </div>
              </div>
            </aside>

            <!-- Products Grid -->
            <div class="lg:col-span-4">
              <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-3 border-b border-gray-200">
                <h2 class="text-lg lg:text-xl font-bold text-gray-900">
                  {{ selectedCategory ? categoryStore.categories.find(c => c.id === selectedCategory)?.name : 'Svi proizvodi' }}
                </h2>
                <p class="text-sm lg:text-base font-bold text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg">{{ filteredProducts.length }} proizvoda</p>
              </div>

              <!-- Loading -->
              <div v-if="productStore.loading" class="text-center py-10">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#1565c0]"></div>
                <p class="text-sm text-gray-600 mt-2">Učitavanje proizvoda...</p>
              </div>

              <!-- Products Grid -->
              <div
                v-else-if="filteredProducts.length > 0"
                class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6"
              >
                <div
                  v-for="product in filteredProducts"
                  :key="product.id"
                  class="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg hover:border-[#1976d2] transition-all duration-300 group flex flex-col h-full"
                >
                  <div
                    @click="viewProductDetail(product.id)"
                    class="cursor-pointer flex-1 flex flex-col"
                  >
                    <div class="relative h-40 lg:h-48 bg-gray-100 overflow-hidden flex-shrink-0">
                      <img
                        v-if="getProductImage(product)"
                        :src="getImageUrl(getProductImage(product).image)"
                        :alt="product.name"
                        class="w-full h-full object-contain group-hover:scale-105 transition duration-300"
                      />
                      <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                        <span class="text-2xl">📦</span>
                      </div>

                      <div v-if="product.on_sale" class="absolute top-1 right-1 bg-red-500 text-white px-2 py-0.5 rounded-full text-xs font-bold shadow">
                        -{{ salePercent(product.price, product.sale_price) }}%
                      </div>
                    </div>

                    <div class="p-3 flex-1 flex flex-col">
                      <p class="text-xs text-[#1565c0] font-bold mb-1 uppercase tracking-wide">{{ product.category_name }}</p>
                      <h3 class="font-bold text-gray-900 mb-1 text-sm line-clamp-2">{{ product.name }}</h3>
                      <p class="text-xs text-gray-600 mb-2 line-clamp-2 leading-relaxed">{{ product.description }}</p>

                      <div class="mt-auto">
                        <div class="flex items-center justify-between mb-2">
                          <div>
                            <p v-if="isVariantOnSale(product)" class="text-xs text-gray-400 line-through mb-0.5">
                              {{ formatPrice(getVariantOriginalPrice(product)) }}
                            </p>
                            <p class="text-base font-bold" :class="isVariantOnSale(product) ? 'text-red-600' : 'text-green-700'">
                              {{ formatPrice(getProductPrice(product)) }}
                            </p>
                          </div>
                        </div>

                        <!-- Variant Dropdown -->
                        <div v-if="product.variants && product.variants.length > 0" class="mb-2" @click.stop>
                          <label class="block text-xs font-bold text-gray-700 mb-1">Dimenzija:</label>
                          <select
                            :value="getSelectedVariant(product)?.id"
                            @change="setSelectedVariant(product.id, product.variants.find(v => v.id == $event.target.value))"
                            class="w-full border border-gray-300 rounded-lg px-2 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm 
                                   focus:ring-2 focus:ring-[#1976d2] focus:border-[#1976d2] cursor-pointer font-semibold
                                   hover:border-gray-400 transition-all shadow-sm bg-white"
                          >
                            <option
                              v-for="variant in product.variants"
                              :key="variant.id"
                              :value="variant.id"
                            >
                              {{ variant.name }}
                            </option>
                          </select>
                        </div>

                        <!-- Quantity Selector -->
                        <div class="flex items-center gap-2 mb-2" @click.stop>
                          <span class="text-xs font-bold text-gray-700">Količina:</span>
                          <div class="flex items-center gap-2 bg-gray-100 rounded-xl p-1">
                            <button
                              @click="setQuantity(product.id, getQuantity(product.id) - 1)"
                              class="w-8 h-8 bg-white rounded-lg hover:bg-gray-200 transition text-base font-bold cursor-pointer shadow-sm"
                            >
                              -
                            </button>
                            <span class="w-10 text-center text-base font-bold text-gray-900">{{ getQuantity(product.id) }}</span>
                            <button
                              @click="setQuantity(product.id, getQuantity(product.id) + 1)"
                              class="w-8 h-8 bg-white rounded-lg hover:bg-gray-200 transition text-base font-bold cursor-pointer shadow-sm"
                            >
                              +
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="px-5 lg:px-6 pb-5 lg:pb-6 flex-shrink-0">
                    <button
                      @click.stop="addToCartFromCard(product)"
                      :disabled="cartStore.isInCart(product.id, getSelectedVariant(product)?.id)"
                      class="w-full bg-gradient-to-r from-[#1976d2] to-[#1565c0] hover:from-[#1565c0] hover:to-[#0d47a1] text-white font-bold py-3 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-lg hover:shadow-xl text-sm lg:text-base"
                    >
                      {{ cartStore.isInCart(product.id, getSelectedVariant(product)?.id) ? '✓ Već u korpi' : '+ Dodaj u korpu' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-else class="text-center py-10">
                <span class="text-3xl text-gray-300 mb-3 block">🔍</span>
                <p class="text-xl text-gray-600 mb-4">Nema proizvoda koji odgovaraju filterima</p>
                <button
                  @click="selectedCategory = null; searchQuery = ''; showOnlyOnSale = false"
                  class="mt-4 text-lg text-[#1565c0] hover:underline cursor-pointer font-semibold"
                >
                  Resetuj filtere
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>

    </main>

    <TheFooter />
  </div>
</template>
