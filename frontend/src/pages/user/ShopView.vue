<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useHead } from '@unhead/vue'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import ResponsivePicture from '@/components/ResponsivePicture.vue'
import { useProductStore } from '@/store/products'
import { useCategoryStore } from '@/store/categories'
import { useCartStore } from '@/store/cart'
import { getImageUrl } from '@/composables/useImageUrl'
import { useStore } from '@/composables/useStore'
import { getStoreById } from '@/config/stores'
import { buildHead, DEFAULT_OG_IMAGE } from '@/utils/seo'
import {
  getSellingMode, getQuantityStep, getMinQuantity, getDefaultQuantity, getPackageSize,
  isValidQuantity, isValidLengthQuantity, isOnRequest, isPackageMode,
  isLengthMode, isWeightMode, formatPriceLabel, getPackageNote
} from '@/composables/useSellingMode'
import {
  getAmbalazaDisplayPrice,
  formatAmbalazaPriceLabel,
  getAmbalazaSellingNote,
  getAmbalazaPackageNote,
  isAmbalazaOnRequest,
  isAmbalazaPackageMode,
  isAmbalazaWeightMode,
  isAmbalazaValidQuantity,
  getAmbalazaMinQuantity,
  getAmbalazaQuantityStep,
  getAmbalazaDefaultQuantity,
  getAmbalazaPackageSize
} from '@/composables/useAmbalazaSelling'

const router = useRouter()
const route = useRoute()
const { storeId, store, storeRoute } = useStore()
const heroStore = computed(() => store.value || getStoreById('steel'))

const productStore = useProductStore()
const categoryStore = useCategoryStore()
const cartStore = useCartStore()

// SEO Meta Tags (store-aware). Strana kategorije (?category=N) ima svoj canonical,
// u istom obliku kao u sitemap-u; nepoznata kategorija pada na stranu prodavnice.
const activeCategory = computed(() => {
  const id = Number(route.query.category)
  return categoryStore.categories.find(c => c.id === id) || null
})

useHead(() => {
  const category = activeCategory.value
  return buildHead({
    title: category ? `${category.name} | ${heroStore.value.seoTitle}` : heroStore.value.seoTitle,
    description: heroStore.value.seoDescription,
    path: category ? `${heroStore.value.path}?category=${category.id}` : heroStore.value.path,
    image: DEFAULT_OG_IMAGE,
    imageAlt: `BetaPack - ${heroStore.value.heroTitle}`
  })
})

// Carousel state
const carouselIndex = ref(0)
const carouselContainer = ref(null)

// Filters
// Kategorija zivi u adresi (?category=N): klik, Nazad/Napred, osvezavanje i direktan
// link daju isti prikaz. Ostali filteri (podkategorija, pretraga, akcija) su lokalni.
const selectedCategory = computed(() => activeCategory.value?.id ?? null)
const selectedSubcategory = ref(null)
const expandedCategories = ref(new Set())
const searchQuery = ref('')
const showOnlyOnSale = ref(false)

// Error message for invalid quantity
const quantityError = ref({})

