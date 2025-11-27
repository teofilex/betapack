<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useOrderStore } from '../store/orders'
import ConfirmModal from '@/components/ConfirmModal.vue'

const emit = defineEmits(['update-count'])
const orderStore = useOrderStore()

// Status boje i nazivi ostaju u komponenti
const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  processing: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800'
}

const statusLabels = {
  pending: 'Na čekanju',
  confirmed: 'Potvrđena',
  processing: 'U obradi',
  completed: 'Završena',
  cancelled: 'Otkazana'
}

// Tabovi za filtriranje
const activeTab = ref('all')
const tabs = [
  { id: 'all', label: 'Sve', count: null, icon: '📋', color: 'bg-gray-600 hover:bg-gray-700' },
  { id: 'pending', label: 'Na čekanju', count: null, icon: '⏳', color: 'bg-yellow-500 hover:bg-yellow-600' },
  { id: 'confirmed', label: 'Potvrđena', count: null, icon: '✅', color: 'bg-[#1976d2] hover:bg-[#1565c0]' },
  { id: 'processing', label: 'U obradi', count: null, icon: '⚙️', color: 'bg-purple-700 hover:bg-purple-800' },
  { id: 'completed', label: 'Završena', count: null, icon: '🎉', color: 'bg-green-500 hover:bg-green-600' },
  { id: 'cancelled', label: 'Otkazana', count: null, icon: '❌', color: 'bg-red-500 hover:bg-red-600' }
]

// Filtrirane porudžbine
const filteredOrders = computed(() => {
  if (activeTab.value === 'all') {
    return orderStore.list
  }
  return orderStore.list.filter(order => order.status === activeTab.value)
})

// Ažuriraj brojeve u tabovima
const updateTabCounts = () => {
  tabs.forEach(tab => {
    if (tab.id === 'all') {
      tab.count = orderStore.list.length
    } else {
      tab.count = orderStore.list.filter(order => order.status === tab.id).length
    }
  })
}

const showDetailModal = ref(false)
const showConfirmDelete = ref(false)

const openDetailModal = (order) => {
  orderStore.selectOrder(order)
  showDetailModal.value = true
}

const closeDetailModal = () => {
  showDetailModal.value = false
  orderStore.clearSelected()
}

const deleteOrder = () => {
  showConfirmDelete.value = true
}

const confirmDelete = async () => {
  if (orderStore.selected) {
    try {
      await orderStore.deleteOrder(orderStore.selected.id)
      closeDetailModal()
      await refreshOrders()
    } catch (error) {
      console.error('Error deleting order:', error)
      alert('Greška pri brisanju narudžbine')
    }
  }
  showConfirmDelete.value = false
}

const cancelDelete = () => {
  showConfirmDelete.value = false
}

// format funkcije ostaju ovde
const formatPrice = (price) =>
  new Intl.NumberFormat('sr-RS', { style: 'currency', currency: 'RSD' }).format(price)

const formatDate = (dateString) =>
  new Date(dateString).toLocaleString('sr-RS')

// Watch za promene u listi porudžbina - samo ažuriraj tabove, ne emituj event
watch(() => orderStore.list, () => {
  updateTabCounts()
}, { deep: true })

// Funkcija za osvežavanje
const refreshOrders = async () => {
  await orderStore.fetchAll()
  updateTabCounts()
  emit('update-count')
}

// Server-Sent Events za real-time notifikacije
let eventSource = null

// onMounted → fetch i osveži brojač, pokreni SSE
onMounted(async () => {
  await refreshOrders()
  startSSE()
  
  // Osveži kada se tab vrati u fokus
  if (typeof window !== 'undefined') {
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState === 'visible' && !orderStore.loading) {
        await refreshOrders()
        // Restartuj SSE ako je zatvoren
        if (!eventSource || eventSource.readyState === EventSource.CLOSED) {
          startSSE()
        }
      }
    })
  }
})

// onUnmounted → zatvori SSE
onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
})

