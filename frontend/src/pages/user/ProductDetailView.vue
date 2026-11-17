<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import ProductImage from '@/components/ProductImage.vue'
import { useCartStore } from '@/store/cart'
import { api } from '@/services/api'
import { getImageUrl } from '@/composables/useImageUrl'
import { cloudinaryUrl } from '@/utils/cloudinary'
import { useStore } from '@/composables/useStore'
import { getStoreById } from '@/config/stores'
import { buildHead, absoluteUrl, SITE_URL } from '@/utils/seo'
import { getAmbalazaDefaultQuantity, getAmbalazaSellingNote, isAmbalazaPackageMode, getAmbalazaQuantityStep, getAmbalazaMinQuantity } from '@/composables/useAmbalazaSelling'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const { storeRoute, storeId } = useStore()

const product = ref(null)
const loading = ref(true)
const selectedVariant = ref(null)
const selectedImageIndex = ref(0)
const quantity = ref(1)
const quantityError = ref(null)

// og:image, twitter:image i JSON-LD: JPEG sirine 1200 px. Originali sa Cloudinary-ja znaju
// biti vise MB (WhatsApp/Facebook odbace prevelike slike), a JPEG je jedini oblik koji
// podrzavaju svi cetkari; f_auto bi im vratio WebP/AVIF.
const shareImageUrl = (image) => cloudinaryUrl(getImageUrl(image), { width: 1200, format: 'jpg' })

// Prodavnica kojoj proizvod pripada. Dok se proizvod ne ucita, vazi prodavnica iz URL-a.
const productStoreId = computed(() => product.value?.store || storeId.value || 'steel')
const productStore = computed(() => getStoreById(productStoreId.value))

// Prava putanja proizvoda: /<prodavnica>/proizvod/<slug>
const productPath = computed(() =>
  product.value
    ? `${productStore.value.path}/proizvod/${product.value.slug || product.value.id}`
    : productStore.value.path
)

const defaultDescription = (name) =>
  productStoreId.value === 'ambalaza'
    ? `Ambalaža za hranu i ugostiteljstvo - ${name}`
    : `Kvalitetan proizvod od kovanog gvožđa - ${name}`

// Dynamic SEO Meta Tags based on product
const productTitle = computed(() =>
  product.value ? `${product.value.name} - ${product.value.category_name || 'Proizvodi'} | BetaPack` : 'Proizvod | BetaPack'
)
const productDescription = computed(() =>
  product.value ? product.value.description || defaultDescription(product.value.name) : 'BetaPack proizvod'
)
const productImage = computed(() =>
  product.value && product.value.images && product.value.images.length > 0
    ? shareImageUrl(product.value.images[0].image)
    : `${SITE_URL}/betapack-logo.png`
)
const productPrice = computed(() =>
  product.value ? product.value.current_price : 0
)

// Schema.org JSON-LD for Product
const productSchema = computed(() => {
  if (!product.value) return null

  const isSteel = productStoreId.value === 'steel'

  return {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.value.name,
    description: product.value.description || defaultDescription(product.value.name),
    image: product.value.images && product.value.images.length > 0
      ? product.value.images.map(img => shareImageUrl(img.image))
      : [`${SITE_URL}/betapack-logo.png`],
    sku: product.value.id ? `BP-${product.value.id}` : undefined,
    brand: {
      '@type': 'Brand',
      name: 'BetaPack'
    },
    manufacturer: {
      '@type': 'Organization',
      name: 'BetaPack'
    },
    offers: {
      '@type': 'Offer',
      url: absoluteUrl(productPath.value),
      priceCurrency: 'RSD',
      price: product.value.current_price,
      priceValidUntil: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0],
      availability: product.value.in_stock
        ? 'https://schema.org/InStock'
        : 'https://schema.org/OutOfStock',
      itemCondition: 'https://schema.org/NewCondition',
      seller: {
        '@type': 'Organization',
        name: 'BetaPack',
        url: SITE_URL
      }
    },
    category: product.value.category_name || (isSteel ? 'Bravarski materijali' : 'Ambalaža'),
    // Materijal je poznat samo za kovano gvozdje; ambalaza je od raznih materijala
    ...(isSteel ? { material: 'Gvožđe' } : {})
  }
})

