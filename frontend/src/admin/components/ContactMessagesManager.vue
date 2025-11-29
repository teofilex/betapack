<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useContactMessagesStore } from '../store/contactMessages'
import ConfirmModal from '@/components/ConfirmModal.vue'

const emit = defineEmits(['update-count'])

const messageStore = useContactMessagesStore()
const showModal = ref(false)
const showConfirmDelete = ref(false)
const messageToDelete = ref(null)

// Funkcija za osvežavanje
const refreshMessages = async () => {
  await messageStore.fetchAll()
  emit('update-count')
}

const viewMessage = (message) => {
  messageStore.selectMessage(message)
  showModal.value = true

  // Automatski označi kao pročitano
  if (!message.is_read) {
    markAsRead(message.id)
  }
}

const markAsRead = async (id) => {
  try {
    await messageStore.markAsRead(id)
  } catch (error) {
    console.error('Error marking message as read:', error)
  }
}

const markAsReplied = async (id) => {
  try {
    await messageStore.markAsReplied(id)
    emit('update-count')
  } catch (error) {
    console.error('Error marking message as replied:', error)
  }
}

const deleteMessage = (id) => {
  messageToDelete.value = id
  showConfirmDelete.value = true
}

const confirmDelete = async () => {
  if (messageToDelete.value) {
    try {
      await messageStore.deleteMessage(messageToDelete.value)
      if (messageStore.selected?.id === messageToDelete.value) {
        showModal.value = false
      }
      emit('update-count')
    } catch (error) {
      console.error('Error deleting message:', error)
      alert('Greška pri brisanju poruke')
    }
  }
  showConfirmDelete.value = false
  messageToDelete.value = null
}

const cancelDelete = () => {
  showConfirmDelete.value = false
  messageToDelete.value = null
}

const closeModal = () => {
  showModal.value = false
  messageStore.clearSelected()
}

const unreadCount = computed(() => messageStore.unreadCount)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('sr-RS', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// onMounted → fetch i osveži brojač
onMounted(async () => {
  await refreshMessages()
  
  // Osveži kada se tab vrati u fokus
  if (typeof window !== 'undefined') {
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState === 'visible' && !messageStore.loading) {
        await refreshMessages()
      }
    })
  }
})
</script>