// SSE funkcija za real-time notifikacije
const startSSE = () => {
  const { useAuthStore } = require('@/store/auth')
  const authStore = useAuthStore()
  
  if (!authStore.accessToken) {
    return
  }
  
  // Zatvori postojeći SSE ako postoji
  if (eventSource) {
    eventSource.close()
  }
  
  // Kreiraj SSE konekciju sa tokenom u query parametru
  const { api } = require('@/services/api')
  const baseURL = api.defaults.baseURL || 'http://127.0.0.1:8000/api'
  
  eventSource = new EventSource(`${baseURL}/orders/notifications/?token=${authStore.accessToken}`)
  
  eventSource.onmessage = async (event) => {
    try {
      // Heartbeat poruke se ignorišu
      if (event.data.startsWith(':')) {
        return
      }
      
      const data = JSON.parse(event.data)
      
      if (data.type === 'new_order') {
        // Nova porudžbina - osveži listu
        await refreshOrders()
      } else if (data.type === 'init') {
        // Inicijalizacija - proveri da li ima novih ordera
        if (data.count > orderStore.list.length) {
          await refreshOrders()
        }
      }
    } catch (e) {
      // Ignoriši parse greške za heartbeat
      if (!event.data.startsWith(':')) {
        console.error('SSE parse error:', e)
      }
    }
  }
  
  eventSource.onerror = (error) => {
    console.error('SSE connection error:', error)
    // Pokušaj ponovo nakon 5 sekundi
    setTimeout(() => {
      if (eventSource && eventSource.readyState === EventSource.CLOSED) {
        startSSE()
      }
    }, 5000)
  }
}
</script>


