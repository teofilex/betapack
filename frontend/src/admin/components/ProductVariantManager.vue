<script setup>
import { ref, watch, onMounted } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/store/auth'
import AdminModal from './AdminModal.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

const props = defineProps({
  productId: Number
})

const emit = defineEmits(['updated'])

const variants = ref([])
const showForm = ref(false)
const editing = ref(null)
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmAction = ref(null)
const variantToDelete = ref(null)

const form = ref({
  name: '',
  price: 0,
  on_sale: false,
  sale_price: null,
  sku: '',
  in_stock: true,
  stock_quantity: 0,
  length_per_unit: null
})

const fetchVariants = async () => {
  if (!props.productId) return
  try {
    const authStore = useAuthStore()
    const response = await api.get(`product-variants/?product_id=${props.productId}`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    variants.value = response.data
  } catch (error) {
    console.error('Error fetching variants:', error)
  }
}

const openForm = (variant = null) => {
  if (variant) {
    editing.value = variant.id
    form.value = { ...variant }
  } else {
    editing.value = null
    form.value = {
      name: '',
      price: 0,
      on_sale: false,
      sale_price: null,
      sku: '',
      in_stock: true,
      stock_quantity: 0,
      length_per_unit: null
    }
  }
  showForm.value = true
}

const closeForm = () => {
  showForm.value = false
  editing.value = null
}

const openConfirm = (msg, action) => {
  confirmMessage.value = msg
  confirmAction.value = action
  showConfirm.value = true
}

const closeConfirm = () => {
  showConfirm.value = false
  confirmMessage.value = ''
  confirmAction.value = null
  variantToDelete.value = null
}

const doConfirm = () => {
  if (confirmAction.value) confirmAction.value()
  closeConfirm()
}

const saveVariant = async () => {
  try {
    const authStore = useAuthStore()
    const authHeaders = { Authorization: `Bearer ${authStore.accessToken}` }
    const data = {
      product: props.productId,
      ...form.value
    }

    if (editing.value) {
      await api.patch(`product-variants/${editing.value}/`, data, {
        headers: authHeaders
      })
    } else {
      await api.post('product-variants/', data, {
        headers: authHeaders
      })
    }

    await fetchVariants()
    emit('updated')
    closeForm()
  } catch (error) {
    console.error('Save error:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Greška pri čuvanju varijante'
    openConfirm(errorMsg, null)
  }
}

const deleteVariant = (id) => {
  // Proveri da li je ovo poslednja varijanta
  if (variants.value.length <= 1) {
    openConfirm(
      'Ne možeš obrisati poslednju varijantu! Proizvod mora imati bar jednu varijantu.',
      null
    )
    return
  }

  const variant = variants.value.find(v => v.id === id)
  const variantName = variant ? variant.name : 'ovu varijantu'
  variantToDelete.value = id
  openConfirm(
    `Da li želiš da obrišeš varijantu "${variantName}"?`,
    async () => {
      try {
        const authStore = useAuthStore()
        await api.delete(`product-variants/${id}/`, {
          headers: { Authorization: `Bearer ${authStore.accessToken}` }
        })
        await fetchVariants()
        emit('updated')
      } catch (error) {
        console.error('Delete error:', error)
        const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Greška pri brisanju varijante. Varijanta možda se koristi u narudžbinama.'
        openConfirm(errorMsg, null)
      }
    }
  )
}

// Fetch na mount i kada se productId promeni
onMounted(() => {
  if (props.productId) {
    fetchVariants()
  }
})

watch(() => props.productId, (newId) => {
  if (newId) {
    fetchVariants()
  } else {
    variants.value = []
  }
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center mb-3">
      <h4 class="font-bold text-sm text-gray-900 px-1">Varijante (Dimenzije)</h4>
      <button
        @click="openForm()"
        class="px-4 py-2 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white rounded-lg text-xs font-semibold cursor-pointer transition-all shadow-md hover:shadow-lg flex items-center gap-1.5"
      >
        <span>➕</span>
        <span>Dodaj varijantu</span>
      </button>
    </div>

    <!-- Lista varijanti -->
    <div class="space-y-4">
      <TransitionGroup name="variant-list">
        <div
          v-for="variant in variants"
          :key="variant.id"
          class="flex items-center justify-between border rounded-lg p-4 bg-white hover:bg-blue-50 hover:shadow-md transition-all duration-200"
        >
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm text-gray-900 mb-1">{{ variant.name }}</p>
            <div class="flex flex-wrap gap-2.5 text-xs text-gray-600 mb-1.5">
              <span><strong>SKU:</strong> {{ variant.sku || 'N/A' }}</span>
              <span><strong>Cena:</strong>
                <span v-if="variant.on_sale" class="text-red-600">
                  <span class="line-through text-gray-400">{{ variant.price }} RSD</span>
                  <span class="ml-1 font-bold">{{ variant.sale_price }} RSD</span>
                  <span class="ml-1 bg-red-100 text-red-800 px-1.5 py-0.5 rounded text-[10px]">AKCIJA</span>
                </span>
                <span v-else class="text-green-600 font-medium">
                  {{ variant.price }} RSD
                </span>
              </span>
              <span v-if="variant.length_per_unit"><strong>Dužina:</strong> {{ variant.length_per_unit }}m</span>
            </div>
            <p class="text-xs mt-1.5 font-medium" :class="variant.in_stock ? 'text-green-600' : 'text-red-600'">
              {{ variant.in_stock ? `✅ Na stanju: ${variant.stock_quantity}` : '❌ Nije na stanju' }}
            </p>
          </div>

          <div class="flex gap-1.5 ml-3">
            <button
              @click="openForm(variant)"
              class="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium cursor-pointer transition-all flex items-center gap-1"
            >
              <span>✏️</span>
              <span>Izmeni</span>
            </button>
            <button
              @click="deleteVariant(variant.id)"
              :disabled="variants.length <= 1"
              :class="variants.length <= 1 
                ? 'px-2.5 py-1.5 bg-gray-400 text-white rounded text-xs font-medium cursor-not-allowed opacity-50 flex items-center gap-1' 
                : 'px-2.5 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium cursor-pointer transition-all flex items-center gap-1'"
              :title="variants.length <= 1 ? 'Ne možeš obrisati poslednju varijantu!' : 'Obriši varijantu'"
            >
              <span>🗑️</span>
              <span>Obriši</span>
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <p v-if="variants.length === 0" class="text-gray-400 text-center py-6 text-sm">
      Nema varijanti. Dodaj dimenzije/varijacije proizvoda.
    </p>

    <!-- MODAL za dodavanje/izmenu -->
    <AdminModal
      :show="showForm"
      :title="editing ? 'Izmeni varijantu' : 'Nova varijanta'"
      max-width="max-w-[400px]"
      z-index="z-[2000]"
      @close="closeForm"
    >
      <form @submit.prevent="saveVariant" class="space-y-4">
        <div>
          <label class="block text-[10px] font-medium mb-2 text-gray-800 px-1">Naziv (dimenzije) *</label>
          <input
            v-model="form.name"
            required
            placeholder="npr. 180×135×18mm"
            class="w-full px-2.5 py-1.5 rounded-lg bg-gray-100 border border-gray-200 text-xs
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div>
          <label class="block text-[10px] font-medium mb-2 text-gray-800 px-1">SKU (šifra)</label>
          <input
            v-model="form.sku"
            placeholder="npr. TACNA-70-180"
            class="w-full px-2.5 py-1.5 rounded-lg bg-gray-100 border border-gray-200 text-xs
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div>
          <label class="block text-[10px] font-medium mb-2 text-gray-800 px-1">Osnovna cena (RSD) *</label>
          <input
            v-model.number="form.price"
            type="number"
            step="0.01"
            required
            class="w-full px-2.5 py-1.5 rounded-lg bg-gray-100 border border-gray-200 text-xs
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div class="flex items-center gap-2 bg-yellow-50 p-2 rounded-lg">
          <input
            v-model="form.on_sale"
            type="checkbox"
            id="variant-on-sale"
            class="cursor-pointer"
          />
          <label for="variant-on-sale" class="text-gray-800 text-[10px] font-medium cursor-pointer px-1">Stavi na akciju</label>
        </div>

        <div v-if="form.on_sale">
          <label class="block text-[10px] font-medium mb-2 text-gray-800 px-1">Akcijska cena (RSD) *</label>
          <input
            v-model.number="form.sale_price"
            type="number"
            step="0.01"
            :required="form.on_sale"
            class="w-full px-2.5 py-1.5 rounded-lg bg-red-50 border border-red-300 text-xs
                   focus:ring-2 focus:ring-red-400 focus:outline-none transition shadow-sm"
          />
          <p class="text-[10px] text-red-600 mt-0.5 px-1">Akcijska cena mora biti niža od osnovne cene</p>
        </div>

        <div>
          <label class="block text-[10px] font-medium mb-2 text-gray-800 px-1">Količina na stanju</label>
          <input
            v-model.number="form.stock_quantity"
            type="number"
            class="w-full px-2.5 py-1.5 rounded-lg bg-gray-100 border border-gray-200 text-xs
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="form.in_stock"
            type="checkbox"
            id="variant-in-stock"
            class="cursor-pointer"
          />
          <label for="variant-in-stock" class="text-gray-800 text-[10px] font-medium cursor-pointer px-1">Na stanju</label>
        </div>

        <!-- Length per unit (only if product is sold by length) -->
        <div class="bg-blue-50 p-3 rounded-lg border border-blue-200">
          <label class="block text-[10px] font-medium mb-2 text-gray-800 px-1">Dužina 1 komada (u metrima) - Opciono</label>
          <input
            v-model.number="form.length_per_unit"
            type="number"
            step="0.1"
            min="0.1"
            placeholder="npr. 4.0 ili 6.0"
            class="w-full px-2.5 py-1.5 rounded-lg bg-white border border-gray-300 text-xs
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
          <p class="text-[10px] text-gray-600 mt-1 px-1">
            Unesite dužinu 1 komada za ovu varijantu (npr. 4.0 za 4m, 6.0 za 6m). 
            Ako ostavite prazno, koristiće se dužina iz proizvoda.
          </p>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            type="button"
            @click="closeForm"
            class="px-3 py-2 bg-gray-300 rounded-lg font-semibold hover:bg-gray-400
                   transition cursor-pointer text-xs"
          >
            Otkaži
          </button>
          <button
            type="submit"
            class="px-3 py-2 bg-blue-600 text-white rounded-lg font-semibold shadow
                   hover:bg-blue-700 transition cursor-pointer text-xs"
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
  </div>
</template>

<style scoped>
.variant-list-enter-active {
  transition: all 0.3s ease;
}

.variant-list-leave-active {
  transition: all 0.3s ease;
}

.variant-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.variant-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.variant-list-move {
  transition: transform 0.3s ease;
}
</style>
