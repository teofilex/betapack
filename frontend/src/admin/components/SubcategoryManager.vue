<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCategoryStore } from '@/admin/store/categories'
import { useSubcategoryStore } from '@/admin/store/subcategories'
import ConfirmModal from '@/components/ConfirmModal.vue'
import AdminModal from './AdminModal.vue'

const emit = defineEmits(['update-count'])

const categoryStore = useCategoryStore()
const subcategoryStore = useSubcategoryStore()

// Confirm modal
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

// UI
const showModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const loading = ref(false)
const error = ref('')

// Form
const form = ref({
  id: null,
  name: '',
  category: '',
  description: ''
})

// Data
const subcategories = computed(() => subcategoryStore.list)
const categories = computed(() => categoryStore.list)

// Modal — Add
const openAddModal = () => {
  if (categories.value.length === 0) {
    openConfirm("Prvo dodaj kategoriju!", null)
    return
  }

  isEditing.value = false
  form.value = { id: null, name: '', category: '', description: '' }
  showModal.value = true
  error.value = ''
}

// Modal — Edit
const openEditModal = (sub) => {
  isEditing.value = true
  form.value = {
    id: sub.id,
    name: sub.name,
    category: sub.category,
    description: sub.description || ''
  }
  showModal.value = true
  error.value = ''
}

// Close modal
const closeModal = () => {
  showModal.value = false
  error.value = ''
}

// Save subcategory
const saveSubcategory = async () => {
  saving.value = true
  error.value = ''

  try {
    const payload = {
      name: form.value.name,
      category: form.value.category,
      description: form.value.description
    }

    if (isEditing.value) {
      await subcategoryStore.update(form.value.id, payload)
    } else {
      await subcategoryStore.create(payload)
    }

    emit('update-count')
    closeModal()
  } catch (err) {
    console.error(err)
    error.value = 'Greška pri čuvanju. Proveri da li naziv već postoji.'
  } finally {
    saving.value = false
  }
}

// Delete — using ConfirmModal
const deleteSubcategory = (sub) => {
  openConfirm(
    `Obrisati podkategoriju "${sub.name}"?`,
    async () => {
      try {
        await subcategoryStore.remove(sub.id)
        emit('update-count')
      } catch (err) {
        console.error(err)
        openConfirm(
          "Ne može da se obriše podkategorija! Moguće da postoje proizvodi u njoj.",
          null
        )
      }
    }
  )
}

