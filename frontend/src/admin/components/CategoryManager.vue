<script setup>
import { ref, onMounted } from 'vue'
import { useCategoryStore } from '@/admin/store/categories'
import ConfirmModal from '@/components/ConfirmModal.vue'
import AdminModal from './AdminModal.vue'

const emit = defineEmits(['update-count'])

const categoryStore = useCategoryStore()

// Confirm modal
const showConfirm = ref(false)
const confirmMessage = ref("")
const confirmAction = ref(null)

const openConfirm = (message, action) => {
  confirmMessage.value = message
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

// Form modal
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const error = ref('')

const form = ref({
  id: null,
  name: '',
  description: ''
})

const openAddModal = () => {
  isEditing.value = false
  form.value = { id: null, name: '', description: '' }
  showModal.value = true
  error.value = ''
}

const openEditModal = (cat) => {
  isEditing.value = true
  form.value = {
    id: cat.id,
    name: cat.name,
    description: cat.description || ''
  }
  showModal.value = true
  error.value = ''
}

const closeModal = () => {
  showModal.value = false
  form.value = { id: null, name: '', description: '' }
  error.value = ''
}

const saveCategory = async () => {
  saving.value = true
  error.value = ''

  try {
    const payload = {
      name: form.value.name,
      description: form.value.description
    }

    if (isEditing.value) {
      await categoryStore.update(form.value.id, payload)
    } else {
      await categoryStore.create(payload)
    }

    emit('update-count')
    closeModal()

  } catch (err) {
    console.error(err)
    error.value = 'Greška pri čuvanju kategorije.'
  } finally {
    saving.value = false
  }
}

const deleteCategory = (cat) => {
  openConfirm(
    `Da li želiš da obrišeš "${cat.name}"?`,
    async () => {
      try {
        await categoryStore.remove(cat.id)
        emit('update-count')
      } catch {
        openConfirm("Ne može da se obriše kategorija jer ima proizvode!", null)
      }
    }
  )
}

onMounted(() => {
  categoryStore.fetch()
  emit('update-count')
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 mb-1">📁 Kategorije</h2>
        <p class="text-xs text-gray-500 font-medium">Organizujte proizvode u kategorije</p>
      </div>

      <button
        @click="openAddModal"
        class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white rounded-lg text-sm font-semibold shadow-md hover:shadow-lg transition-all cursor-pointer flex items-center gap-1.5"
      >
        <span class="text-base">➕</span>
        <span>Dodaj Kategoriju</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="categoryStore.loading" class="text-center py-16">
      <div class="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-[#3555e4] mb-4"></div>
      <p class="text-gray-600 text-lg font-semibold">Učitavanje kategorija...</p>
    </div>

    <!-- List -->
    <div v-else-if="categoryStore.list.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="cat in categoryStore.list"
        :key="cat.id"
        class="bg-white border-2 border-gray-200 rounded-2xl p-6 shadow-md 
               hover:shadow-xl hover:border-blue-300 transition-all duration-300 transform hover:scale-[1.02]"
      >
        <div class="flex justify-between items-start mb-4">
          <div class="flex-1">
            <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ cat.name }}</h3>

            <p v-if="cat.description" class="text-gray-600 text-sm mt-2 leading-relaxed">
              {{ cat.description }}
            </p>
          </div>
        </div>

        <div class="flex items-center justify-between pt-4 border-t border-gray-200">
          <span
            class="px-4 py-2 bg-gradient-to-r from-green-50 to-green-100 text-green-700 rounded-xl
                   text-sm font-bold border border-green-200"
          >
            📦 {{ cat.product_count || 0 }} proizvoda
          </span>

          <div class="flex gap-2">
            <button
              @click="openEditModal(cat)"
              class="px-4 py-2.5 bg-blue-400 hover:bg-blue-500 text-white rounded-lg shadow-sm hover:shadow transition-all cursor-pointer text-sm font-medium"
            >
              ✏️ Izmeni
            </button>

            <button
              @click="deleteCategory(cat)"
              class="px-4 py-2.5 bg-red-400 hover:bg-red-500 text-white rounded-lg shadow-sm hover:shadow transition-all cursor-pointer text-sm font-medium"
            >
              🗑️ Obriši
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="text-center py-20">
      <div class="inline-block bg-gray-100 rounded-full p-8 mb-4">
        <span class="text-6xl">📁</span>
      </div>
      <p class="text-xl font-bold text-gray-600 mb-2">
        Nema kategorija
      </p>
      <p class="text-gray-500 mb-6">Dodajte prvu kategoriju da započnete!</p>
      <button
        @click="openAddModal"
        class="px-6 py-3 bg-gradient-to-r from-[#3555e4] to-[#64b5f6] text-white rounded-xl font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 cursor-pointer"
      >
        ➕ Dodaj Prvu Kategoriju
      </button>
    </div>

    <!-- Modal -->
    <AdminModal
      :show="showModal"
      :title="isEditing ? 'Izmeni Kategoriju' : 'Nova Kategorija'"
      @close="closeModal"
    >
      <form @submit.prevent="saveCategory" class="space-y-6">
        <div>
          <label class="block mb-2 font-medium text-gray-800">Naziv *</label>
          <input
            v-model="form.name"
            required
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <div>
          <label class="block mb-2 font-medium text-gray-800">Opis</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-4 py-3 rounded-xl bg-gray-100 border border-gray-200
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm resize-none"
          ></textarea>
        </div>

        <p v-if="error" class="text-red-600 font-medium">{{ error }}</p>

        <div class="flex justify-end gap-4 pt-4">
          <button
            type="button"
            @click="closeModal"
            class="px-6 py-3 bg-gray-300 rounded-xl font-semibold hover:bg-gray-400
                   transition cursor-pointer"
          >
            Otkaži
          </button>

          <button
            type="submit"
            :disabled="saving"
            class="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold shadow
                   hover:bg-blue-700 transition cursor-pointer disabled:opacity-60"
          >
            {{ saving ? 'Čuvanje...' : 'Sačuvaj' }}
          </button>
        </div>
      </form>
    </AdminModal>

    <!-- Confirm Modal -->
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

