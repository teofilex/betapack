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
  stock_quantity: 0
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
      stock_quantity: 0
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
    <div class="flex justify-between items-center mb-4">
      <h4 class="font-bold text-xl text-gray-900">Varijante (Dimenzije)</h4>
      <button
        @click="openForm()"
        class="px-5 py-2.5 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white rounded-lg text-sm font-semibold cursor-pointer transition-all shadow-md hover:shadow-lg"
      >
        ➕ Dodaj varijantu
      </button>
    </div>

    <!-- Lista varijanti -->
    <div class="space-y-3">
      <TransitionGroup name="variant-list">
        <div
          v-for="variant in variants"
          :key="variant.id"
          class="flex items-center justify-between border-2 rounded-xl p-4 bg-white hover:bg-blue-50 hover:shadow-lg transition-all duration-300 transform hover:scale-[1.02]"
        >
          <div class="flex-1">
            <p class="font-semibold text-lg text-gray-900 mb-1">{{ variant.name }}</p>
            <div class="flex flex-wrap gap-4 text-sm text-gray-600">
              <span><strong>SKU:</strong> {{ variant.sku || 'N/A' }}</span>
              <span><strong>Cena:</strong>
                <span v-if="variant.on_sale" class="text-red-600">
                  <span class="line-through text-gray-400">{{ variant.price }} RSD</span>
                  <span class="ml-2 font-bold">{{ variant.sale_price }} RSD</span>
                  <span class="ml-1 bg-red-100 text-red-800 px-2 py-0.5 rounded-full text-xs">AKCIJA</span>
                </span>
                <span v-else class="text-green-600 font-medium">
                  {{ variant.price }} RSD
                </span>
              </span>
            </div>
            <p class="text-sm mt-2 font-medium" :class="variant.in_stock ? 'text-green-600' : 'text-red-600'">
              {{ variant.in_stock ? `✅ Na stanju: ${variant.stock_quantity}` : '❌ Nije na stanju' }}
            </p>
          </div>

          <div class="flex gap-2 ml-4">
            <button
              @click="openForm(variant)"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium cursor-pointer transition-all shadow-md hover:shadow-lg"
            >
              ✏️ Izmeni
            </button>
            <button
              @click="deleteVariant(variant.id)"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium cursor-pointer transition-all shadow-md hover:shadow-lg"
            >
              🗑️ Obriši
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <p v-if="variants.length === 0" class="text-gray-400 text-center py-12 text-lg">
      Nema varijanti. Dodaj dimenzije/varijacije proizvoda.
    </p>

    <!-- MODAL za dodavanje/izmenu -->
    <AdminModal
      :show="showForm"
      :title="editing ? 'Izmeni varijantu' : 'Nova varijanta'"
      max-width="max-w-lg"
      z-index="z-[2000]"
      @close="closeForm"
    >
      <form @submit.prevent="saveVariant" class="space-y-4">
        <div>
          <label class="block font-medium mb-1 text-gray-800">Naziv (dimenzije) *</label>
          <input
            v-model="form.name"
            required
            placeholder="npr. 180×135×18mm"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div>
          <label class="block font-medium mb-1 text-gray-800">SKU (šifra)</label>
          <input
            v-model="form.sku"
            placeholder="npr. TACNA-70-180"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div>
          <label class="block font-medium mb-1 text-gray-800">Osnovna cena (RSD) *</label>
          <input
            v-model.number="form.price"
            type="number"
            step="0.01"
            required
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div class="flex items-center gap-2 bg-yellow-50 p-3 rounded-lg">
          <input
            v-model="form.on_sale"
            type="checkbox"
            id="variant-on-sale"
            class="cursor-pointer"
          />
          <label for="variant-on-sale" class="text-gray-800 font-medium cursor-pointer">Stavi na akciju</label>
        </div>

        <div v-if="form.on_sale">
          <label class="block font-medium mb-1 text-gray-800">Akcijska cena (RSD) *</label>
          <input
            v-model.number="form.sale_price"
            type="number"
            step="0.01"
            :required="form.on_sale"
            class="w-full px-4 py-3 rounded-xl bg-red-50 border border-red-300
                   focus:ring-2 focus:ring-red-400 focus:outline-none transition shadow-sm"
          />
          <p class="text-xs text-red-600 mt-1">Akcijska cena mora biti niža od osnovne cene</p>
        </div>

        <div>
          <label class="block font-medium mb-1 text-gray-800">Količina na stanju</label>
          <input
            v-model.number="form.stock_quantity"
            type="number"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
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
          <label for="variant-in-stock" class="text-gray-800 font-medium cursor-pointer">Na stanju</label>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <button
            type="button"
            @click="closeForm"
            class="px-6 py-3 bg-gray-300 rounded-xl font-semibold hover:bg-gray-400
                   transition cursor-pointer"
          >
            Otkaži
          </button>
          <button
            type="submit"
            class="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold shadow
                   hover:bg-blue-700 transition cursor-pointer"
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