// Load data
onMounted(async () => {
  loading.value = true
  await categoryStore.fetch()
  await subcategoryStore.fetch()
  loading.value = false
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
        <div>
        <h2 class="text-xs lg:text-sm font-bold text-gray-900 mb-1 flex items-center gap-1">📂 Podkategorije</h2>
        <p class="text-xs text-gray-500 font-medium">Organizujte proizvode u podkategorije</p>
      </div>

      <button
        @click="openAddModal"
        class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white rounded-lg text-xs font-medium shadow-md hover:shadow-lg transition-all cursor-pointer flex items-center gap-1.5"
      >
        <span class="text-sm">➕</span>
        <span>Dodaj Podkategoriju</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#3555e4] mb-2"></div>
      <p class="text-gray-600 text-sm font-semibold">Učitavanje podkategorija...</p>
    </div>

    <!-- List -->
    <div v-else-if="subcategories.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div
        v-for="sub in subcategories"
        :key="sub.id"
        class="bg-white border border-gray-200 rounded-lg p-3 shadow-md 
               hover:shadow-lg hover:border-blue-300 transition-all duration-300 transform hover:scale-[1.01]"
      >
        <div class="flex justify-between items-start mb-2">
          <div class="flex-1">
            <h3 class="text-sm font-bold text-gray-900 mb-1">{{ sub.name }}</h3>
            <span class="inline-block px-2 py-1 bg-gradient-to-r from-blue-50 to-blue-100 text-blue-700 rounded-lg text-xs font-bold border border-blue-200 mb-2">
              📁 {{ sub.category_name }}
            </span>

            <p v-if="sub.description" class="text-gray-600 text-xs mt-2 leading-relaxed">
              {{ sub.description }}
            </p>
          </div>
        </div>

        <div class="flex items-center justify-end gap-1.5 pt-2 border-t border-gray-200">
          <button
            @click="openEditModal(sub)"
            class="px-2 py-1 bg-blue-400 hover:bg-blue-500 text-white rounded-lg shadow-sm hover:shadow transition-all cursor-pointer text-xs font-medium"
          >
            ✏️ Izmeni
          </button>

          <button
            @click="deleteSubcategory(sub)"
            class="px-2 py-1 bg-red-400 hover:bg-red-500 text-white rounded-lg shadow-sm hover:shadow transition-all cursor-pointer text-xs font-medium"
          >
            🗑️ Obriši
          </button>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="text-center py-10">
      <div class="inline-block bg-gray-100 rounded-full p-4 mb-3">
        <span class="text-3xl">📂</span>
      </div>
      <p v-if="categories.length === 0" class="text-sm font-bold text-gray-600 mb-1">
        Prvo dodajte kategorije
      </p>
      <p v-else class="text-sm font-bold text-gray-600 mb-1">
        Nema podkategorija
      </p>
      <p class="text-sm text-gray-500 mb-3">Dodajte prvu podkategoriju da započnete!</p>
      <button
        v-if="categories.length > 0"
        @click="openAddModal"
        class="px-2 py-1 bg-gradient-to-r from-[#3555e4] to-[#64b5f6] text-white rounded-md font-medium shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer text-xs"
      >
        ➕ Dodaj Prvu Podkategoriju
      </button>
    </div>

    <!-- Modal -->
    <AdminModal
      :show="showModal"
      :title="isEditing ? 'Izmeni Podkategoriju' : 'Nova Podkategorija'"
      max-width="max-w-[400px]"
      @close="closeModal"
    >
      <form @submit.prevent="saveSubcategory" class="space-y-5">
        <!-- CATEGORY -->
        <div>
          <label class="block mb-1 text-xs font-medium text-gray-800 px-1">Kategorija *</label>
          <select
            v-model="form.category"
            required
            class="w-full px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-white border border-gray-300 text-xs sm:text-sm
                   focus:ring-2 focus:ring-[#1976d2] focus:border-[#1976d2] focus:outline-none transition-all 
                   shadow-sm hover:border-gray-400 cursor-pointer"
          >
            <option value="">Izaberi kategoriju</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
        </div>

        <!-- NAME -->
        <div>
          <label class="block mb-1 text-xs font-medium text-gray-800 px-1">Naziv *</label>
          <input
            v-model="form.name"
            required
            class="w-full px-2.5 py-1.5 rounded-lg bg-gray-100 border border-gray-200 text-xs
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm"
          />
        </div>

        <!-- DESCRIPTION -->
        <div>
          <label class="block mb-1 text-xs font-medium text-gray-800 px-1">Opis</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-2.5 py-1.5 rounded-lg bg-gray-100 border border-gray-200 text-xs
                   focus:ring-2 focus:ring-blue-400 focus:outline-none transition shadow-sm resize-none"
          ></textarea>
        </div>

        <!-- ERROR -->
        <p v-if="error" class="text-red-600 text-sm font-medium px-1">{{ error }}</p>

        <!-- BUTTONS -->
        <div class="flex justify-end gap-2 pt-1">
          <button
            type="button"
            @click="closeModal"
            class="px-3 py-2 rounded-lg bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold
                   transition cursor-pointer text-xs"
          >
            Otkaži
          </button>

          <button
            type="submit"
            :disabled="saving"
            class="px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold
                   transition cursor-pointer disabled:opacity-60 text-xs"
          >
            {{ saving ? "Čuvanje..." : "Sačuvaj" }}
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