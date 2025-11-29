<script setup>
import { ref } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/store/auth'
import ConfirmModal from '@/components/ConfirmModal.vue'
import { getImageUrl } from '@/composables/useImageUrl'

const props = defineProps({
  productId: Number
})

const emit = defineEmits(['updated'])

const images = ref([])
const uploading = ref(false)
const selectedFile = ref(null)
const showConfirm = ref(false)
const confirmMessage = ref('')
const confirmAction = ref(null)
const imageToDelete = ref(null)
const previewImage = ref(null)
const showPreview = ref(false)

const fetchImages = async () => {
  if (!props.productId) return
  try {
    const authStore = useAuthStore()
    const response = await api.get(`product-images/?product_id=${props.productId}`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    images.value = response.data
  } catch (error) {
    console.error('Error fetching images:', error)
  }
}

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
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
  imageToDelete.value = null
}

const doConfirm = () => {
  if (confirmAction.value) confirmAction.value()
  closeConfirm()
}

const uploadImage = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  const formData = new FormData()
  formData.append('image', selectedFile.value)
  formData.append('product', props.productId)
  formData.append('is_primary', images.value.length === 0) // Prva slika je primary

  try {
    const authStore = useAuthStore()
    await api.post('product-images/', formData, {
      headers: { 
        Authorization: `Bearer ${authStore.accessToken}`,
        'Content-Type': 'multipart/form-data' 
      }
    })
    selectedFile.value = null
    await fetchImages()
    emit('updated')
  } catch (error) {
    console.error('Upload error:', error)
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Greška pri upload-u slike'
    openConfirm(errorMsg, null)
  } finally {
    uploading.value = false
  }
}

const setPrimary = async (imageId) => {
  try {
    const authStore = useAuthStore()
    await api.patch(`product-images/${imageId}/`, { is_primary: true }, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    await fetchImages()
  } catch (error) {
    console.error('Error setting primary:', error)
  }
}

const selectImageForPreview = (img) => {
  previewImage.value = img
  showPreview.value = true
}

const closePreview = () => {
  showPreview.value = false
  previewImage.value = null
}

const deleteImage = (imageId) => {
  imageToDelete.value = imageId
  openConfirm(
    'Da li želiš da obrišeš ovu sliku?',
    async () => {
      try {
        const authStore = useAuthStore()
        await api.delete(`product-images/${imageId}/`, {
          headers: { Authorization: `Bearer ${authStore.accessToken}` }
        })
        await fetchImages()
        emit('updated')
      } catch (error) {
        console.error('Delete error:', error)
        const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Greška pri brisanju slike'
        openConfirm(errorMsg, null)
      }
    }
  )
}

// Fetch na mount
if (props.productId) {
  fetchImages()
}
</script>

<template>
  <div class="space-y-4">
    <h4 class="font-semibold text-sm px-1 mb-1">Slike proizvoda</h4>

    <!-- Upload forma -->
    <div class="flex gap-3 items-center">
      <input
        type="file"
        @change="handleFileSelect"
        accept="image/*"
        class="flex-1 border rounded-lg px-3 py-2 text-xs cursor-pointer"
      />
      <button
        @click="uploadImage"
        :disabled="!selectedFile || uploading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-medium disabled:opacity-50 cursor-pointer flex items-center gap-1.5"
      >
        <span>{{ uploading ? 'Upload...' : 'Dodaj sliku' }}</span>
      </button>
    </div>

    <!-- Galerija -->
    <div class="grid grid-cols-4 gap-3">
      <TransitionGroup name="image-list">
        <div
          v-for="img in images"
          :key="img.id"
          class="relative border rounded-lg overflow-hidden group cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-md"
          @click="selectImageForPreview(img)"
        >
          <img
            v-if="img.image"
            :src="getImageUrl(img.image)"
            :alt="img.alt_text"
            class="w-full h-24 object-cover transition-transform duration-300 group-hover:scale-110"
          />
          <div v-else class="w-full h-24 bg-gray-200 flex items-center justify-center text-gray-400">
            <span class="text-2xl">📷</span>
          </div>

          <div v-if="img.is_primary" class="absolute top-2 left-2 bg-green-500 text-white px-2 py-1 text-xs font-semibold rounded shadow">
            ⭐ Glavna
          </div>

          <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-1.5 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-all duration-300">
            <button
              v-if="!img.is_primary"
              @click.stop="setPrimary(img.id)"
              class="flex-1 px-2 py-1 bg-green-600 hover:bg-green-700 text-white text-xs font-medium rounded cursor-pointer transition-all"
            >
              ⭐ Glavna
            </button>
            <button
              @click.stop="deleteImage(img.id)"
              class="px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded cursor-pointer transition-all"
            >
              🗑️
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <p v-if="images.length === 0" class="text-gray-400 text-center py-6 text-sm">
      Nema slika. Dodaj prvu sliku proizvoda.
    </p>

    <ConfirmModal
      :show="showConfirm"
      :message="confirmMessage"
      title="Potvrda"
      confirmText="Obriši"
      cancelText="Odustani"
      @confirm="doConfirm"
      @cancel="closeConfirm"
    />

    <!-- Preview Modal -->
    <Transition name="preview">
      <div
        v-if="showPreview && previewImage"
        @click="closePreview"
        class="fixed inset-0 bg-black/90 backdrop-blur-md flex items-center justify-center z-[2000] cursor-pointer"
      >
        <div @click.stop class="max-w-2xl max-h-[90vh] bg-white rounded-lg overflow-hidden shadow-xl transform transition-all">
          <div class="relative">
            <img
              v-if="previewImage.image"
              :src="getImageUrl(previewImage.image)"
              :alt="previewImage.alt_text || 'Preview'"
              class="w-full h-auto max-h-[85vh] object-contain"
            />
            <div v-else class="w-full h-64 bg-gray-200 flex items-center justify-center text-gray-400">
              <span class="text-3xl">📷</span>
            </div>
            <button
              @click="closePreview"
              class="absolute top-2 right-2 bg-white/95 hover:bg-white text-gray-800 rounded-full w-8 h-8 flex items-center justify-center text-xl font-bold shadow-lg hover:scale-110 transition-all duration-200 cursor-pointer"
            >
              ×
            </button>
          </div>
          <div v-if="previewImage.alt_text" class="p-2 bg-white border-t">
            <p class="text-gray-700 text-xs font-medium">{{ previewImage.alt_text }}</p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.preview-enter-active,
.preview-leave-active {
  transition: all 0.3s ease;
}

.preview-enter-from,
.preview-leave-to {
  opacity: 0;
}

.preview-enter-from > div,
.preview-leave-to > div {
  transform: scale(0.8) translateY(20px);
  opacity: 0;
}

.image-list-enter-active {
  transition: all 0.3s ease;
}

.image-list-leave-active {
  transition: all 0.3s ease;
}

.image-list-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(10px);
}

.image-list-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(-10px);
}

.image-list-move {
  transition: transform 0.3s ease;
}
</style>
