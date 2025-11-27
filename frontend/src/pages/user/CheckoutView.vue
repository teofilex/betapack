<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { useCartStore } from '@/store/cart'
import { api } from '@/services/api'
import { getImageUrl } from '@/composables/useImageUrl'

const router = useRouter()
const cartStore = useCartStore()

const form = ref({
  customer_name: '',
  customer_phone: '',
  customer_email: '',
  delivery_address: '',
  notes: ''
})

const submitting = ref(false)
const errors = ref({})

const formatPrice = (price) => {
  return new Intl.NumberFormat('sr-RS', {
    style: 'currency',
    currency: 'RSD',
    minimumFractionDigits: 0
  }).format(price)
}

const cartItems = computed(() => cartStore.items)
const cartTotal = computed(() => cartStore.total)

const validatePhone = (phone) => {
  // Serbian phone validation: 06X/XXXXXXX or +381XXXXXXXXX
  const pattern = /^(\+381|0)[0-9]{8,9}$/
  return pattern.test(phone.replace(/[\s\-\/]/g, ''))
}

const validateField = (fieldName) => {
  // Clear error for this field
  delete errors.value[fieldName]

  switch (fieldName) {
    case 'customer_name':
      if (!form.value.customer_name.trim()) {
        errors.value.customer_name = 'Ime je obavezno'
      }
      break

    case 'customer_phone':
      if (!form.value.customer_phone.trim()) {
        errors.value.customer_phone = 'Broj telefona je obavezan'
      } else if (!validatePhone(form.value.customer_phone)) {
        errors.value.customer_phone = 'Unesite ispravan broj telefona (npr: 0641234567)'
      }
      break

    case 'customer_email':
      if (form.value.customer_email && form.value.customer_email.trim()) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailPattern.test(form.value.customer_email.trim())) {
          errors.value.customer_email = 'Unesite ispravnu email adresu'
        }
      }
      break

    case 'delivery_address':
      if (!form.value.delivery_address.trim()) {
        errors.value.delivery_address = 'Adresa dostave je obavezna'
      }
      break
  }
}

const validateForm = () => {
  errors.value = {}

  if (!form.value.customer_name.trim()) {
    errors.value.customer_name = 'Ime je obavezno'
  }

  if (!form.value.customer_phone.trim()) {
    errors.value.customer_phone = 'Broj telefona je obavezan'
  } else if (!validatePhone(form.value.customer_phone)) {
    errors.value.customer_phone = 'Unesite ispravan broj telefona (npr: 0641234567)'
  }

  if (form.value.customer_email && form.value.customer_email.trim()) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailPattern.test(form.value.customer_email.trim())) {
      errors.value.customer_email = 'Unesite ispravnu email adresu'
    }
  }

  if (!form.value.delivery_address.trim()) {
    errors.value.delivery_address = 'Adresa dostave je obavezna'
  }

  return Object.keys(errors.value).length === 0
}

