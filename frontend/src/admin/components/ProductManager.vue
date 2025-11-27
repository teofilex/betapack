<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useProductStore } from '@/admin/store/products'
import { useProductStore as useUserProductStore } from '@/store/products'
import { useCategoryStore } from '@/admin/store/categories'
import { useSubcategoryStore } from '@/admin/store/subcategories'
import { useAuthStore } from '@/store/auth'
import ProductDetailModal from './ProductDetailModal.vue'
import ProductVariantManager from './ProductVariantManager.vue'
import ProductImageManager from './ProductImageManager.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import AdminModal from './AdminModal.vue'
import { api } from '@/services/api'
import { getImageUrl } from '@/composables/useImageUrl'

const showConfirm = ref(false)
const confirmMessage = ref("")
const confirmAction = ref(null)

const openConfirm = (msg, action) => {
  confirmMessage.value = msg
  confirmAction.value = action
  showConfirm.value = true
}

const closeConfirm = () => {
  showConfirm.value = false
  confirmMessage.value = ""
  confirmAction.value = null
}

const doConfirm = () => {
  if (confirmAction.value) confirmAction.value()
  closeConfirm()
}
const emit = defineEmits(['update-count'])

const productStore = useProductStore()
const userProductStore = useUserProductStore()
const categoryStore = useCategoryStore()
const subcategoryStore = useSubcategoryStore()

// Detail modal
const showDetailModal = ref(false)
const selectedProduct = ref(null)

// UI
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const error = ref('')
const loading = ref(false)

const filterCategory = ref('')
const filterSubcategory = ref('')
const searchQuery = ref('')

// Tab navigation (for editing mode)
const currentTab = ref('basic') // 'basic', 'variants', 'images'

// Reset subcategory when category changes
watch(filterCategory, () => {
  filterSubcategory.value = ''
})

// Form
const form = ref({
  id: null,
  name: '',
  description: '',
  price: '',
  category: '',
  subcategory: '',
  on_sale: false,
  sale_price: '',
  featured: false,
  in_stock: true,
  stock_quantity: 0
})

// Stock management
const showStockModal = ref(false)
const stockProduct = ref(null)
const stockQuantityChange = ref(0)
const stockOperation = ref('add') // 'add' or 'subtract'

// Images and variants for new product
const productImages = ref([])
const productVariants = ref([])
const showVariantForm = ref(false)
const editingVariant = ref(null)
const variantForm = ref({
  name: '',
  price: 0,
  on_sale: false,
  sale_price: null,
  sku: '',
  in_stock: true,
  stock_quantity: 0
})

// Filtered subcategories
const filteredSubcategories = computed(() => {
  if (!form.value.category) return []
  return subcategoryStore.list.filter(s => s.category === form.value.category)
})

// Filtered products
const filteredProducts = computed(() => {
  let result = [...productStore.list]

  if (filterCategory.value) {
    result = result.filter(p => Number(p.category) === Number(filterCategory.value))
  }

  if (filterSubcategory.value) {
    result = result.filter(p => p.subcategory && Number(p.subcategory) === Number(filterSubcategory.value))
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      p =>
        p.name.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        (p.category_name && p.category_name.toLowerCase().includes(q)) ||
        (p.subcategory_name && p.subcategory_name.toLowerCase().includes(q))
    )
  }

  return result
})

// Price formatting
const formatPrice = price =>
  new Intl.NumberFormat('sr-RS', {
    style: 'currency',
    currency: 'RSD'
  }).format(price)

// Modal
const openAddModal = () => {
  if (categoryStore.list.length === 0) {
    openConfirm('Najpre dodaj kategoriju!', null)
    return
  }

  isEditing.value = false
  form.value = {
    id: null,
    name: '',
    description: '',
    price: '',
    category: '',
    subcategory: '',
    on_sale: false,
    sale_price: '',
    featured: false,
    in_stock: true,
    stock_quantity: 0
  }
  productImages.value = []
  productVariants.value = []
  showVariantForm.value = false
  editingVariant.value = null

  showModal.value = true
}

const openEditModal = product => {
  isEditing.value = true
  form.value = {
    ...product,
    in_stock: product.in_stock !== undefined ? product.in_stock : true,
    stock_quantity: product.stock_quantity || 0
  }
  currentTab.value = 'basic' // Reset to basic tab
  showModal.value = true
}