<template>
  <div>

    <!-- Header -->
    <div class="flex justify-between items-center mb-8 pt-8">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 mb-1">🛒 Narudžbine</h2>
        <p class="text-xs text-gray-500 font-medium">Upravljajte narudžbinama</p>
      </div>

      <button
        @click="refreshOrders"
        class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white rounded-lg text-sm font-semibold shadow-md hover:shadow-lg transition-all cursor-pointer flex items-center gap-1.5"
      >
        <span class="text-base">🔄</span>
        <span>Osveži</span>
      </button>
    </div>

    <!-- Tabs -->
    <div class="mb-8 bg-white rounded-2xl p-3 shadow-lg border border-gray-200 overflow-x-auto">
      <div class="flex gap-2 min-w-max">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="activeTab === tab.id
            ? `${tab.color} text-white shadow-lg scale-105`
            : 'bg-gray-50 text-gray-700 hover:bg-gray-100 hover:shadow-md'"
          class="px-6 py-4 font-bold text-base transition-all duration-300 cursor-pointer whitespace-nowrap flex items-center gap-3 rounded-xl border-2 min-w-[140px] justify-center"
          :style="activeTab === tab.id ? { borderColor: 'transparent' } : { borderColor: '#e5e7eb' }"
        >
          <span class="text-xl">{{ tab.icon }}</span>
          <span class="font-semibold">{{ tab.label }}</span>
          <span 
            v-if="tab.count !== null"
            :class="activeTab === tab.id 
              ? 'bg-white/30 text-white border-white/50' 
              : 'bg-white text-gray-700 border-gray-300'"
            class="px-3 py-1 rounded-full text-sm font-bold border-2 min-w-[28px] flex items-center justify-center"
          >
            {{ tab.count }}
          </span>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="orderStore.loading" class="text-center py-16 text-gray-600 text-lg">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[#1976d2] mb-4"></div>
      <p>Učitavanje narudžbina...</p>
    </div>

    <!-- Orders LIST -->
    <div v-else-if="filteredOrders.length > 0" class="space-y-4">
      <TransitionGroup name="order-list">
        <div
          v-for="order in filteredOrders"
          :key="order.id"
          class="bg-white rounded-2xl shadow-md border-2 border-gray-200 p-6 hover:shadow-xl hover:border-blue-300 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] group"
          @click="openDetailModal(order)"
        >
          <div class="flex justify-between items-start gap-6">

            <!-- Left Section -->
            <div class="flex-1">
              <!-- Order ID and Date -->
              <div class="flex items-center gap-3 mb-4">
                <div class="bg-[#1976d2] text-white rounded-xl px-4 py-2 shadow-md">
                  <span class="text-sm font-bold opacity-90">#</span>
                  <span class="text-2xl font-bold">{{ order.id }}</span>
                </div>
                <div class="flex items-center gap-2 text-gray-500">
                  <span class="text-lg">📅</span>
                  <p class="text-sm font-medium">{{ formatDate(order.created_at) }}</p>
                </div>
              </div>

              <!-- Customer Info -->
              <div class="space-y-2 mb-4">
                <div class="flex items-center gap-2">
                  <span class="text-xl">👤</span>
                  <p class="text-lg font-bold text-gray-900">{{ order.customer_name }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-lg">📞</span>
                  <a 
                    :href="`tel:${order.customer_phone}`"
                    @click.stop
                    class="text-base font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    {{ order.customer_phone }}
                  </a>
                </div>
                <div v-if="order.customer_email" class="flex items-center gap-2">
                  <span class="text-lg">✉️</span>
                  <a 
                    :href="`mailto:${order.customer_email}`"
                    @click.stop
                    class="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    {{ order.customer_email }}
                  </a>
                </div>
              </div>

              <!-- Total Amount -->
              <div class="mt-4 pt-4 border-t border-gray-200">
                <p class="text-sm font-semibold text-gray-500 uppercase mb-1">Ukupno</p>
                <p class="text-2xl font-bold text-green-600">
                  {{ formatPrice(order.total_amount) }}
                </p>
              </div>
            </div>

            <!-- Right Section -->
            <div class="flex flex-col items-end gap-4">
              <!-- Status Badge -->
              <div class="flex flex-col items-end gap-2">
                <span
                  :class="statusColors[order.status]"
                  class="px-5 py-2.5 rounded-full text-sm font-bold shadow-md border-2"
                  :style="{ borderColor: 'transparent' }"
                >
                  {{ statusLabels[order.status] }}
                </span>
              </div>

              <!-- Items Count -->
              <div v-if="order.items && order.items.length > 0" class="text-right">
                <p class="text-xs text-gray-500 uppercase font-semibold mb-1">Stavki</p>
                <p class="text-lg font-bold text-gray-700">
                  {{ order.items.length }} {{ order.items.length === 1 ? 'stavka' : 'stavki' }}
                </p>
              </div>

              <!-- View Button -->
              <button
                @click.stop="openDetailModal(order)"
                class="px-6 py-3 bg-[#1976d2] hover:bg-[#1565c0] text-white rounded-xl font-bold shadow-lg
                hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:scale-105 flex items-center gap-2"
              >
                <span>👁️</span>
                <span>Pregled</span>
              </button>
            </div>

          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Empty -->
    <div v-else class="py-20 text-center">
      <div class="inline-block bg-gray-100 rounded-full p-6 mb-4">
        <span class="text-5xl">📦</span>
      </div>
      <p class="text-xl font-semibold text-gray-600 mb-2">
        Nema narudžbina
      </p>
      <p class="text-gray-500">Nove narudžbine će se pojaviti ovde automatski</p>
    </div>

    <!-- DETAIL MODAL -->
    <div
      v-if="showDetailModal && orderStore.selected"
      @click.self="closeDetailModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center p-5 z-[1500]"
    >
      <div class="bg-white rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">

        <!-- Modal Header -->
        <div class="p-6 border-b bg-[#1976d2] text-white flex justify-between">
          <div>
            <h3 class="text-3xl font-bold mb-1">
              Narudžbina #{{ orderStore.selected.id }}
            </h3>
            <p class="text-sm opacity-90">{{ formatDate(orderStore.selected.created_at) }}</p>
          </div>

          <button @click="closeDetailModal" class="text-4xl hover:bg-white/20 rounded px-3 py-1 cursor-pointer transition">
            &times;
          </button>
        </div>

        <div class="p-8 space-y-6">

          <!-- Kupac -->
          <div>
            <h4 class="font-bold text-xl mb-4 text-gray-900">Kupac</h4>
            <div class="space-y-3 bg-blue-50 p-6 rounded-xl border border-blue-200">
              <div>
                <p class="text-sm text-gray-500 uppercase font-semibold mb-1">Ime</p>
                <p class="text-lg font-semibold text-gray-900">{{ orderStore.selected.customer_name }}</p>
              </div>

              <div>
                <p class="text-sm text-gray-500 uppercase font-semibold mb-1">Telefon</p>
                <a
                  :href="`tel:${orderStore.selected.customer_phone}`"
                  class="text-lg font-semibold text-[#1976d2] hover:text-[#1565c0] hover:underline cursor-pointer"
                >
                  {{ orderStore.selected.customer_phone }}
                </a>
              </div>

              <div v-if="orderStore.selected.customer_email">
                <p class="text-sm text-gray-500 uppercase font-semibold mb-1">Email</p>
                <a
                  :href="`mailto:${orderStore.selected.customer_email}`"
                  class="text-lg font-semibold text-[#1976d2] hover:text-[#1565c0] hover:underline cursor-pointer"
                >
                  {{ orderStore.selected.customer_email }}
                </a>
              </div>

              <div v-if="orderStore.selected.delivery_address">
                <p class="text-sm text-gray-500 uppercase font-semibold mb-1">Adresa</p>
                <p class="text-base text-gray-900">{{ orderStore.selected.delivery_address }}</p>
              </div>
            </div>
          </div>

          <!-- Items -->
          <div>
            <h4 class="font-bold text-xl mb-4 text-gray-900">Stavke</h4>

            <div class="space-y-3">
              <div
                v-for="item in orderStore.selected.items"
                :key="item.id"
                class="bg-white border border-gray-200 p-5 rounded-xl hover:shadow-md transition"
              >
                <div class="flex justify-between items-start">

                  <div class="flex-1">
                    <p class="font-bold text-lg text-gray-900 mb-1">{{ item.product_name }}</p>
                    <p v-if="item.variant_name" class="text-sm text-gray-600 mb-2">{{ item.variant_name }}</p>

                    <p class="text-sm text-gray-500">
                      Količina:
                      <span class="font-semibold text-gray-700">{{ item.quantity }}</span> kom
                    </p>

                    <p class="text-sm text-gray-500 mt-1">{{ formatPrice(item.unit_price) }} / kom</p>
                  </div>

                  <div class="text-right ml-4">
                    <p class="text-xl font-bold text-green-700">
                      {{ formatPrice(item.total_price) }}
                    </p>
                  </div>

                </div>
              </div>
            </div>
          </div>

          <!-- Total -->
          <div class="border-t-2 border-gray-300 pt-6">
            <div class="flex justify-between items-center bg-green-600
            text-white p-5 rounded-xl">
              <span class="text-xl font-bold">Ukupno:</span>
              <span class="text-3xl font-bold">{{ formatPrice(orderStore.selected.total_amount) }}</span>
            </div>
          </div>

          <!-- Napomena -->
          <div v-if="orderStore.selected.notes">
            <h4 class="font-bold text-xl mb-3 text-gray-900">Napomena kupca</h4>
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-5 rounded-r-lg">
              <p class="text-base text-gray-800">{{ orderStore.selected.notes }}</p>
            </div>
          </div>

          <!-- UPDATE STATUS -->
          <div>
            <h4 class="font-bold text-xl mb-4 text-gray-900">Ažuriraj status</h4>

            <div class="flex flex-wrap gap-3">
              <button
                v-for="(label, status) in statusLabels"
                :key="status"
                @click="async () => {
                  await orderStore.updateStatus(orderStore.selected.id, status)
                  await refreshOrders()
                }"
                :class="orderStore.selected.status === status
                  ? 'bg-[#1976d2] hover:bg-[#1565c0] text-white shadow-lg scale-105'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
                class="px-6 py-3 rounded-xl text-base font-semibold transition-all cursor-pointer"
              >
                {{ label }}
              </button>
            </div>
          </div>

          <!-- DELETE ORDER -->
          <div class="border-t pt-6 mt-6">
            <button
              @click="deleteOrder"
              class="w-full px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl text-base font-semibold transition cursor-pointer"
            >
              Obriši narudžbinu
            </button>
          </div>

        </div>

      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      :show="showConfirmDelete"
      message="Da li ste sigurni da želite da obrišete ovu narudžbinu? Ova akcija je nepovratna."
      title="Potvrda brisanja"
      confirmText="Obriši"
      cancelText="Odustani"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<style scoped>
.order-list-enter-active {
  transition: all 0.4s ease;
}

.order-list-leave-active {
  transition: all 0.3s ease;
}

.order-list-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
}

.order-list-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.95);
}

.order-list-move {
  transition: transform 0.3s ease;
}
</style>