// Schema.org JSON-LD for BreadcrumbList: Početna > prodavnica > kategorija > proizvod
const breadcrumbSchema = computed(() => {
  if (!product.value) return null

  const trail = [
    { name: 'Početna', url: `${SITE_URL}/` },
    { name: productStore.value.shortLabel, url: absoluteUrl(productStore.value.path) }
  ]

  if (product.value.category_name) {
    trail.push({
      name: product.value.category_name,
      url: absoluteUrl(`${productStore.value.path}?category=${product.value.category}`)
    })
  }

  trail.push({ name: product.value.name, url: absoluteUrl(productPath.value) })

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: trail.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: item.url
    }))
  }
})

useHead(() => {
  const head = buildHead({
    title: productTitle.value,
    description: productDescription.value,
    path: productPath.value,
    image: productImage.value,
    imageAlt: productTitle.value,
    type: 'product'
  })

  return {
    ...head,
    meta: [
      ...head.meta,
      { property: 'product:price:amount', content: productPrice.value },
      { property: 'product:price:currency', content: 'RSD' }
    ],
    // Structured data postoji tek kad je proizvod ucitan
    script: product.value
      ? [
          { type: 'application/ld+json', key: 'ld-product', innerHTML: JSON.stringify(productSchema.value) },
          { type: 'application/ld+json', key: 'ld-breadcrumb', innerHTML: JSON.stringify(breadcrumbSchema.value) }
        ]
      : []
  }
})

// Pocetna kolicina zavisi od nacina prodaje: ambalaza koja ide u pakovanjima
// krece od pune velicine pakovanja, gvozdje po metrazi od pola metra.
// Koristi se i pri ucitavanju proizvoda i pri promeni varijante, da brojac
// nikad ne krene od vrednosti koja je ispod dozvoljenog minimuma.
const pocetnaKolicina = (variant = null) => {
  if (!product.value) return 1
  if (product.value.store === 'ambalaza') {
    return getAmbalazaDefaultQuantity(product.value, variant)
  }
  return product.value.sold_by_length ? 0.5 : 1
}