// Stock management
const openStockModal = (product) => {
  stockProduct.value = product
  stockQuantityChange.value = 0
  stockOperation.value = 'add'
  showStockModal.value = true
}

const closeStockModal = () => {
  showStockModal.value = false
  stockProduct.value = null
  stockQuantityChange.value = 0
  stockOperation.value = 'add'
}

const updateStockQuantity = async () => {
  if (!stockProduct.value || stockQuantityChange.value <= 0) return
  
  try {
    const authStore = useAuthStore()
    const authHeaders = { Authorization: `Bearer ${authStore.accessToken}` }
    
    const currentQuantity = stockProduct.value.stock_quantity || 0
    let newQuantity
    if (stockOperation.value === 'add') {
      newQuantity = currentQuantity + stockQuantityChange.value
    } else {
      newQuantity = Math.max(0, currentQuantity - stockQuantityChange.value)
    }
    
    await api.patch(`products/${stockProduct.value.id}/`, {
      stock_quantity: newQuantity,
      in_stock: newQuantity > 0
    }, {
      headers: authHeaders
    })
    
    // Refresh products
    await productStore.fetch()
    closeStockModal()
  } catch (err) {
    console.error('Error updating stock:', err)
    error.value = err.response?.data?.detail || 'Greška pri ažuriranju količine'
  }
}

const closeModal = () => {
  showModal.value = false
  error.value = ''
  productImages.value = []
  productVariants.value = []
  showVariantForm.value = false
  editingVariant.value = null
}

// Image handling
const handleImageSelect = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        productImages.value.push({
          file: file,
          preview: e.target.result,
          is_primary: productImages.value.length === 0
        })
      }
      reader.readAsDataURL(file)
    }
  })
  event.target.value = '' // Reset input
}

const removeImage = (index) => {
  productImages.value.splice(index, 1)
  // If we removed the primary image, make the first one primary
  if (productImages.value.length > 0 && !productImages.value.some(img => img.is_primary)) {
    productImages.value[0].is_primary = true
  }
}

const setPrimaryImage = (index) => {
  productImages.value.forEach((img, i) => {
    img.is_primary = i === index
  })
}

// Variant handling
const openVariantForm = (variant = null) => {
  if (variant) {
    editingVariant.value = variant
    variantForm.value = { ...variant }
  } else {
    editingVariant.value = null
    variantForm.value = {
      name: '',
      price: 0,
      on_sale: false,
      sale_price: null,
      sku: '',
      in_stock: true,
      stock_quantity: 0
    }
  }
  showVariantForm.value = true
}

const closeVariantForm = () => {
  showVariantForm.value = false
  editingVariant.value = null
}

const saveVariant = () => {
  if (!variantForm.value.name.trim()) {
    openConfirm('Naziv varijante je obavezan!', null)
    return
  }

  if (editingVariant.value) {
    const index = productVariants.value.findIndex(v => v === editingVariant.value)
    if (index !== -1) {
      productVariants.value[index] = { ...variantForm.value }
    }
  } else {
    productVariants.value.push({ ...variantForm.value })
  }
  closeVariantForm()
}

const removeVariant = (variant) => {
  const index = productVariants.value.indexOf(variant)
  if (index !== -1) {
    productVariants.value.splice(index, 1)
  }
}