const formatPrice = (price) => {
  return new Intl.NumberFormat('sr-RS', {
    style: 'currency',
    currency: 'RSD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
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

  // Filter by subcategory
  if (selectedSubcategory.value) {
    products = products.filter(p => p.subcategory === selectedSubcategory.value)
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

const productPath = (product) => {
  const identifier = product.slug || product.id || product
  return storeRoute(`/proizvod/${identifier}`)
}

const viewProductDetail = (product) => {
  router.push(productPath(product))
}

// Product quantities (key = product.id, value = quantity)
const productQuantities = ref({})

// Selected variants per product (key = product.id, value = variant or null)
const selectedVariants = ref({})

const isAmbalazaShop = () => storeId.value === 'ambalaza'

const getProductMinQuantity = (product) => {
  if (isAmbalazaShop()) return getAmbalazaMinQuantity(product, getSelectedVariant(product))
  return getMinQuantity(product)
}

const getProductQuantityStep = (product) => {
  if (isAmbalazaShop()) return getAmbalazaQuantityStep(product, getSelectedVariant(product))
  return getQuantityStep(product)
}

const getProductDefaultQuantity = (product, variant = null) => {
  if (isAmbalazaShop()) return getAmbalazaDefaultQuantity(product, variant ?? getSelectedVariant(product))
  return getDefaultQuantity(product)
}

const getQuantity = (productId) => {
  if (productQuantities.value[productId] !== undefined) {
    return productQuantities.value[productId]
  }
  const product = productStore.products.find(p => p.id === productId)
  return product ? getProductDefaultQuantity(product) : 1
}

const setQuantity = (productId, quantity) => {
  const product = productStore.products.find(p => p.id === productId)
  const variant = product ? getSelectedVariant(product) : null
  const minQuantity = product ? getProductMinQuantity(product) : 1
  if (quantity < minQuantity) quantity = minQuantity

  if (product) {
    const valid = isAmbalazaShop()
      ? isAmbalazaValidQuantity(product, quantity, variant)
      : isValidQuantity(product, quantity)

    if (!valid) {
      const mode = isAmbalazaShop()
        ? (variant?.selling_mode || product.selling_mode)
        : getSellingMode(product)

      if (mode === 'length') {
        quantityError.value[productId] = 'Proizvod se prodaje ceo ili na pola (npr. 1, 1.5, 2, 2.5). Uneta vrednost nije validna.'
        const whole = Math.floor(quantity)
        const decimal = quantity % 1
        quantity = decimal < 0.25 ? whole : (decimal < 0.75 ? whole + 0.5 : whole + 1)
      } else if (mode === 'package') {
        const pkg = isAmbalazaShop()
          ? getAmbalazaPackageSize(product, variant)
          : getPackageSize(product)
        quantityError.value[productId] = `Količina mora biti višekratnik pakovanja (${pkg} kom.)`
        quantity = Math.max(pkg, Math.round(quantity / pkg) * pkg)
      }
    } else {
      quantityError.value[productId] = null
    }
  }

  productQuantities.value[productId] = quantity
}

// Get selected variant for a product.
// selectedVariants čuva samo ID (ne ceo objekat) — varijanta se uvek
// traži iznova u trenutnom product.variants, da izbegnemo prikaz
// zastarelog objekta posle refetch-a (npr. nakon izmene u adminu).
const getSelectedVariant = (product) => {
  if (!product.variants || product.variants.length === 0) return null

  const selectedId = selectedVariants.value[product.id]
  if (selectedId != null) {
    const current = product.variants.find(v => v.id === selectedId)
    if (current) return current
  }

  // Otherwise, auto-select variant
  const saleVariant = product.variants.find(v => v.on_sale)
  const variantToSelect = saleVariant || product.variants[0]
  selectedVariants.value[product.id] = variantToSelect.id
  return variantToSelect
}

// Sort variants by dimension only (for dropdown display)
const getSortedVariantsByDimension = (product) => {
  if (!product.variants || product.variants.length === 0) return []

  const extractDimension = (name) => {
    const match = name.match(/(\d+)/)
    return match ? parseInt(match[1]) : 0
  }

  return [...product.variants].sort((a, b) => {
    return extractDimension(a.name) - extractDimension(b.name)
  })
}

// Set selected variant for a product
const setSelectedVariant = (productId, variant) => {
  selectedVariants.value[productId] = variant?.id ?? null
  const product = productStore.products.find(p => p.id === productId)
  setQuantity(productId, product ? getProductDefaultQuantity(product, variant) : 1)
}

// Get price for a product (considering selected variant)
const getProductPrice = (product) => {
  if (isAmbalazaShop()) {
    return getAmbalazaDisplayPrice(product, getSelectedVariant(product))
  }
  if (isOnRequest(product)) return null
  const variant = getSelectedVariant(product)
  if (variant) {
    return parseFloat(variant.current_price || variant.price)
  }
  return product.current_price != null ? parseFloat(product.current_price) : null
}

// Check if selected variant is on sale
const isVariantOnSale = (product) => {
  const variant = getSelectedVariant(product)
  if (variant) {
    return variant.on_sale
  }
  return product.on_sale
}

const formatProductPriceLabel = (product) => {
  if (isAmbalazaShop()) {
    return formatAmbalazaPriceLabel(product, getSelectedVariant(product), formatPrice)
  }
  if (isOnRequest(product)) return 'Cena na upit'
  const price = getProductPrice(product)
  if (price == null) return 'Cena na upit'
  const mode = getSellingMode(product)
  if (mode === 'package') return `${formatPrice(price)} / kom.`
  if (mode === 'weight') return `${formatPrice(price)} / kg`
  if (mode === 'length') return `${formatPrice(price)} / kom.`
  return formatPrice(price)
}

const isProductOnRequest = (product) => {
  if (isAmbalazaShop()) return isAmbalazaOnRequest(product, getSelectedVariant(product))
  return isOnRequest(product)
}

const getProductSellingNote = (product) => {
  if (!isAmbalazaShop()) return null
  return getAmbalazaSellingNote(product, getSelectedVariant(product))
}

const getVariantOriginalPrice = (product) => {
  const variant = getSelectedVariant(product)
  if (variant) {
    return parseFloat(variant.price)
  }
  return parseFloat(product.price)
}

// Get length_per_unit from variant or product
const getVariantLength = (product) => {
  const variant = getSelectedVariant(product)
  if (variant) {
    // Use effective_length_per_unit if available (from backend), otherwise length_per_unit, otherwise product's length
    if (variant.effective_length_per_unit) {
      return parseFloat(variant.effective_length_per_unit)
    }
    if (variant.length_per_unit) {
      return parseFloat(variant.length_per_unit)
    }
  }
  return product.length_per_unit ? parseFloat(product.length_per_unit) : null
}

// Get cart item for a product
const getCartItem = (product) => {
  const variant = getSelectedVariant(product)
  const variantId = variant ? variant.id : null
  return cartStore.getCartItem(product.id, variantId)
}

// Get quantity from cart for a product
const getCartQuantity = (product) => {
  const cartItem = getCartItem(product)
  return cartItem ? cartItem.quantity : 0
}

// Update quantity in cart
const updateCartQuantity = (product, newQuantity) => {
  const minQuantity = getProductMinQuantity(product)
  if (newQuantity < minQuantity) return

  const variant = getSelectedVariant(product)
  const valid = isAmbalazaShop()
    ? isAmbalazaValidQuantity(product, newQuantity, variant)
    : isValidQuantity(product, newQuantity)

  if (!valid) {
    if (isAmbalazaShop()) {
      if (isAmbalazaPackageMode(product, variant)) {
        const pkg = getAmbalazaPackageSize(product, variant)
        newQuantity = Math.max(pkg, Math.round(newQuantity / pkg) * pkg)
      }
    } else if (isLengthMode(product)) {
      quantityError.value[product.id] = 'Proizvod se prodaje ceo ili na pola (npr. 1, 1.5, 2, 2.5). Uneta vrednost nije validna.'
      const whole = Math.floor(newQuantity)
      const decimal = newQuantity % 1
      newQuantity = decimal < 0.25 ? whole : (decimal < 0.75 ? whole + 0.5 : whole + 1)
    } else if (isPackageMode(product)) {
      const pkg = parseInt(product.package_size, 10) || 1
      newQuantity = Math.max(pkg, Math.round(newQuantity / pkg) * pkg)
    }
    setTimeout(() => { quantityError.value[product.id] = null }, 3000)
  } else {
    quantityError.value[product.id] = null
  }

  const cartId = variant ? `${product.id}-${variant.id}` : product.id
  cartStore.updateQuantity(cartId, newQuantity)
}

const addToCartFromCard = (product) => {
  const variant = getSelectedVariant(product)
  let quantity = getQuantity(product.id)

  if (isAmbalazaShop() && !isAmbalazaValidQuantity(product, quantity, variant)) {
    quantity = getProductDefaultQuantity(product, variant)
  } else if (!isAmbalazaShop() && !isValidQuantity(product, quantity)) {
    setQuantity(product.id, getProductDefaultQuantity(product))
    return
  }

  quantityError.value[product.id] = null
  cartStore.add({ ...product, selectedVariant: variant }, quantity)
  setQuantity(product.id, getProductDefaultQuantity(product, variant))
}

// Remove product from cart
const removeFromCart = (product) => {
  const variant = getSelectedVariant(product)
  const cartId = variant 
    ? `${product.id}-${variant.id}`
    : product.id
  
  cartStore.remove(cartId)
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

// Podkategorija vazi samo unutar svoje kategorije; pri promeni kategorije
// (klik ili Nazad/Napred) se odbacuje ako joj ne pripada.
watch(selectedCategory, (categoryId) => {
  const category = categoryStore.categories.find(c => c.id === categoryId)
  const belongs = category?.subcategories?.some(s => s.id === selectedSubcategory.value)
  if (!belongs) {
    selectedSubcategory.value = null
  }
  scrollToProducts()
})

// Upisuje kategoriju u adresu (push, da Nazad vraca na prethodnu kategoriju)
const setCategory = (categoryId) => {
  if (categoryId === selectedCategory.value) return
  const query = { ...route.query }
  if (categoryId == null) {
    delete query.category
  } else {
    query.category = String(categoryId)
  }
  router.push({ path: route.path, query })
}

const selectCategory = (categoryId) => {
  selectedSubcategory.value = null
  setCategory(categoryId)
}

const selectSubcategory = (categoryId, subcategoryId) => {
  selectedSubcategory.value = subcategoryId
  setCategory(categoryId)
}

const resetFilters = () => {
  selectedSubcategory.value = null
  searchQuery.value = ''
  showOnlyOnSale.value = false
  setCategory(null)
}

// Scroll to products when subcategory changes
watch(selectedSubcategory, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    scrollToProducts()
  }
})

// Scroll to products grid with offset for sticky header
const scrollToProducts = () => {
  setTimeout(() => {
    const element = document.getElementById('products-section')
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, 50)
}

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

const loadStoreData = async () => {
  if (!storeId.value) return

  // Reset filters when switching store (kategorija se ravna po adresi)
  selectedSubcategory.value = null
  searchQuery.value = ''
  showOnlyOnSale.value = false
  selectedVariants.value = {}
  productQuantities.value = {}
  await categoryStore.fetchCategories(storeId.value)
  await productStore.fetchProducts(storeId.value)
}

watch(
  () => route.path,
  () => {
    if (route.name?.endsWith('-shop')) {
      loadStoreData()
    }
  },
  { immediate: true }
)

const onPageShow = (event) => {
  if (event.persisted && route.name?.endsWith('-shop')) {
    loadStoreData()
  }
}

const onVisibilityChange = () => {
  if (document.visibilityState === 'visible' && route.name?.endsWith('-shop')) {
    loadStoreData()
  }
}

// 'focus' pokriva slučaj kada su admin i shop u dva odvojena prozora
// jedan pored drugog (oba "visible", pa 'visibilitychange' ne okine).
const onWindowFocus = () => {
  if (route.name?.endsWith('-shop')) {
    loadStoreData()
  }
}

onMounted(() => {
  window.addEventListener('pageshow', onPageShow)
  document.addEventListener('visibilitychange', onVisibilityChange)
  window.addEventListener('focus', onWindowFocus)
})

onUnmounted(() => {
  window.removeEventListener('pageshow', onPageShow)
  document.removeEventListener('visibilitychange', onVisibilityChange)
  window.removeEventListener('focus', onWindowFocus)
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1">

      <!-- Hero Image -->
      <div class="relative overflow-hidden" :style="{ height: storeId === 'ambalaza' ? '580px' : '450px' }">
        <ResponsivePicture
          :src="heroStore.heroImage"
          :sources="heroStore.heroImageSources"
          :width="heroStore.heroImageSize[0]"
          :height="heroStore.heroImageSize[1]"
          :alt="`BetaPack - ${heroStore.heroTitle}`"
          eager
          class="absolute inset-0 w-full h-full object-cover"
        />

        <!-- Ambalaža hero overlay -->
        <div
          v-if="storeId === 'ambalaza'"
          class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/55 to-black/30"
        ></div>

        <div class="absolute inset-0 flex items-center justify-center px-4">
          <!-- Ambalaža styled hero -->
          <div
            v-if="storeId === 'ambalaza'"
            class="text-center text-white max-w-4xl w-full animate-fade-in-up"
          >
            <span
              class="inline-block mb-4 px-4 py-1.5 rounded-full text-xs sm:text-sm font-semibold tracking-wider uppercase border border-white/25 bg-white/10 backdrop-blur-sm"
            >
              Beta Pack Ambalaža
            </span>
            <h1
              class="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold mb-5 leading-tight"
              style="text-shadow: 2px 2px 12px rgba(0,0,0,0.8);"
            >
              {{ heroStore.heroTitle }}
            </h1>
            <p
              class="text-sm sm:text-base lg:text-lg text-gray-100 max-w-3xl mx-auto leading-relaxed mb-6"
              style="text-shadow: 1px 1px 6px rgba(0,0,0,0.8);"
            >
              {{ heroStore.heroSubtitle }}
            </p>

            <div
              v-if="heroStore.heroTags?.length"
              class="flex flex-wrap items-center justify-center gap-2 sm:gap-3 mb-6 max-w-3xl mx-auto"
            >
              <span
                v-for="(tag, index) in heroStore.heroTags"
                :key="tag"
                class="inline-flex items-center"
              >
                <span
                  class="px-3 py-1.5 rounded-full text-xs sm:text-sm font-semibold bg-white/15 backdrop-blur-md border border-white/20 shadow-sm"
                >
                  {{ tag }}
                </span>
                <span
                  v-if="index < heroStore.heroTags.length - 1"
                  class="hidden sm:inline text-white/40 mx-1 text-lg select-none"
                >•</span>
              </span>
            </div>

            <p
              v-if="heroStore.heroTagline"
              class="text-base sm:text-lg lg:text-xl font-semibold tracking-wide text-[#42a5f5]"
              style="text-shadow: 1px 1px 8px rgba(0,0,0,0.9);"
            >
              {{ heroStore.heroTagline }}
            </p>
          </div>

          <!-- Default hero (Gvožđara) -->
          <div
            v-else
            class="text-center text-white px-6 py-8 max-w-4xl rounded-xl animate-fade-in-up"
            style="background-color: rgba(0, 0, 0, 0.65); backdrop-filter: blur(4px);"
          >
            <h1
              class="text-3xl lg:text-5xl xl:text-6xl font-bold mb-4 uppercase"
              style="text-shadow: 2px 2px 8px rgba(0,0,0,0.9);"
            >
              {{ heroStore.heroTitle }}
            </h1>
            <p
              class="text-base lg:text-xl text-white"
              style="text-shadow: 2px 2px 6px rgba(0,0,0,0.9);"
            >
              {{ heroStore.heroSubtitle }}
            </p>
          </div>
        </div>

        <!-- Buttons positioned at bottom -->
        <div class="absolute inset-0 flex items-end justify-center pb-6 sm:pb-10 pointer-events-none">
          <div class="flex flex-col items-center gap-3 px-4 pointer-events-auto">
            <div class="flex flex-wrap justify-center gap-3">
              <a
                href="#products"
                class="bg-white hover:bg-gray-100 text-gray-900 font-semibold px-6 py-3 rounded-lg transition cursor-pointer shadow-lg text-sm lg:text-base"
              >
                {{ heroStore.heroCatalogButton || 'Pogledaj katalog' }}
              </a>
              <router-link
                :to="storeRoute('/kontakt')"
                class="text-white font-semibold px-6 py-3 rounded-lg transition cursor-pointer shadow-lg text-sm lg:text-base"
                :style="{ backgroundColor: heroStore.accentColor }"
              >
                {{ heroStore.heroContactButton || 'Pošalji upit' }}
              </router-link>
            </div>
            <p
              v-if="storeId === 'ambalaza' && heroStore.heroOfferNote"
              class="text-center text-xs sm:text-sm text-white/90 max-w-xl leading-relaxed font-medium px-2"
              style="text-shadow: 1px 1px 6px rgba(0,0,0,0.9);"
            >
              {{ heroStore.heroOfferNote }}
            </p>
          </div>
        </div>
      </div>

      <!-- Trust Badges Section -->
      <div class="bg-white py-12 border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
            <!-- Badge 1 -->
            <div class="flex flex-col items-center text-center group">
              <div class="w-16 h-16 mb-3 rounded-full bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors duration-300">
                <span class="text-3xl">🚚</span>
              </div>
              <h3 class="font-bold text-sm md:text-base text-gray-900 mb-1">Dostava</h3>
              <p class="text-xs md:text-sm text-gray-600">Širom Republike Srbije</p>
            </div>

            <!-- Badge 2 -->
            <div class="flex flex-col items-center text-center group">
              <div class="w-16 h-16 mb-3 rounded-full bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors duration-300">
                <span class="text-3xl">✅</span>
              </div>
              <h3 class="font-bold text-sm md:text-base text-gray-900 mb-1">Garancija kvaliteta</h3>
              <p class="text-xs md:text-sm text-gray-600">Sertifikovani materijali</p>
            </div>

            <!-- Badge 3 -->
            <div class="flex flex-col items-center text-center group">
              <div class="w-16 h-16 mb-3 rounded-full bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors duration-300">
                <span class="text-3xl">📞</span>
              </div>
              <h3 class="font-bold text-sm md:text-base text-gray-900 mb-1">Podrška</h3>
              <p class="text-xs md:text-sm text-gray-600">065/330 02 42</p>
            </div>

            <!-- Badge 4 -->
            <div class="flex flex-col items-center text-center group">
              <div class="w-16 h-16 mb-3 rounded-full bg-orange-100 flex items-center justify-center group-hover:bg-orange-200 transition-colors duration-300">
                <span class="text-3xl">🏆</span>
              </div>
              <h3 class="font-bold text-sm md:text-base text-gray-900 mb-1">25 godina iskustva</h3>
              <p class="text-xs md:text-sm text-gray-600">Pouzdan partner</p>
            </div>
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
                      @click="viewProductDetail(product)"
                      class="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-xl transition cursor-pointer group"
                    >
                      <div class="relative h-48 bg-white overflow-hidden">
                        <img
                          v-if="getProductImage(product)"
                          :src="getImageUrl(getProductImage(product).image)"
                          :alt="`${product.name} - ${product.category_name} - BetaPack kovano gvožđe`"
                          loading="lazy"
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
                        <h3 class="font-bold text-gray-900 mb-3 text-lg line-clamp-1"><router-link :to="productPath(product)" @click.stop>{{ product.name }}</router-link></h3>

                        <div class="flex items-center justify-between mt-3">
                          <div>
                            <p v-if="product.has_sale_variants && product.original_min_price" class="text-base text-gray-400 line-through mb-1">
                              {{ formatPrice(product.original_min_price) }}
                            </p>
                            <p v-else-if="product.on_sale" class="text-base text-gray-400 line-through mb-1">
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
              <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-4 sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto">
                <div class="flex items-center justify-between mb-4 border-b border-gray-200 pb-2">
                  <h3 class="font-bold text-base lg:text-lg text-gray-900">Filteri</h3>
                  <button
                    v-if="selectedCategory || selectedSubcategory || searchQuery || showOnlyOnSale"
                    @click="resetFilters"
                    class="text-xs text-gray-500 hover:text-red-600 transition cursor-pointer flex items-center gap-1"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Resetuj
                  </button>
                </div>

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
                    @click="selectCategory(null)"
                    :class="selectedCategory === null ? 'bg-gradient-to-r from-[#1976d2] to-[#1565c0] text-white font-semibold shadow-md' : 'text-gray-700 hover:bg-gray-100'"
                    class="w-full text-left px-3 py-2 text-sm rounded-lg transition mb-1 cursor-pointer font-semibold"
                  >
                    Sve kategorije
                  </button>

                  <div v-for="cat in categoryStore.categories" :key="cat.id" class="mb-1">
                    <!-- Category with subcategories -->
                    <div v-if="cat.subcategories && cat.subcategories.length > 0">
                      <div class="flex items-center">
                        <button
                          @click="selectCategory(cat.id)"
                          :class="selectedCategory === cat.id && !selectedSubcategory ? 'bg-gradient-to-r from-[#1976d2] to-[#1565c0] text-white font-semibold shadow-md' : 'text-gray-700 hover:bg-gray-100'"
                          class="flex-1 text-left px-3 py-2 text-sm rounded-l-lg transition cursor-pointer font-semibold"
                        >
                          {{ cat.name }}
                        </button>
                        <button
                          @click="expandedCategories.has(cat.id) ? expandedCategories.delete(cat.id) : expandedCategories.add(cat.id)"
                          class="px-2 py-2 text-gray-500 hover:bg-gray-100 rounded-r-lg transition"
                        >
                          <svg
                            :class="expandedCategories.has(cat.id) ? 'rotate-180' : ''"
                            class="w-4 h-4 transition-transform"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                      </div>
                      <!-- Subcategories -->
                      <div v-if="expandedCategories.has(cat.id)" class="ml-3 mt-1 border-l-2 border-gray-200 pl-2">
                        <button
                          v-for="sub in cat.subcategories"
                          :key="sub.id"
                          @click="selectSubcategory(cat.id, sub.id)"
                          :class="selectedSubcategory === sub.id ? 'bg-gradient-to-r from-[#1976d2] to-[#1565c0] text-white font-semibold shadow-md' : 'text-gray-600 hover:bg-gray-100'"
                          class="w-full text-left px-3 py-1.5 text-xs rounded-lg transition mb-0.5 cursor-pointer"
                        >
                          {{ sub.name }}
                        </button>
                      </div>
                    </div>
                    <!-- Category without subcategories -->
                    <button
                      v-else
                      @click="selectCategory(cat.id)"
                      :class="selectedCategory === cat.id ? 'bg-gradient-to-r from-[#1976d2] to-[#1565c0] text-white font-semibold shadow-md' : 'text-gray-700 hover:bg-gray-100'"
                      class="w-full text-left px-3 py-2 text-sm rounded-lg transition cursor-pointer font-semibold"
                    >
                      {{ cat.name }}
                    </button>
                  </div>
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
            <div id="products-section" class="lg:col-span-4 scroll-mt-24">
              <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-3 border-b border-gray-200">
                <h2 class="text-lg lg:text-xl font-bold text-gray-900">
                  {{ selectedSubcategory
                    ? categoryStore.categories.find(c => c.id === selectedCategory)?.subcategories?.find(s => s.id === selectedSubcategory)?.name
                    : (selectedCategory ? categoryStore.categories.find(c => c.id === selectedCategory)?.name : 'Svi proizvodi') }}
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
                  class="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-2xl hover:border-[#1976d2] hover:-translate-y-2 transition-all duration-300 group flex flex-col h-full"
                >
                  <div
                    @click="viewProductDetail(product)"
                    class="cursor-pointer flex-1 flex flex-col"
                  >
                    <div class="relative h-56 lg:h-64 bg-white overflow-hidden flex-shrink-0">
                      <!-- Dark overlay on hover -->
                      <div class="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors duration-300 z-10 pointer-events-none"></div>

                      <img
                        v-if="getProductImage(product)"
                        :src="getImageUrl(getProductImage(product).image)"
                        :alt="`${product.name} - ${product.category_name} - BetaPack kovano gvožđe`"
                        loading="lazy"
                        class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
                      />
                      <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                        <span class="text-2xl">📦</span>
                      </div>

                      <!-- Sale Badge - improved -->
                      <div v-if="product.on_sale || isVariantOnSale(product)" class="absolute top-2 right-2 z-20">
                        <div class="bg-gradient-to-br from-red-500 to-red-600 text-white px-3 py-1.5 rounded-full text-xs font-bold shadow-lg flex items-center gap-1 animate-pulse">
                          <span>🔥</span>
                          <span>-{{ salePercent(getVariantOriginalPrice(product), getProductPrice(product)) }}%</span>
                        </div>
                      </div>

                      <!-- Stock indicator -->
                      <div v-if="!product.in_stock" class="absolute top-2 left-2 bg-gray-800/90 text-white px-3 py-1 rounded-full text-xs font-semibold z-20">
                        Rasprodato
                      </div>

                      <!-- SKU badge -->
                      <div v-if="getSelectedVariant(product)?.sku" class="absolute bottom-2 left-2 bg-gray-800/80 text-white px-2 py-1 rounded text-[10px] font-mono z-20">
                        {{ getSelectedVariant(product).sku }}
                      </div>
                    </div>

                    <div class="p-3 flex-1 flex flex-col">
                      <p class="text-xs text-[#1565c0] font-bold mb-1 uppercase tracking-wide">{{ product.category_name }}</p>
                      <h3 class="font-bold text-gray-900 mb-1 text-sm line-clamp-2"><router-link :to="productPath(product)" @click.stop>{{ product.name }}</router-link></h3>
                      <p class="text-xs text-gray-600 mb-2 line-clamp-2 leading-relaxed">{{ product.description }}</p>

                      <div class="mt-auto">
                        <div class="flex items-center justify-between mb-2">
                          <div>
                            <p v-if="isVariantOnSale(product) && !isProductOnRequest(product)" class="text-xs text-gray-400 line-through mb-0.5">
                              {{ formatPrice(getVariantOriginalPrice(product)) }}
                            </p>
                            <p v-if="isProductOnRequest(product)" class="text-base font-bold text-orange-600">
                              Cena na upit
                            </p>
                            <p v-else class="text-base font-bold" :class="isVariantOnSale(product) ? 'text-red-600' : 'text-green-700'">
                              {{ formatProductPriceLabel(product) }}
                            </p>
                            <p
                              v-if="storeId === 'ambalaza' && getProductSellingNote(product)"
                              class="text-[10px] text-[#1976d2] font-semibold mt-1"
                            >
                              {{ getProductSellingNote(product) }}
                            </p>
                            <p
                              v-if="storeId === 'ambalaza' && isAmbalazaPackageMode(product, getSelectedVariant(product)) && getProductPrice(product)"
                              class="text-[10px] text-gray-600 mt-0.5"
                            >
                              Ukupno ({{ getQuantity(product.id) }} kom.):
                              {{ formatPrice(getProductPrice(product) * getQuantity(product.id)) }}
                            </p>
                            <p v-if="product.dimensions" class="text-[10px] text-gray-500 mt-0.5">{{ product.dimensions }}</p>
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
                              v-for="variant in getSortedVariantsByDimension(product)"
                              :key="variant.id"
                              :value="variant.id"
                            >
                              {{ variant.name }}
                            </option>
                          </select>
                        </div>

                        <!-- Quantity Selector (only show if product is NOT in cart) -->
                        <div v-if="!cartStore.isInCart(product.id, getSelectedVariant(product)?.id)" class="mb-2 w-full" @click.stop>
                          <span class="block text-xs font-bold text-gray-700 mb-1">Količina:</span>
                          <div class="flex items-center gap-1.5 w-full bg-gray-100 rounded-xl p-1">
                            <button
                              @click="setQuantity(product.id, getQuantity(product.id) - getProductQuantityStep(product))"
                              class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm flex items-center justify-center"
                            >
                              −
                            </button>
                            <input
                              :value="getQuantity(product.id)"
                              @input="setQuantity(product.id, parseFloat($event.target.value) || getProductMinQuantity(product))"
                              type="number"
                              :min="getProductMinQuantity(product)"
                              :step="getProductQuantityStep(product)"
                              class="flex-1 min-w-0 w-full text-sm font-semibold tabular-nums text-center text-gray-900 bg-white border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-[#1976d2] focus:outline-none"
                            />
                            <button
                              @click="setQuantity(product.id, getQuantity(product.id) + getProductQuantityStep(product))"
                              class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm flex items-center justify-center"
                            >
                              +
                            </button>
                          </div>
                          <p v-if="storeId === 'steel' && isLengthMode(product)" class="text-[10px] text-blue-600 font-semibold italic">
                            ℹ️ Proizvodi se prodaju po komadu (1 kom = {{ getVariantLength(product) || product.length_per_unit || 6 }} m), uz mogućnost kupovine celog ili pola komada ({{ ((getVariantLength(product) || product.length_per_unit || 6) / 2).toFixed(1) }} m).
                          </p>
                          <p v-if="storeId === 'steel' && isPackageMode(product)" class="text-[10px] text-green-600 font-semibold italic">
                            📦 {{ getPackageNote(product) }} — cena po komadu
                          </p>
                          <p v-if="storeId === 'steel' && isWeightMode(product)" class="text-[10px] text-blue-600 font-semibold italic">
                            ⚖️ Prodaja po kilogramu
                          </p>
                          <p v-if="storeId === 'ambalaza' && !isProductOnRequest(product) && isAmbalazaPackageMode(product, getSelectedVariant(product))" class="text-[10px] text-green-600 font-semibold italic">
                            📦 {{ getAmbalazaPackageNote(product, getSelectedVariant(product)) }} — cena po komadu
                          </p>
                          <p v-if="storeId === 'ambalaza' && !isProductOnRequest(product) && isAmbalazaWeightMode(product, getSelectedVariant(product))" class="text-[10px] text-blue-600 font-semibold italic">
                            ⚖️ Prodaja po kilogramu
                          </p>
                          <p v-if="quantityError[product.id]" class="text-[10px] text-red-600 font-semibold italic mt-1">
                            ❌ {{ quantityError[product.id] }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="px-5 lg:px-6 pb-5 lg:pb-6 flex-shrink-0">
                    <!-- If product is in cart, show quantity controls -->
                    <div v-if="cartStore.isInCart(product.id, getSelectedVariant(product)?.id)" class="space-y-2 w-full" @click.stop>
                      <span class="block text-xs font-bold text-gray-700 mb-1">Izmeni količinu:</span>
                      <div class="flex items-center gap-1.5 w-full bg-gray-100 rounded-xl p-1">
                        <button
                          @click.stop="updateCartQuantity(product, getCartQuantity(product) - getProductQuantityStep(product))"
                          :disabled="getCartQuantity(product) <= getProductMinQuantity(product)"
                          class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                          −
                        </button>
                        <input
                          :value="getCartQuantity(product)"
                          @input="updateCartQuantity(product, parseFloat($event.target.value) || getProductMinQuantity(product))"
                          @blur="updateCartQuantity(product, Math.max(getProductMinQuantity(product), parseFloat($event.target.value) || getProductMinQuantity(product)))"
                          type="number"
                          :min="getProductMinQuantity(product)"
                          :step="getProductQuantityStep(product)"
                          class="flex-1 min-w-0 w-full text-sm font-semibold tabular-nums text-center text-gray-900 bg-white border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-[#1976d2] focus:outline-none"
                        />
                        <button
                          @click.stop="updateCartQuantity(product, getCartQuantity(product) + getProductQuantityStep(product))"
                          class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm flex items-center justify-center"
                        >
                          +
                        </button>
                      </div>
                      <p v-if="storeId === 'steel' && isLengthMode(product)" class="text-[10px] text-blue-600 font-semibold italic text-center">
                        📏 Izabrano je {{ (getCartQuantity(product) * (getVariantLength(product) || product.length_per_unit || 6)).toFixed(2) }} metara
                      </p>
                      <p v-if="storeId === 'steel' && isPackageMode(product)" class="text-[10px] text-green-600 font-semibold italic text-center">
                        📦 {{ getCartQuantity(product) / (product.package_size || 1) }} pak. ({{ getCartQuantity(product) }} kom.)
                      </p>
                      <p v-if="storeId === 'ambalaza' && isAmbalazaPackageMode(product, getSelectedVariant(product))" class="text-[10px] text-green-600 font-semibold italic text-center">
                        📦 {{ getCartQuantity(product) / (getAmbalazaPackageSize(product, getSelectedVariant(product)) || 1) }} pak. ({{ getCartQuantity(product) }} kom.)
                      </p>
                      <p v-if="quantityError[product.id]" class="text-[10px] text-red-600 font-semibold italic text-center mt-1">
                        ❌ {{ quantityError[product.id] }}
                      </p>
                      <!-- Remove from cart button -->
                      <button
                        @click.stop="removeFromCart(product)"
                        class="w-full text-red-600 hover:text-red-700 text-xs font-semibold cursor-pointer text-center mt-1"
                      >
                        Ukloni
                      </button>
                    </div>
                    <!-- If product is not in cart, show add button -->
                    <button
                      v-else
                      @click.stop="addToCartFromCard(product)"
                      class="w-full bg-gradient-to-r from-[#1976d2] to-[#1565c0] hover:from-[#1565c0] hover:to-[#0d47a1] text-white font-bold py-3 rounded-xl transition-all duration-300 cursor-pointer shadow-lg hover:shadow-xl text-sm lg:text-base"
                    >
                      {{ isProductOnRequest(product) ? 'Dodaj na upit' : '+ Dodaj u korpu' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-else class="text-center py-10">
                <span class="text-3xl text-gray-300 mb-3 block">🔍</span>
                <p class="text-xl text-gray-600 mb-4">Nema proizvoda koji odgovaraju filterima</p>
                <button
                  @click="resetFilters"
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

<style scoped>
/* Fade-in animation for hero text */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out forwards;
}

/* Pulse animation for sale badges */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