// Reset quantity when variant changes, or load from cart if variant is in cart
watch(selectedVariant, () => {
  if (product.value) {
    const variantId = selectedVariant.value ? selectedVariant.value.id : null
    const cartItem = cartStore.getCartItem(product.value.id, variantId)
    quantity.value = cartItem ? cartItem.quantity : pocetnaKolicina(selectedVariant.value)
  } else {
    quantity.value = 1
  }
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('sr-RS', {
    style: 'currency',
    currency: 'RSD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price)
}

const salePercent = computed(() => {
  // Ako je varijanta odabrana, koristi njene cene
  if (selectedVariant.value && selectedVariant.value.on_sale) {
    const regularPrice = parseFloat(selectedVariant.value.price)
    const salePrice = parseFloat(selectedVariant.value.sale_price)
    return Math.round(((regularPrice - salePrice) / regularPrice) * 100)
  }

  // Inače koristi cene proizvoda (ako nema varijanti)
  if (!product.value || !product.value.on_sale) return 0
  return Math.round(((product.value.price - product.value.sale_price) / product.value.price) * 100)
})

const isOnSale = computed(() => {
  // Proveri da li je odabrana varijanta na akciji ili proizvod
  if (selectedVariant.value) {
    return selectedVariant.value.on_sale
  }
  return product.value && product.value.on_sale
})

const finalPrice = computed(() => {
  if (!product.value) return 0

  if (selectedVariant.value) {
    const price = selectedVariant.value.current_price ?? selectedVariant.value.price
    if (product.value.store === 'ambalaza' && selectedVariant.value.selling_mode === 'on_request') return null
    return parseFloat(price)
  }

  if (product.value.store === 'ambalaza' && product.value.selling_mode === 'on_request') return null
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

const sortedVariants = computed(() => {
  if (!product.value || !product.value.variants || product.value.variants.length === 0) {
    return []
  }

  // Helper function to extract numeric dimension (e.g., "16x16" -> 16)
  const extractDimension = (name) => {
    const match = name.match(/(\d+)/)
    return match ? parseInt(match[1]) : 0
  }

  // Sort: sale variants first, then by dimension
  return [...product.value.variants].sort((a, b) => {
    // Akcijske varijante prvo
    if (a.on_sale && !b.on_sale) return -1
    if (!a.on_sale && b.on_sale) return 1
    // Zatim po dimenziji
    return extractDimension(a.name) - extractDimension(b.name)
  })
})

const fetchProduct = async () => {
  loading.value = true
  try {
    const response = await api.get(`/products/${route.params.slugOrId}/`, {
      params: { _: Date.now() }
    })
    product.value = response.data

    // Proizvod otvoren pod pogresnom prodavnicom (npr. stari /proizvod/<slug> link
    // za ambalazu) prebacuje se na svoju pravu putanju.
    if (product.value.store && storeId.value && product.value.store !== storeId.value) {
      router.replace({ path: productPath.value, query: route.query, hash: route.hash })
    }

    // Auto-select first variant if available (first from sorted list - sale variants first)
    if (product.value.variants && product.value.variants.length > 0) {
      // Use sortedVariants to get the first variant (sale variants are first)
      const sorted = [...product.value.variants].sort((a, b) => {
        if (a.on_sale && !b.on_sale) return -1
        if (!a.on_sale && b.on_sale) return 1
        const extractDim = (name) => {
          const match = name.match(/(\d+)/)
          return match ? parseInt(match[1]) : 0
        }
        return extractDim(a.name) - extractDim(b.name)
      })
      selectedVariant.value = sorted[0]
      // Check if this variant is in cart and load quantity
      const variantId = selectedVariant.value.id
      const cartItem = cartStore.getCartItem(product.value.id, variantId)
      quantity.value = cartItem ? cartItem.quantity : pocetnaKolicina(selectedVariant.value)
    } else {
      // No variants, check if product is in cart
      const cartItem = cartStore.getCartItem(product.value.id, null)
      quantity.value = cartItem ? cartItem.quantity : pocetnaKolicina(null)
    }
  } catch (error) {
    console.error('Error fetching product:', error)
    router.push(storeRoute())
  } finally {
    loading.value = false
  }
}

// Get cart item for current product
const getCartItem = computed(() => {
  if (!product.value) return null
  const variantId = selectedVariant.value ? selectedVariant.value.id : null
  return cartStore.getCartItem(product.value.id, variantId)
})

// Check if product is in cart
const isInCart = computed(() => {
  if (!product.value) return false
  const variantId = selectedVariant.value ? selectedVariant.value.id : null
  return cartStore.isInCart(product.value.id, variantId)
})

// Get quantity from cart
const getCartQuantity = computed(() => {
  const cartItem = getCartItem.value
  return cartItem ? cartItem.quantity : 0
})

// Update quantity in cart
const updateCartQuantity = (newQuantity) => {
  if (!product.value) return
  const minQuantity = product.value.sold_by_length ? 0.5 : 1
  if (newQuantity < minQuantity) return
  
  // Validate for sold_by_length products
  if (product.value.sold_by_length && !isValidLengthQuantity(newQuantity)) {
    quantityError.value = 'Proizvod se prodaje ceo ili na pola (npr. 1, 1.5, 2, 2.5). Uneta vrednost nije validna.'
    // Round to nearest valid value (whole or whole + 0.5)
    const whole = Math.floor(newQuantity)
    const decimal = newQuantity % 1
    newQuantity = decimal < 0.25 ? whole : (decimal < 0.75 ? whole + 0.5 : whole + 1)
    // Clear error after a short delay
    setTimeout(() => {
      quantityError.value = null
    }, 3000)
  } else {
    quantityError.value = null
  }
  
  const variantId = selectedVariant.value ? selectedVariant.value.id : null
  const cartId = variantId 
    ? `${product.value.id}-${variantId}`
    : product.value.id
  
  cartStore.updateQuantity(cartId, newQuantity)
}

const addToCart = () => {
  // Validate for sold_by_length products
  if (product.value.sold_by_length && !isValidLengthQuantity(quantity.value)) {
    quantityError.value = 'Proizvod se prodaje ceo ili na pola (npr. 1, 1.5, 2, 2.5). Uneta vrednost nije validna.'
    // Round to nearest valid value (whole or whole + 0.5)
    const whole = Math.floor(quantity.value)
    const decimal = quantity.value % 1
    quantity.value = decimal < 0.25 ? whole : (decimal < 0.75 ? whole + 0.5 : whole + 1)
    // Clear error after a short delay
    setTimeout(() => {
      quantityError.value = null
    }, 3000)
    return
  }
  
  quantityError.value = null
  const cartItem = {
    ...product.value,
    selectedVariant: selectedVariant.value
  }
  cartStore.add(cartItem, quantity.value)

  // Reset quantity after adding
  quantity.value = product.value.sold_by_length ? 0.5 : 1
  // Don't redirect - stay on page so user can add more variants or change quantity
}

const selectImage = (index) => {
  selectedImageIndex.value = index
}

const goBack = () => {
  router.push(storeRoute())
}

// Validate quantity for sold_by_length products (must be whole number or whole + 0.5)
const isValidLengthQuantity = (qty) => {
  if (qty <= 0) return false
  // Check if it's a whole number or whole + 0.5
  const decimalPart = qty % 1
  return decimalPart === 0 || decimalPart === 0.5
}

// Validate and update quantity
const validateAndUpdateQuantity = (newQuantity) => {
  if (product.value?.sold_by_length && !isValidLengthQuantity(newQuantity)) {
    quantityError.value = 'Proizvod se prodaje ceo ili na pola (npr. 1, 1.5, 2, 2.5). Uneta vrednost nije validna.'
    // Round to nearest valid value (whole or whole + 0.5)
    const whole = Math.floor(newQuantity)
    const decimal = newQuantity % 1
    quantity.value = decimal < 0.25 ? whole : (decimal < 0.75 ? whole + 0.5 : whole + 1)
    // Clear error after a short delay
    setTimeout(() => {
      quantityError.value = null
    }, 3000)
  } else {
    quantityError.value = null
    quantity.value = newQuantity
  }
}

const getQtyStep = () => {
  if (product.value?.store === 'ambalaza') {
    return getAmbalazaQuantityStep(product.value, selectedVariant.value)
  }
  return product.value?.sold_by_length ? 0.5 : 1
}

const getQtyMin = () => {
  if (product.value?.store === 'ambalaza') {
    return getAmbalazaMinQuantity(product.value, selectedVariant.value)
  }
  return product.value?.sold_by_length ? 0.5 : 1
}

// Get length_per_unit from variant or product
const getVariantLength = () => {
  if (selectedVariant.value) {
    // Use effective_length_per_unit if available (from backend), otherwise length_per_unit, otherwise product's length
    if (selectedVariant.value.effective_length_per_unit) {
      return parseFloat(selectedVariant.value.effective_length_per_unit)
    }
    if (selectedVariant.value.length_per_unit) {
      return parseFloat(selectedVariant.value.length_per_unit)
    }
  }
  return product.value?.length_per_unit ? parseFloat(product.value.length_per_unit) : null
}

const onPageShow = (event) => {
  if (event.persisted) {
    fetchProduct()
  }
}

const onVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    fetchProduct()
  }
}

// 'focus' pokriva slučaj kada su admin i shop u dva odvojena prozora
// jedan pored drugog (oba "visible", pa 'visibilitychange' ne okine).
const onWindowFocus = () => {
  fetchProduct()
}

watch(
  () => route.params.slugOrId,
  () => {
    fetchProduct()
  }
)

onMounted(() => {
  fetchProduct()
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
        <!-- min-h-screen: podnozje ostaje ispod prvog ekrana dok se proizvod ucitava, pa se ne pomera kad sadrzaj stigne -->
        <div v-if="loading" class="text-center py-20 min-h-screen">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#1565c0]"></div>
          <p class="text-gray-600 mt-4">Učitavanje proizvoda...</p>
        </div>

        <!-- Product Detail -->
        <div v-else-if="product" class="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8 lg:items-stretch">

            <!-- Gallery -->
            <div>
              <!-- Main Image -->
              <div class="relative bg-white rounded-xl overflow-hidden mb-4 aspect-square border border-gray-200">
                <ProductImage
                  v-if="images.length > 0"
                  :src="getImageUrl(images[selectedImageIndex].image)"
                  :alt="`${product.name} - ${product.category_name} - BetaPack kovano gvožđe`"
                  :widths="[480, 720, 1080]"
                  sizes="(min-width: 1024px) 560px, 90vw"
                  eager
                  priority
                  class="w-full h-full object-contain"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  <span class="text-8xl">📦</span>
                </div>

                <!-- Sale Badge -->
                <div v-if="isOnSale" class="absolute top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-full font-bold shadow-lg">
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
                  class="aspect-square rounded-lg overflow-hidden hover:ring-2 hover:ring-[#1976d2] transition cursor-pointer bg-white"
                >
                  <ProductImage
                    :src="getImageUrl(img.image)"
                    :alt="`${product.name} - Slika ${index + 1} - BetaPack`"
                    :widths="[120, 240, 360]"
                    sizes="(min-width: 1024px) 130px, 22vw"
                    class="w-full h-full object-contain"
                  />
                </button>
              </div>
            </div>

            <!-- Product Info -->
            <div class="flex flex-col min-h-[400px]">
              <!-- Category & SKU -->
              <div class="flex items-center justify-between mb-1">
                <p class="text-xs text-[#1976d2] font-semibold">{{ product.category_name }}</p>
                <p v-if="selectedVariant?.sku" class="text-xs text-gray-500 font-mono bg-gray-100 px-2 py-0.5 rounded">
                  {{ selectedVariant.sku }}
                </p>
              </div>

              <!-- Title -->
              <h1 class="text-xl lg:text-2xl font-bold text-gray-900 mb-3">{{ product.name }}</h1>

              <!-- Price -->
              <div class="mb-4">
                <p v-if="finalPrice == null" class="text-xl lg:text-2xl font-bold text-orange-600">Cena na upit</p>
                <div v-else-if="isOnSale" class="flex items-center gap-2">
                  <span class="text-base text-gray-400 line-through">
                    {{ formatPrice(selectedVariant ? selectedVariant.price : product.price) }}
                  </span>
                  <span class="text-xl lg:text-2xl font-bold text-red-600">{{ formatPrice(finalPrice) }}</span>
                </div>
                <div v-else>
                  <span class="text-xl lg:text-2xl font-bold text-green-700">{{ formatPrice(finalPrice) }}</span>
                </div>
                <p
                  v-if="product.store === 'ambalaza' && selectedVariant"
                  class="text-xs text-[#1976d2] font-semibold mt-1"
                >
                  {{ getAmbalazaSellingNote(product, selectedVariant) }}
                </p>
                <p
                  v-if="product.store === 'ambalaza' && isAmbalazaPackageMode(product, selectedVariant) && finalPrice != null"
                  class="text-xs text-gray-600 mt-1"
                >
                  Ukupno ({{ quantity }} kom.): {{ formatPrice(finalPrice * quantity) }}
                </p>
                <p v-if="finalPrice != null" class="text-xs text-gray-500 mt-1">Cena uključuje PDV</p>
              </div>

              <!-- Description -->
              <div class="mb-4">
                <h3 class="font-semibold text-sm text-gray-900 mb-1">Opis</h3>
                <p class="text-sm text-gray-700 leading-relaxed">{{ product.description }}</p>
              </div>

              <!-- Variants -->
              <div v-if="sortedVariants.length > 0" class="mb-4">
                <h3 class="font-semibold text-sm text-gray-900 mb-2">Izaberite dimenziju</h3>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="variant in sortedVariants"
                    :key="variant.id"
                    @click="selectedVariant = variant"
                    :class="[
                      selectedVariant?.id === variant.id
                        ? 'bg-[#1976d2] text-white ring-2 ring-[#1976d2]'
                        : 'bg-white text-gray-700 ring-1 ring-gray-300 hover:ring-[#1976d2]'
                    ]"
                    class="px-3 py-2 rounded-lg font-medium transition text-xs cursor-pointer"
                  >
                    <div>{{ variant.name }}</div>
                  </button>
                </div>
              </div>

              <!-- Quantity (samo dok proizvod nije u korpi — kad je u korpi, koristi se "Izmeni količinu" ispod) -->
              <div v-if="!isInCart" class="mb-3 w-full">
                <h3 class="font-semibold text-sm text-gray-900 mb-2">Količina</h3>
                <div class="flex items-center gap-1.5 w-full bg-gray-100 rounded-lg p-1">
                  <button
                    @click="validateAndUpdateQuantity(Math.max(getQtyMin(), quantity - getQtyStep()))"
                    class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm flex items-center justify-center"
                  >
                    −
                  </button>
                  <input
                    :value="quantity"
                    @input="validateAndUpdateQuantity(parseFloat($event.target.value) || getQtyMin())"
                    type="number"
                    :min="getQtyMin()"
                    :step="getQtyStep()"
                    class="flex-1 min-w-0 w-full text-sm font-semibold tabular-nums text-center text-gray-900 bg-white border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-[#1976d2] focus:outline-none"
                  />
                  <button
                    @click="validateAndUpdateQuantity(quantity + getQtyStep())"
                    class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm flex items-center justify-center"
                  >
                    +
                  </button>
                </div>
                <p v-if="product.sold_by_length" class="text-xs text-blue-600 font-semibold italic mt-2">
                  ℹ️ Proizvodi se prodaju po komadu (1 kom = {{ getVariantLength() || product.length_per_unit || 6 }} m), uz mogućnost kupovine celog ili pola komada ({{ ((getVariantLength() || product.length_per_unit || 6) / 2).toFixed(1) }} m).
                </p>
                <p v-if="quantityError" class="text-xs text-red-600 font-semibold italic mt-1">
                  ❌ {{ quantityError }}
                </p>
                <p v-if="product.sold_by_length && quantity" class="text-xs text-green-600 font-semibold mt-1">
                  📏 Izabrano je {{ (quantity * (getVariantLength() || product.length_per_unit || 6)).toFixed(2) }} metara
                </p>
              </div>

              <!-- Additional Info -->
              <div class="mb-4 pb-4 border-b space-y-2 text-xs text-gray-600">
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

              <!-- Add to Cart / Update Quantity - Fixed at Bottom -->
              <div class="space-y-2">
                <!-- If product is in cart, show quantity controls -->
                <div v-if="isInCart" class="space-y-2">
                  <div class="mb-2">
                    <h3 class="font-semibold text-sm text-gray-900">Izmeni količinu</h3>
                  </div>
                  <div class="flex items-center gap-1.5 w-full bg-gray-100 rounded-lg p-1">
                    <button
                      @click="updateCartQuantity(getCartQuantity - getQtyStep())"
                      :disabled="getCartQuantity <= getQtyMin()"
                      class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      −
                    </button>
                    <input
                      :value="getCartQuantity"
                      @input="updateCartQuantity(parseFloat($event.target.value) || getQtyMin())"
                      @blur="updateCartQuantity(Math.max(getQtyMin(), parseFloat($event.target.value) || getQtyMin()))"
                      type="number"
                      :min="getQtyMin()"
                      :step="getQtyStep()"
                      class="flex-1 min-w-0 w-full text-sm font-semibold tabular-nums text-center text-gray-900 bg-white border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-[#1976d2] focus:outline-none"
                    />
                    <button
                      @click="updateCartQuantity(getCartQuantity + getQtyStep())"
                      class="w-8 h-8 shrink-0 bg-white rounded-md hover:bg-gray-200 transition text-sm font-bold cursor-pointer shadow-sm flex items-center justify-center"
                    >
                      +
                    </button>
                  </div>
                  <p v-if="product.sold_by_length" class="text-xs text-blue-600 font-semibold italic">
                    📏 Izabrano je {{ (getCartQuantity * (getVariantLength() || product.length_per_unit || 6)).toFixed(2) }} metara
                  </p>
                  <p v-if="quantityError" class="text-xs text-red-600 font-semibold italic mt-1">
                    ❌ {{ quantityError }}
                  </p>
                </div>
                <!-- If product is not in cart, show add button -->
                <button
                  v-else
                  @click="addToCart"
                  class="w-full bg-[#1976d2] hover:bg-[#1565c0] text-white font-bold py-2.5 rounded-lg transition text-sm shadow-md hover:shadow-lg cursor-pointer"
                >
                  🛒 Dodaj u korpu
                </button>
                
                <!-- Link to Cart/Checkout -->
                <router-link
                  to="/cart"
                  class="block w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-bold py-2.5 rounded-lg transition-all text-sm shadow-md hover:shadow-lg cursor-pointer text-center"
                >
                  🛍️ Idi na korpu i naruči
                </router-link>

                <button
                  @click="router.push(storeRoute('/kontakt'))"
                  class="w-full bg-white hover:bg-gray-50 text-gray-900 font-semibold py-2.5 rounded-lg border border-gray-300 transition cursor-pointer text-sm"
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