// Save
const saveProduct = async () => {
  saving.value = true
  error.value = ''

  try {
    const data = {
      name: form.value.name,
      description: form.value.description,
      price: parseFloat(form.value.price),
      category: form.value.category,
      subcategory: form.value.subcategory || null,
      on_sale: form.value.on_sale,
      sale_price:
        form.value.on_sale && form.value.sale_price
          ? parseFloat(form.value.sale_price)
          : null,
      featured: form.value.featured || false,
      in_stock: form.value.in_stock !== undefined ? form.value.in_stock : true,
      stock_quantity: form.value.stock_quantity || 0
    }

    let productId
    const authStore = useAuthStore()
    const authHeaders = { Authorization: `Bearer ${authStore.accessToken}` }

    if (isEditing.value) {
      await productStore.update(form.value.id, data)
      productId = form.value.id
    } else {
      // Create product and get ID from response
      const response = await api.post('products/', data, {
        headers: authHeaders
      })
      productId = response.data.id
      await productStore.fetch() // Refresh list
    }

    // Upload images if any
    if (productImages.value.length > 0 && productId) {
      for (let i = 0; i < productImages.value.length; i++) {
        const imageData = productImages.value[i]
        const formData = new FormData()
        formData.append('image', imageData.file)
        formData.append('product', productId)
        formData.append('is_primary', imageData.is_primary)

        try {
          await api.post('product-images/', formData, {
            headers: { 
              ...authHeaders,
              'Content-Type': 'multipart/form-data' 
            }
          })
        } catch (err) {
          console.error('Error uploading image:', err)
          const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Greška pri upload-u slike.'
          error.value = errorMsg
          throw err // Re-throw da se vidi u konzoli
        }
      }
    }

    // Create variants if any
    if (productVariants.value.length > 0 && productId) {
      for (const variant of productVariants.value) {
        try {
          await api.post('product-variants/', {
            product: productId,
            ...variant
          }, {
            headers: authHeaders
          })
        } catch (err) {
          console.error('Error creating variant:', err)
          const errorMsg = err.response?.data?.detail || err.response?.data?.message || JSON.stringify(err.response?.data) || 'Greška pri kreiranju varijante.'
          error.value = errorMsg
          throw err // Re-throw da se vidi u konzoli
        }
      }
    }

    emit('update-count')
    // Osveži proizvode u user store-u da se prikažu nove slike
    await userProductStore.fetchProducts()
    closeModal()
  } catch (err) {
    console.error(err)
    error.value = 'Greška pri čuvanju proizvoda.'
  } finally {
    saving.value = false
  }
}

// Delete
const deleteProduct = (product) => {
  openConfirm(
    `Da li želiš da obrišeš proizvod "${product.name}"?`,
    async () => {
      try {
        await productStore.remove(product.id)
        emit('update-count')
      } catch (err) {
        console.error(err)
        const errorMsg = err.response?.data?.detail || err.response?.data?.message || 'Ne može da se obriše proizvod! Proizvod možda se koristi u narudžbinama.'
        openConfirm(errorMsg, null)
      }
    }
  )
}


// Detail modal functions
const openDetailModal = (product) => {
  selectedProduct.value = product
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedProduct.value = null
}

const handleDetailUpdate = async () => {
  await productStore.fetch()
  emit('update-count')
}

// Handle updates from variant/image managers in tabs
const handleTabUpdate = async () => {
  await productStore.fetch()
  await userProductStore.fetchProducts()
  emit('update-count')
}