const submitOrder = async () => {
  if (!validateForm()) return

  if (cartItems.value.length === 0) {
    alert('Vaša korpa je prazna!')
    return
  }

  submitting.value = true

  try {
    // Prepare order data
    const orderData = {
      customer_name: form.value.customer_name.trim(),
      customer_phone: form.value.customer_phone.replace(/[\s\-\/]/g, ''),
      customer_email: form.value.customer_email?.trim() || null,
      delivery_address: form.value.delivery_address.trim(),
      notes: form.value.notes?.trim() || null,
      items: cartItems.value.map(item => ({
        product_id: item.id,
        variant_id: item.selectedVariant?.id || null,
        quantity: item.quantity
      }))
    }
    
    // Remove null fields to avoid sending them (backend will handle defaults)
    // Actually, let's send null explicitly for optional fields
    if (!orderData.customer_email) orderData.customer_email = null
    if (!orderData.notes) orderData.notes = null

    // Submit order
    const response = await api.post('orders/', orderData)

    // Clear cart
    cartStore.clear()

    // Redirect to success page
    router.push({
      name: 'order-success',
      params: { orderId: response.data.id }
    })

  } catch (error) {
    console.error('Order submission error:', error)

    // Handle validation errors from backend
    if (error.response?.data && typeof error.response.data === 'object') {
      const backendErrors = error.response.data

      // Map backend field errors to frontend errors
      if (backendErrors.customer_name) {
        errors.value.customer_name = Array.isArray(backendErrors.customer_name)
          ? backendErrors.customer_name[0]
          : backendErrors.customer_name
      }
      if (backendErrors.customer_phone) {
        errors.value.customer_phone = Array.isArray(backendErrors.customer_phone)
          ? backendErrors.customer_phone[0]
          : backendErrors.customer_phone
      }
      if (backendErrors.customer_email) {
        errors.value.customer_email = Array.isArray(backendErrors.customer_email)
          ? backendErrors.customer_email[0]
          : backendErrors.customer_email
      }
      if (backendErrors.delivery_address) {
        errors.value.delivery_address = Array.isArray(backendErrors.delivery_address)
          ? backendErrors.delivery_address[0]
          : backendErrors.delivery_address
      }

      // If there are field-specific errors, show them
      if (Object.keys(errors.value).length > 0) {
        alert('Molimo ispravite označena polja pre slanja narudžbine.')
        return
      }
    }

    // Generic error message
    const errorMessage = error.response?.data?.detail ||
                        error.response?.data?.message ||
                        error.message ||
                        'Došlo je do greške pri slanju narudžbine. Molimo pokušajte ponovo ili nas kontaktirajte telefonom.'
    alert(errorMessage)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <h1 class="text-4xl font-bold text-gray-900 mb-8">Finalizacija narudžbine</h1>

        <div v-if="cartItems.length === 0" class="bg-white rounded-xl shadow-lg p-12 text-center">
          <span class="text-6xl text-gray-300 mb-4 block">🛒</span>
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Vaša korpa je prazna</h2>
          <p class="text-gray-600 mb-6">Dodajte proizvode u korpu pre naručivanja</p>
          <button
            @click="router.push('/')"
            class="bg-[#1976d2] hover:bg-[#1565c0] text-white font-semibold px-8 py-3 rounded-lg transition"
          >
            Pogledaj proizvode
          </button>
        </div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">

          <!-- Checkout Form -->
          <div class="lg:col-span-2">
            <div class="bg-white rounded-xl shadow-lg p-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-6">Vaši podaci</h2>

              <form @submit.prevent="submitOrder" class="space-y-6">

                <!-- Name -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Ime i prezime <span class="text-red-600">*</span>
                  </label>
                  <input
                    v-model="form.customer_name"
                    @blur="validateField('customer_name')"
                    required
                    type="text"
                    class="w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-[#1976d2] focus:border-transparent transition-colors"
                    :class="errors.customer_name ? 'border-red-500 bg-red-50' : 'border-gray-300'"
                    placeholder="Petar Petrović"
                  />
                  <p v-if="errors.customer_name" class="text-red-600 text-sm mt-1 font-medium">{{ errors.customer_name }}</p>
                </div>

                <!-- Phone -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Broj telefona <span class="text-red-600">*</span>
                  </label>
                  <input
                    v-model="form.customer_phone"
                    @blur="validateField('customer_phone')"
                    required
                    type="tel"
                    class="w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-[#1976d2] focus:border-transparent transition-colors"
                    :class="errors.customer_phone ? 'border-red-500 bg-red-50' : 'border-gray-300'"
                    placeholder="060/123-4567"
                  />
                  <p v-if="errors.customer_phone" class="text-red-600 text-sm mt-1 font-medium">{{ errors.customer_phone }}</p>
                  <p v-else class="text-gray-500 text-sm mt-1">Format: 06X/XXX-XXXX ili +381XXXXXXXXX</p>
                </div>

                <!-- Email -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Email <span class="text-gray-400">(opciono)</span>
                  </label>
                  <input
                    v-model="form.customer_email"
                    @blur="validateField('customer_email')"
                    type="email"
                    class="w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-[#1976d2] focus:border-transparent transition-colors"
                    :class="errors.customer_email ? 'border-red-500 bg-red-50' : 'border-gray-300'"
                    placeholder="vas.email@primer.com"
                  />
                  <p v-if="errors.customer_email" class="text-red-600 text-sm mt-1 font-medium">{{ errors.customer_email }}</p>
                </div>

                <!-- Address -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Adresa dostave <span class="text-red-600">*</span>
                  </label>
                  <textarea
                    v-model="form.delivery_address"
                    @blur="validateField('delivery_address')"
                    required
                    rows="2"
                    class="w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-[#1976d2] focus:border-transparent resize-none transition-colors"
                    :class="errors.delivery_address ? 'border-red-500 bg-red-50' : 'border-gray-300'"
                    placeholder="Ulica i broj, Grad"
                  ></textarea>
                  <p v-if="errors.delivery_address" class="text-red-600 text-sm mt-1 font-medium">{{ errors.delivery_address }}</p>
                </div>

                <!-- Notes -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Napomena <span class="text-gray-400">(opciono)</span>
                  </label>
                  <textarea
                    v-model="form.notes"
                    rows="3"
                    class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1976d2] focus:border-transparent resize-none transition-colors"
                    placeholder="Dodatne informacije o narudžbini..."
                  ></textarea>
                </div>

                <!-- Info Box -->
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 class="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                    <span>ℹ️</span>
                    <span>Kako funkcioniše naručivanje?</span>
                  </h3>
                  <ul class="text-sm text-blue-800 space-y-1">
                    <li>1. Popunite formu sa vašim podacima</li>
                    <li>2. Kliknite "Pošalji narudžbinu"</li>
                    <li>3. Primićete SMS potvrdu na vaš telefon</li>
                    <li>4. Kontaktiraćemo vas telefonom za dodatne detalje</li>
                    <li>5. Finalna cena i uslovi dostave se dogovaraju telefonski</li>
                  </ul>
                </div>

              </form>
            </div>
          </div>

          <!-- Order Summary -->
          <div class="lg:col-span-1">
            <div class="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              <h2 class="text-xl font-bold text-gray-900 mb-6">Pregled narudžbine</h2>

              <!-- Cart Items -->
              <div class="space-y-4 mb-6">
                <div
                  v-for="item in cartItems"
                  :key="item.id"
                  class="flex gap-3 pb-4 border-b"
                >
                  <div class="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                    <img
                      v-if="item.images && item.images.length > 0"
                      :src="getImageUrl(item.images[0].image)"
                      :alt="item.name"
                      class="w-full h-full object-contain"
                    />
                    <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                      <span class="text-2xl">📦</span>
                    </div>
                  </div>

                  <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-gray-900 text-sm line-clamp-1">{{ item.name }}</h3>
                    <p v-if="item.selectedVariant" class="text-xs text-gray-600">{{ item.selectedVariant.name }}</p>
                    <p class="text-sm text-gray-600">{{ item.quantity }} × {{ formatPrice(item.current_price) }}</p>
                  </div>

                  <div class="text-right">
                    <p class="font-semibold text-gray-900">{{ formatPrice(item.current_price * item.quantity) }}</p>
                  </div>
                </div>
              </div>

              <!-- Total -->
              <div class="border-t pt-4 mb-6">
                <div class="flex justify-between items-center text-xl font-bold">
                  <span class="text-gray-900">Ukupno:</span>
                  <span class="text-green-700">{{ formatPrice(cartTotal) }}</span>
                </div>
                <p class="text-xs text-gray-500 mt-2">Finalna cena će biti potvrđena telefonom</p>
              </div>

              <!-- Submit Button -->
              <button
                @click="submitOrder"
                :disabled="submitting"
                class="w-full bg-[#1976d2] hover:bg-[#1565c0] text-white font-bold py-4 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ submitting ? 'Slanje...' : 'Pošalji narudžbinu' }}
              </button>

              <!-- Contact -->
              <div class="mt-6 pt-6 border-t text-center">
                <p class="text-sm text-gray-600 mb-3">Ili nas pozovite direktno:</p>
                <a
                  href="tel:0653300242"
                  class="inline-flex items-center gap-2 text-[#1565c0] hover:text-[#1565c0] font-semibold"
                >
                  <span>📞</span>
                  <span>065/330 02 42</span>
                </a>
              </div>
            </div>
          </div>

        </div>

      </div>
    </main>

    <TheFooter />
  </div>
</template>