<template>
  <div class="p-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4 mb-4">
      <div class="flex-1">
        <h2 class="text-xs lg:text-sm font-bold text-gray-900 flex items-center gap-1">💬 Kontakt Poruke</h2>
        <p class="text-gray-600 mt-1 text-sm">
          <span v-if="unreadCount > 0" class="text-red-600 font-semibold">
            {{ unreadCount }} nepročitanih poruka
          </span>
          <span v-else class="text-green-600 font-semibold">
            Nema nepročitanih poruka
          </span>
        </p>
      </div>

      <button
        @click="refreshMessages"
        class="px-3 py-1.5 bg-[#1976d2] text-white rounded-lg font-semibold hover:bg-[#1565c0] transition cursor-pointer flex items-center gap-1.5 text-sm whitespace-nowrap"
      >
        <span>🔄</span>
        <span>Osveži</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="messageStore.loading" class="text-center py-12">
      <div class="text-4xl mb-4">⏳</div>
      <p class="text-gray-600">Učitavanje poruka...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="messageStore.list.length === 0" class="text-center py-12 bg-white rounded-xl shadow-lg">
      <div class="text-6xl mb-4">📭</div>
      <h3 class="text-sm font-bold text-gray-900 mb-1">Nema poruka</h3>
      <p class="text-gray-600">Još niko nije poslao poruku sa kontakt forme.</p>
    </div>

    <!-- Messages List -->
    <div v-else class="space-y-2">
      <div
        v-for="message in messageStore.list"
        :key="message.id"
        @click="viewMessage(message)"
        class="bg-white rounded-lg shadow-md border p-3 hover:shadow-lg hover:border-blue-300 transition-all duration-300 cursor-pointer transform hover:scale-[1.01] group"
        :class="message.is_read ? 'border-gray-200' : 'border-[#1976d2] bg-blue-50/30'"
      >
        <div class="flex justify-between items-start gap-3">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-base">
                {{ message.is_read ? '📖' : '📩' }}
              </span>
              <h3 class="text-xs font-bold text-gray-900">
                {{ message.name }}
              </h3>
              <span
                v-if="!message.is_read"
                class="px-2 py-0.5 bg-red-500 text-white text-[10px] font-bold rounded-full"
              >
                NOVO
              </span>
              <span
                v-if="message.is_replied"
                class="px-2 py-0.5 bg-green-500 text-white text-[10px] font-bold rounded-full"
              >
                ODGOVORENO
              </span>
            </div>

            <div class="space-y-1 text-xs text-gray-600 mb-2">
              <div class="flex items-center gap-2">
                <span>📞</span>
                <a :href="`tel:${message.phone}`" class="hover:text-[#1976d2] font-semibold cursor-pointer">
                  {{ message.phone }}
                </a>
              </div>
              <div v-if="message.email" class="flex items-center gap-2">
                <span>✉️</span>
                <a :href="`mailto:${message.email}`" class="hover:text-[#1976d2] cursor-pointer">
                  {{ message.email }}
                </a>
              </div>
            </div>

            <p class="text-xs text-gray-700 line-clamp-2 mb-1">
              {{ message.message }}
            </p>

            <p class="text-xs text-gray-500">
              {{ formatDate(message.created_at) }}
            </p>
          </div>

          <button
            @click.stop="deleteMessage(message.id)"
            class="px-3 py-1.5 text-red-600 hover:bg-red-50 rounded-lg transition font-medium cursor-pointer text-xs flex items-center gap-1"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div
      v-if="showModal && messageStore.selected"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click="closeModal"
    >
      <div
        class="bg-white rounded-2xl shadow-2xl w-[95vw] sm:w-full sm:max-w-xl max-h-[98vh] overflow-y-auto"
        @click.stop
      >
        <!-- Modal Header -->
        <div class="sticky top-0 bg-white border-b border-gray-200 px-5 py-4 flex justify-between items-center">
          <div>
            <h3 class="text-base font-bold text-gray-900 px-1">{{ messageStore.selected.name }}</h3>
            <p class="text-xs text-gray-500 mt-1 px-1">
              {{ formatDate(messageStore.selected.created_at) }}
            </p>
          </div>
          <button
            @click="closeModal"
            class="text-gray-500 hover:text-gray-700 text-2xl font-bold leading-none cursor-pointer"
          >
            ×
          </button>
        </div>

        <!-- Modal Body -->
        <div class="px-5 py-5 space-y-5">
          <!-- Contact Info -->
          <div class="bg-gray-50 rounded-lg p-4 space-y-3">
            <div class="flex items-center gap-3">
              <span class="text-base">📞</span>
              <div>
                <p class="text-xs text-gray-500 font-medium mb-1 px-1">Telefon</p>
                <a :href="`tel:${messageStore.selected.phone}`" class="text-sm font-bold text-[#1976d2] hover:underline cursor-pointer px-1">
                  {{ messageStore.selected.phone }}
                </a>
              </div>
            </div>

            <div v-if="messageStore.selected.email" class="flex items-center gap-3">
              <span class="text-base">✉️</span>
              <div>
                <p class="text-xs text-gray-500 font-medium mb-1 px-1">Email</p>
                <a :href="`mailto:${messageStore.selected.email}`" class="text-sm font-bold text-[#1976d2] hover:underline cursor-pointer px-1">
                  {{ messageStore.selected.email }}
                </a>
              </div>
            </div>
          </div>

          <!-- Message -->
          <div>
            <h4 class="text-xs font-semibold text-gray-500 mb-2 px-1">PORUKA</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed px-1">
                {{ messageStore.selected.message }}
              </p>
            </div>
          </div>

          <!-- Status -->
          <div class="flex gap-3">
            <div
              class="flex-1 px-3 py-2 rounded-lg text-center"
              :class="messageStore.selected.is_read ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
            >
              <p class="text-xs font-semibold">{{ messageStore.selected.is_read ? '✓ Pročitano' : '○ Nepročitano' }}</p>
            </div>
            <div
              class="flex-1 px-3 py-2 rounded-lg text-center"
              :class="messageStore.selected.is_replied ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
            >
              <p class="text-xs font-semibold">{{ messageStore.selected.is_replied ? '✓ Odgovoreno' : '○ Nije odgovoreno' }}</p>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-5 py-4 flex gap-3">
          <button
            v-if="!messageStore.selected.is_replied"
            @click="markAsReplied(messageStore.selected.id)"
            class="flex-1 px-4 py-2.5 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600 transition cursor-pointer text-xs flex items-center gap-1.5"
          >
            <span>✓</span>
            <span>Označi kao odgovoreno</span>
          </button>
          <button
            @click="deleteMessage(messageStore.selected.id)"
            class="px-4 py-2.5 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600 transition cursor-pointer text-xs flex items-center gap-1.5"
          >
            <span>🗑️</span>
            <span>Obriši</span>
          </button>
          <button
            @click="closeModal"
            class="px-4 py-2.5 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition cursor-pointer text-xs flex items-center gap-1.5"
          >
            Zatvori
          </button>
        </div>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      :show="showConfirmDelete"
      message="Da li ste sigurni da želite da obrišete ovu poruku? Ova akcija je nepovratna."
      title="Potvrda brisanja"
      confirmText="Obriši"
      cancelText="Odustani"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>