// On load
onMounted(async () => {
  loading.value = true
  await categoryStore.fetch()
  await subcategoryStore.fetch()
  await productStore.fetch()
  loading.value = false
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 mb-1">📦 Proizvodi</h2>
        <p class="text-xs text-gray-500 font-medium">Upravljajte proizvodima u vašoj prodavnici</p>
      </div>

      <button
        @click="openAddModal"
        class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white rounded-lg text-sm font-semibold shadow-md hover:shadow-lg transition-all cursor-pointer flex items-center gap-1.5"
      >
        <span class="text-base">➕</span>
        <span>Dodaj Proizvod</span>
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl shadow-lg border-2 border-gray-200 p-6 mb-8">
      <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <span>🔍</span>
        <span>Filteri i pretraga</span>
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <!-- Search -->
        <div>
          <label class="block text-sm font-bold text-gray-700 mb-2">🔎 Pretraga</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Pretraži proizvode..."
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-[#1976d2] focus:border-[#1976d2] transition shadow-sm"
          />
        </div>

        <!-- Category Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Kategorija</label>
          <select
            v-model="filterCategory"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1976d2] focus:border-transparent cursor-pointer"
          >
            <option value="">Sve kategorije</option>
            <option v-for="cat in categoryStore.list" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- Subcategory Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Podkategorija</label>
          <select
            v-model="filterSubcategory"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1976d2] focus:border-transparent cursor-pointer"
            :disabled="!filterCategory"
          >
            <option value="">Sve podkategorije</option>
            <option
              v-for="subcat in subcategoryStore.list.filter(s => s.category == filterCategory)"
              :key="subcat.id"
              :value="subcat.id"
            >
              {{ subcat.name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-16">
      <div class="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-[#3555e4] mb-4"></div>
      <p class="text-gray-600 text-lg font-semibold">Učitavanje proizvoda...</p>
    </div>

    <!-- List -->
    <div
      v-else-if="Array.isArray(filteredProducts) && filteredProducts.length > 0"
      class="grid grid-cols-[repeat(auto-fill,minmax(380px,1fr))] gap-6"
    >
      <div
        v-for="product in filteredProducts"
        :key="product.id"
        class="bg-white border-2 border-gray-200 rounded-2xl p-6 hover:shadow-xl hover:border-[#1976d2] transition-all duration-300 transform hover:scale-[1.02] group"
      >
        <!-- Header -->
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1">
            <h3 class="text-xl font-bold text-gray-900 mb-1 line-clamp-2">{{ product.name }}</h3>
            <div class="flex items-center gap-2 mt-2">
              <span class="text-sm font-semibold text-[#1976d2]">
                📁 {{ product.category_name || 'Bez kategorije' }}
              </span>
              <span v-if="product.subcategory_name" class="text-sm text-gray-500">
                / {{ product.subcategory_name }}
              </span>
            </div>
          </div>

          <span
            v-if="product.on_sale"
            class="px-4 py-2 bg-red-500 text-white rounded-xl text-xs font-bold shadow-lg whitespace-nowrap"
          >
            🔥 AKCIJA
          </span>
        </div>

        <!-- Description -->
        <p class="text-gray-600 text-sm mt-3 mb-4 line-clamp-2 leading-relaxed">
          {{ product.description }}
        </p>

        <!-- Price -->
        <div class="mb-4 pb-4 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <span v-if="product.on_sale" class="line-through text-gray-400 text-lg">
              {{ formatPrice(product.price) }}
            </span>
            <span class="text-2xl font-bold text-green-600">
              {{ formatPrice(product.current_price) }}
            </span>
          </div>
        </div>

        <!-- Stock Quantity Display -->
        <div class="mb-4 flex items-center justify-between bg-gray-50 p-4 rounded-xl border border-gray-200">
          <div class="flex items-center gap-2">
            <span class="text-lg">📦</span>
            <div>
              <span class="text-xs font-semibold text-gray-600 uppercase">Količina:</span>
              <span
                class="text-lg font-bold ml-2"
                :class="(product.stock_quantity || 0) > 0 ? 'text-green-600' : 'text-gray-400'"
              >
                {{ (product.stock_quantity !== undefined && product.stock_quantity !== null) ? (product.stock_quantity > 0 ? product.stock_quantity : '0') : '∞ Neograničeno' }}
              </span>
            </div>
          </div>
          <button
            @click.stop="openStockModal(product)"
            class="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-xs font-medium cursor-pointer shadow-sm hover:shadow transition-all"
          >
            ➕ Dodaj
          </button>
        </div>

        <!-- Slike i Varijante Pregled -->
        <div class="mb-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
          <!-- Slike -->
          <div class="mb-3">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-gray-700 uppercase flex items-center gap-1">
                🖼️ Slike
              </span>
              <span class="text-xs font-bold text-[#1976d2]">
                {{ product.images?.length || 0 }}
              </span>
            </div>
            <div v-if="product.images && product.images.length > 0" class="flex gap-2 overflow-x-auto">
              <div
                v-for="img in product.images.slice(0, 4)"
                :key="img.id"
                class="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0 border border-gray-300"
              >
                <img
                  :src="getImageUrl(img.image)"
                  :alt="product.name"
                  class="w-full h-full object-contain bg-white"
                />
              </div>
              <div v-if="product.images.length > 4" class="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
                +{{ product.images.length - 4 }}
              </div>
            </div>
            <p v-else class="text-xs text-gray-400">Nema slika</p>
          </div>

          <!-- Varijante -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-semibold text-gray-700 uppercase flex items-center gap-1">
                📐 Varijante
              </span>
              <span class="text-xs font-bold text-[#1976d2]">
                {{ product.variants?.length || 0 }}
              </span>
            </div>
            <div v-if="product.variants && product.variants.length > 0" class="flex flex-wrap gap-1">
              <span
                v-for="variant in product.variants.slice(0, 3)"
                :key="variant.id"
                class="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-medium text-gray-700"
              >
                {{ variant.name }}
              </span>
              <span v-if="product.variants.length > 3" class="px-2 py-1 bg-gray-200 rounded text-xs font-bold text-gray-600">
                +{{ product.variants.length - 3 }}
              </span>
            </div>
            <p v-else class="text-xs text-gray-400">Nema varijanti</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 mt-4">
          <button
            @click="openDetailModal(product)"
            class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg text-xs font-medium cursor-pointer shadow-sm hover:shadow transition-all flex items-center justify-center gap-1.5"
          >
            <span class="text-sm">🎨</span>
            <span>Varijante/Slike</span>
          </button>

          <button
            @click="openEditModal(product)"
            class="px-4 py-2.5 bg-[#1976d2] hover:bg-[#1565c0] text-white rounded-lg text-sm font-medium cursor-pointer shadow-sm hover:shadow transition-all"
          >
            ✏️ Izmeni
          </button>

          <button
            @click="deleteProduct(product)"
            class="px-4 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium cursor-pointer shadow-sm hover:shadow transition-all"
          >
            🗑️ Obriši
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="py-20 text-center">
      <div class="inline-block bg-gray-100 rounded-full p-8 mb-4">
        <span class="text-6xl">📦</span>
      </div>
      <p class="text-xl font-bold text-gray-600 mb-2">
        Nema proizvoda
      </p>
      <p class="text-gray-500 mb-6">Dodajte prvi proizvod da započnete!</p>
      <button
        @click="openAddModal"
        class="px-6 py-3 bg-[#1976d2] hover:bg-[#1565c0] text-white rounded-xl font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 cursor-pointer"
      >
        ➕ Dodaj Prvi Proizvod
      </button>
    </div>

    <!-- MODAL -->
    <AdminModal
      :show="showModal"
      :title="isEditing ? 'Izmeni Proizvod' : 'Novi Proizvod'"
      max-width="max-w-[750px]"
      @close="closeModal"
    >
      <!-- Tab Navigation (only when editing) -->
      <div v-if="isEditing" class="flex gap-2 mb-6 border-b-2 border-gray-200">
        <button
          type="button"
          @click="currentTab = 'basic'"
          :class="currentTab === 'basic'
            ? 'border-b-4 border-[#1976d2] text-[#1976d2] font-bold'
            : 'text-gray-600 hover:text-gray-800'"
          class="px-6 py-3 transition-all cursor-pointer"
        >
          📝 Osnovni podaci
        </button>
        <button
          type="button"
          @click="currentTab = 'variants'"
          :class="currentTab === 'variants'
            ? 'border-b-4 border-[#1976d2] text-[#1976d2] font-bold'
            : 'text-gray-600 hover:text-gray-800'"
          class="px-6 py-3 transition-all cursor-pointer"
        >
          📐 Varijante
        </button>
        <button
          type="button"
          @click="currentTab = 'images'"
          :class="currentTab === 'images'
            ? 'border-b-4 border-[#1976d2] text-[#1976d2] font-bold'
            : 'text-gray-600 hover:text-gray-800'"
          class="px-6 py-3 transition-all cursor-pointer"
        >
          🖼️ Slike
        </button>
      </div>

      <!-- Basic Info Tab (or full form for new products) -->
      <form v-show="!isEditing || currentTab === 'basic'" @submit.prevent="saveProduct" class="space-y-6">
        <!-- NAME -->
        <div>
          <label class="block mb-2 font-medium text-gray-800">Naziv *</label>
          <input
            v-model="form.name"
            required
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200 
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
        </div>

        <!-- DESCRIPTION -->
        <div>
          <label class="block mb-2 font-medium text-gray-800">Opis *</label>
          <textarea
            v-model="form.description"
            rows="4"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200 
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition resize-none shadow-sm"
          ></textarea>
        </div>

        <!-- PRICE -->
        <div>
          <label class="block mb-2 font-medium text-gray-800">Cena (RSD) *</label>
          <input
            v-model="form.price"
            type="number"
            required
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
        </div>

        <!-- CATEGORY -->
        <div>
          <label class="block mb-2 font-medium text-gray-800">Kategorija *</label>
          <select
            v-model="form.category"
            required
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm cursor-pointer"
          >
            <option value="">Izaberi kategoriju</option>
            <option v-for="c in categoryStore.list" :value="c.id" :key="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>

        <!-- SUBCATEGORY -->
        <div>
          <label class="block mb-2 font-medium text-gray-800">Podkategorija</label>
          <select
            v-model="form.subcategory"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm cursor-pointer"
          >
            <option value="">Bez podkategorije</option>
            <option
              v-for="s in filteredSubcategories"
              :value="s.id"
              :key="s.id"
            >
              {{ s.name }}
            </option>
          </select>
        </div>

        <!-- On sale -->
        <label class="flex items-center gap-2 mt-2 cursor-pointer">
          <input v-model="form.on_sale" type="checkbox" class="cursor-pointer" />
          <span class="text-gray-800 font-medium cursor-pointer">Proizvod je na akciji</span>
        </label>

        <!-- Featured -->
        <label class="flex items-center gap-2 mt-2 cursor-pointer">
          <input v-model="form.featured" type="checkbox" class="cursor-pointer" />
          <span class="text-gray-800 font-medium cursor-pointer">Preporučeni proizvod</span>
        </label>

        <!-- Stock Management -->
        <div class="border-t pt-6 mt-6">
          <label class="flex items-center gap-2 mb-4 cursor-pointer">
            <input v-model="form.in_stock" type="checkbox" class="cursor-pointer" />
            <span class="text-gray-800 font-medium cursor-pointer">Proizvod je na stanju</span>
          </label>

          <div>
            <label class="block mb-2 font-medium text-gray-800">Količina na stanju (opciono)</label>
            <input
              v-model.number="form.stock_quantity"
              type="number"
              min="0"
              placeholder="0 = neograničeno"
              class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                     focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
            />
            <p class="text-xs text-gray-500 mt-1">Ostavite 0 za neograničenu količinu</p>
          </div>
        </div>

        <div v-if="form.on_sale">
          <label class="block font-medium mt-3 mb-1 text-gray-800">Akcijska cena *</label>
          <input
            v-model="form.sale_price"
            type="number"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
        </div>

        <!-- SLIKE PROIZVODA (samo za nove proizvode) -->
        <div v-if="!isEditing" class="border-t pt-6 mt-6">
          <h4 class="font-semibold text-lg mb-4 text-gray-800">Slike proizvoda</h4>
          
          <!-- Upload -->
          <div class="mb-4">
            <input
              type="file"
              @change="handleImageSelect"
              accept="image/*"
              multiple
              class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200 cursor-pointer"
            />
            <p class="text-xs text-gray-500 mt-1">Možete odabrati više slika odjednom</p>
          </div>

          <!-- Preview slika -->
          <div v-if="productImages.length > 0" class="grid grid-cols-3 gap-4 mb-4">
            <div
              v-for="(img, index) in productImages"
              :key="index"
              class="relative border rounded-lg overflow-hidden group"
            >
              <img
                :src="img.preview"
                :alt="`Preview ${index + 1}`"
                class="w-full h-32 object-cover"
              />
              
              <div v-if="img.is_primary" class="absolute top-2 left-2 bg-green-500 text-white px-2 py-1 text-xs rounded">
                Glavna
              </div>

              <div class="absolute bottom-0 left-0 right-0 bg-black/70 p-2 flex gap-2 opacity-0 group-hover:opacity-100 transition">
                <button
                  v-if="!img.is_primary"
                  @click="setPrimaryImage(index)"
                  type="button"
                  class="flex-1 px-2 py-1 bg-green-600 text-white text-xs rounded cursor-pointer"
                >
                  Glavna
                </button>
                <button
                  @click="removeImage(index)"
                  type="button"
                  class="px-2 py-1 bg-red-600 text-white text-xs rounded cursor-pointer"
                >
                  Obriši
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- VARIJANTE (samo za nove proizvode) -->
        <div v-if="!isEditing" class="border-t pt-6 mt-6">
          <div class="flex justify-between items-center mb-4">
            <h4 class="font-semibold text-lg text-gray-800">Varijante (Dimenzije)</h4>
            <button
              @click="openVariantForm()"
              type="button"
              class="px-4 py-2 bg-green-600 text-white rounded text-sm cursor-pointer"
            >
              + Dodaj varijantu
            </button>
          </div>

          <!-- Lista varijanti -->
          <div v-if="productVariants.length > 0" class="space-y-2 mb-4">
            <div
              v-for="(variant, index) in productVariants"
              :key="index"
              class="flex items-center justify-between border rounded-lg p-3 bg-gray-50"
            >
              <div>
                <p class="font-medium">{{ variant.name }}</p>
                <p class="text-sm text-gray-600">
                  SKU: {{ variant.sku || 'N/A' }} |
                  <span v-if="variant.on_sale" class="text-red-600">
                    <span class="line-through text-gray-400">{{ variant.price }} RSD</span>
                    <span class="ml-1 font-bold">{{ variant.sale_price }} RSD</span>
                    <span class="ml-1 text-xs bg-red-100 text-red-800 px-1 rounded">AKCIJA</span>
                  </span>
                  <span v-else class="text-green-600">{{ variant.price }} RSD</span>
                </p>
                <p class="text-xs" :class="variant.in_stock ? 'text-green-600' : 'text-red-600'">
                  {{ variant.in_stock ? `Na stanju: ${variant.stock_quantity}` : 'Nije na stanju' }}
                </p>
              </div>

              <div class="flex gap-2">
                <button
                  @click="openVariantForm(variant)"
                  type="button"
                  class="px-3 py-1 bg-[#1976d2] text-white rounded text-sm cursor-pointer"
                >
                  Izmeni
                </button>
                <button
                  @click="removeVariant(variant)"
                  type="button"
                  class="px-3 py-1 bg-red-500 text-white rounded text-sm cursor-pointer"
                >
                  Obriši
                </button>
              </div>
            </div>
          </div>

          <p v-if="productVariants.length === 0" class="text-gray-400 text-sm text-center py-4">
            Nema varijanti. Dodaj dimenzije/varijacije proizvoda.
          </p>
        </div>

        <!-- ERROR -->
        <p v-if="error" class="text-red-600 font-semibold">{{ error }}</p>

        <!-- BUTTONS (only show in basic tab when editing, always show for new products) -->
        <div v-if="!isEditing || currentTab === 'basic'" class="flex justify-end gap-4 pt-4">
          <button
            type="button"
            @click="closeModal"
            class="px-6 py-3 bg-gray-300 rounded-xl font-semibold hover:bg-gray-400 transition cursor-pointer"
          >
            Otkaži
          </button>

          <button
            type="submit"
            :disabled="saving"
            class="px-6 py-3 bg-[#1976d2] text-white rounded-xl font-semibold shadow
                   hover:bg-[#1565c0] transition cursor-pointer disabled:opacity-60"
          >
            {{ saving ? "Čuvanje..." : "Sačuvaj" }}
          </button>
        </div>
      </form>

      <!-- Variants Tab Content -->
      <div v-if="isEditing && currentTab === 'variants'" class="space-y-4">
        <ProductVariantManager
          :product-id="form.id"
          @updated="handleTabUpdate"
        />
      </div>

      <!-- Images Tab Content -->
      <div v-if="isEditing && currentTab === 'images'" class="space-y-4">
        <ProductImageManager
          :product-id="form.id"
          @updated="handleTabUpdate"
        />
      </div>
    </AdminModal>


    <!-- Detail Modal za varijante/slike -->
    <ProductDetailModal
      :show="showDetailModal"
      :product="selectedProduct"
      @close="closeDetailModal"
      @updated="handleDetailUpdate"
    />
    <!-- Variant Form Modal -->
    <AdminModal
      :show="showVariantForm"
      :title="editingVariant ? 'Izmeni varijantu' : 'Nova varijanta'"
      max-width="max-w-md"
      z-index="z-[2000]"
      @close="closeVariantForm"
    >
      <form @submit.prevent="saveVariant" class="space-y-4">
        <div>
          <label class="block font-medium mb-1 text-gray-800">Naziv (dimenzije) *</label>
          <input
            v-model="variantForm.name"
            required
            placeholder="npr. 180×135×18mm"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
        </div>

        <div>
          <label class="block font-medium mb-1 text-gray-800">SKU (šifra)</label>
          <input
            v-model="variantForm.sku"
            placeholder="npr. TACNA-70-180"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
        </div>

        <div>
          <label class="block font-medium mb-1 text-gray-800">Osnovna cena (RSD) *</label>
          <input
            v-model.number="variantForm.price"
            type="number"
            step="0.01"
            required
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
        </div>

        <div class="flex items-center gap-2 bg-yellow-50 p-3 rounded-lg">
          <input
            v-model="variantForm.on_sale"
            type="checkbox"
            id="product-variant-on-sale"
            class="cursor-pointer"
          />
          <label for="product-variant-on-sale" class="text-gray-800 font-medium cursor-pointer">Stavi na akciju</label>
        </div>

        <div v-if="variantForm.on_sale">
          <label class="block font-medium mb-1 text-gray-800">Akcijska cena (RSD) *</label>
          <input
            v-model.number="variantForm.sale_price"
            type="number"
            step="0.01"
            :required="variantForm.on_sale"
            class="w-full px-4 py-3 rounded-xl bg-red-50 border border-red-300
                   focus:ring-2 focus:ring-red-400 focus:outline-none transition shadow-sm"
          />
          <p class="text-xs text-red-600 mt-1">Akcijska cena mora biti niža od osnovne cene</p>
        </div>

        <div>
          <label class="block font-medium mb-1 text-gray-800">Količina na stanju</label>
          <input
            v-model.number="variantForm.stock_quantity"
            type="number"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="variantForm.in_stock"
            type="checkbox"
            id="variant-in-stock-form"
            class="cursor-pointer"
          />
          <label for="variant-in-stock-form" class="text-gray-800 font-medium cursor-pointer">Na stanju</label>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="closeVariantForm"
            class="px-6 py-3 bg-gray-300 rounded-xl font-semibold hover:bg-gray-400
                   transition cursor-pointer"
          >
            Otkaži
          </button>
          <button
            type="submit"
            class="px-6 py-3 bg-[#1976d2] text-white rounded-xl font-semibold shadow
                   hover:bg-[#1565c0] transition cursor-pointer"
          >
            Sačuvaj
          </button>
        </div>
      </form>
    </AdminModal>

    <ConfirmModal
      :show="showConfirm"
      :message="confirmMessage"
      title="Potvrda"
      confirmText="Obriši"
      cancelText="Odustani"
      @confirm="doConfirm"
      @cancel="closeConfirm"
    />

    <!-- Stock Management Modal -->
    <AdminModal
      :show="showStockModal"
      title="Upravljanje količinom na stanju"
      max-width="max-w-md"
      @close="closeStockModal"
    >
      <div v-if="stockProduct" class="space-y-5">
        <div class="bg-gray-50 p-4 rounded-xl">
          <p class="text-gray-700 mb-2">
            <span class="font-semibold">Proizvod:</span> {{ stockProduct.name }}
          </p>
          <p class="text-gray-700">
            <span class="font-semibold">Trenutna količina:</span> 
            <span class="text-2xl font-bold text-green-600 ml-2">
              {{ stockProduct.stock_quantity || 0 }}
            </span>
          </p>
        </div>

        <!-- Operation Selection -->
        <div>
          <label class="block mb-3 font-medium text-gray-800">Operacija</label>
          <div class="flex gap-3">
            <button
              @click="stockOperation = 'add'"
              :class="stockOperation === 'add' 
                ? 'bg-green-600 text-white shadow-md' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
              class="flex-1 px-4 py-3 rounded-xl font-medium transition-all cursor-pointer"
            >
              ➕ Dodaj
            </button>
            <button
              @click="stockOperation = 'subtract'"
              :class="stockOperation === 'subtract' 
                ? 'bg-red-600 text-white shadow-md' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
              class="flex-1 px-4 py-3 rounded-xl font-medium transition-all cursor-pointer"
            >
              ➖ Smanji
            </button>
          </div>
        </div>

        <div>
          <label class="block mb-2 font-medium text-gray-800">
            Količina za {{ stockOperation === 'add' ? 'dodavanje' : 'smanjenje' }} *
          </label>
          <input
            v-model.number="stockQuantityChange"
            type="number"
            min="1"
            placeholder="Unesite količinu"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-[#1976d2] focus:outline-none transition shadow-sm"
          />
          <p v-if="stockOperation === 'subtract' && stockProduct.stock_quantity" class="text-xs text-gray-500 mt-1">
            Nova količina: {{ Math.max(0, (stockProduct.stock_quantity || 0) - (stockQuantityChange || 0)) }}
          </p>
        </div>

        <div class="flex gap-3 pt-2">
          <button
            @click="updateStockQuantity"
            :disabled="!stockQuantityChange || stockQuantityChange <= 0"
            :class="stockOperation === 'add' 
              ? 'bg-green-600 hover:bg-green-700' 
              : 'bg-red-600 hover:bg-red-700'"
            class="flex-1 px-4 py-3 disabled:bg-gray-400 
                   text-white rounded-xl font-medium transition-all cursor-pointer shadow-md hover:shadow-lg"
          >
            {{ stockOperation === 'add' ? 'Dodaj količinu' : 'Smanji količinu' }}
          </button>
          <button
            @click="closeStockModal"
            class="px-4 py-3 bg-gray-300 hover:bg-gray-400 text-gray-800 rounded-xl font-medium transition-all cursor-pointer"
          >
            Odustani
          </button>
        </div>
      </div>
    </AdminModal>
  </div>
</template>
