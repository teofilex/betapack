<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const messages = ref([])
const loading = ref(true)
const selectedMessage = ref(null)
const showModal = ref(false)

const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${authStore.accessToken}` }
})

const fetchMessages = async () => {
  loading.value = true
  try {
    const response = await api.get('/contact-messages/', getAuthHeaders())
    messages.value = response.data
  } catch (error) {
    console.error('Error fetching contact messages:', error)
  } finally {
    loading.value = false
  }
}

const viewMessage = (message) => {
  selectedMessage.value = message
  showModal.value = true

  // Automatski označi kao pročitano
  if (!message.is_read) {
    markAsRead(message.id)
  }
}

const markAsRead = async (id) => {
  try {
    await api.patch(`/contact-messages/${id}/`, { is_read: true }, getAuthHeaders())
    const msg = messages.value.find(m => m.id === id)
    if (msg) msg.is_read = true
  } catch (error) {
    console.error('Error marking message as read:', error)
  }
}

const markAsReplied = async (id) => {
  try {
    await api.patch(`/contact-messages/${id}/`, { is_replied: true }, getAuthHeaders())
    const msg = messages.value.find(m => m.id === id)
    if (msg) msg.is_replied = true
  } catch (error) {
    console.error('Error marking message as replied:', error)
  }
}

const deleteMessage = async (id) => {
  if (!confirm('Da li ste sigurni da želite da obrišete ovu poruku?')) return

  try {
    await api.delete(`/contact-messages/${id}/`, getAuthHeaders())
    messages.value = messages.value.filter(m => m.id !== id)
    if (selectedMessage.value?.id === id) {
      showModal.value = false
    }
  } catch (error) {
    console.error('Error deleting message:', error)
  }
}

const closeModal = () => {
  showModal.value = false
  selectedMessage.value = null
}

const unreadCount = computed(() =>
  messages.value.filter(m => !m.is_read).length
)

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

onMounted(() => {
  fetchMessages()
})
</script>

<template>
  <div class="p-8">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h2 class="text-3xl font-bold text-gray-900">Kontakt Poruke</h2>
        <p class="text-gray-600 mt-2">
          <span v-if="unreadCount > 0" class="text-red-600 font-semibold">
            {{ unreadCount }} nepročitanih poruka
          </span>
          <span v-else class="text-green-600 font-semibold">
            Nema nepročitanih poruka
          </span>
        </p>
      </div>

      <button
        @click="fetchMessages"
        class="px-6 py-3 bg-[#1976d2] text-white rounded-xl font-semibold hover:bg-[#1565c0] transition cursor-pointer flex items-center gap-2"
      >
        <span>🔄</span>
        <span>Osveži</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="text-4xl mb-4">⏳</div>
      <p class="text-gray-600">Učitavanje poruka...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="messages.length === 0" class="text-center py-12 bg-white rounded-xl shadow-lg">
      <div class="text-6xl mb-4">📭</div>
      <h3 class="text-xl font-bold text-gray-900 mb-2">Nema poruka</h3>
      <p class="text-gray-600">Još niko nije poslao poruku sa kontakt forme.</p>
    </div>

    <!-- Messages List -->
    <div v-else class="space-y-4">
      <div
        v-for="message in messages"
        :key="message.id"
        @click="viewMessage(message)"
        class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition cursor-pointer border-2"
        :class="message.is_read ? 'border-gray-200' : 'border-[#1976d2] bg-blue-50/30'"
      >
        <div class="flex justify-between items-start gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <span class="text-2xl">
                {{ message.is_read ? '📖' : '📩' }}
              </span>
              <h3 class="text-lg font-bold text-gray-900">
                {{ message.name }}
              </h3>
              <span
                v-if="!message.is_read"
                class="px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full"
              >
                NOVO
              </span>
              <span
                v-if="message.is_replied"
                class="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full"
              >
                ODGOVORENO
              </span>
            </div>

            <div class="space-y-1 text-sm text-gray-600 mb-3">
              <div class="flex items-center gap-2">
                <span>📞</span>
                <a :href="`tel:${message.phone}`" class="hover:text-[#1976d2] font-semibold">
                  {{ message.phone }}
                </a>
              </div>
              <div v-if="message.email" class="flex items-center gap-2">
                <span>✉️</span>
                <a :href="`mailto:${message.email}`" class="hover:text-[#1976d2]">
                  {{ message.email }}
                </a>
              </div>
            </div>

            <p class="text-gray-700 line-clamp-2 mb-3">
              {{ message.message }}
            </p>

            <p class="text-xs text-gray-500">
              {{ formatDate(message.created_at) }}
            </p>
          </div>

          <button
            @click.stop="deleteMessage(message.id)"
            class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition font-semibold"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div
      v-if="showModal && selectedMessage"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click="closeModal"
    >
      <div
        class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <!-- Modal Header -->
        <div class="sticky top-0 bg-white border-b border-gray-200 px-8 py-6 flex justify-between items-center">
          <div>
            <h3 class="text-2xl font-bold text-gray-900">{{ selectedMessage.name }}</h3>
            <p class="text-sm text-gray-500 mt-1">
              {{ formatDate(selectedMessage.created_at) }}
            </p>
          </div>
          <button
            @click="closeModal"
            class="text-gray-500 hover:text-gray-700 text-3xl font-bold leading-none"
          >
            ×
          </button>
        </div>

        <!-- Modal Body -->
        <div class="px-8 py-6 space-y-6">
          <!-- Contact Info -->
          <div class="bg-gray-50 rounded-xl p-6 space-y-3">
            <div class="flex items-center gap-3">
              <span class="text-2xl">📞</span>
              <div>
                <p class="text-xs text-gray-500 font-semibold">Telefon</p>
                <a :href="`tel:${selectedMessage.phone}`" class="text-lg font-bold text-[#1976d2] hover:underline">
                  {{ selectedMessage.phone }}
                </a>
              </div>
            </div>

            <div v-if="selectedMessage.email" class="flex items-center gap-3">
              <span class="text-2xl">✉️</span>
              <div>
                <p class="text-xs text-gray-500 font-semibold">Email</p>
                <a :href="`mailto:${selectedMessage.email}`" class="text-lg font-bold text-[#1976d2] hover:underline">
                  {{ selectedMessage.email }}
                </a>
              </div>
            </div>
          </div>

          <!-- Message -->
          <div>
            <h4 class="text-sm font-semibold text-gray-500 mb-3">PORUKA</h4>
            <div class="bg-gray-50 rounded-xl p-6">
              <p class="text-gray-800 whitespace-pre-wrap leading-relaxed">
                {{ selectedMessage.message }}
              </p>
            </div>
          </div>

          <!-- Status -->
          <div class="flex gap-3">
            <div
              class="flex-1 px-4 py-3 rounded-xl text-center"
              :class="selectedMessage.is_read ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
            >
              <p class="text-xs font-semibold">{{ selectedMessage.is_read ? '✓ Pročitano' : '○ Nepročitano' }}</p>
            </div>
            <div
              class="flex-1 px-4 py-3 rounded-xl text-center"
              :class="selectedMessage.is_replied ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'"
            >
              <p class="text-xs font-semibold">{{ selectedMessage.is_replied ? '✓ Odgovoreno' : '○ Nije odgovoreno' }}</p>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-8 py-6 flex gap-4">
          <button
            v-if="!selectedMessage.is_replied"
            @click="markAsReplied(selectedMessage.id)"
            class="flex-1 px-6 py-3 bg-green-500 text-white rounded-xl font-semibold hover:bg-green-600 transition cursor-pointer"
          >
            ✓ Označi kao odgovoreno
          </button>
          <button
            @click="deleteMessage(selectedMessage.id)"
            class="px-6 py-3 bg-red-500 text-white rounded-xl font-semibold hover:bg-red-600 transition cursor-pointer"
          >
            🗑️ Obriši
          </button>
          <button
            @click="closeModal"
            class="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-300 transition cursor-pointer"
          >
            Zatvori
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
