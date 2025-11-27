<script setup>
import { useRoute, useRouter } from 'vue-router'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'

const route = useRoute()
const router = useRouter()

const orderId = route.params.orderId
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1 flex items-center justify-center py-16">
      <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="bg-white rounded-2xl shadow-xl p-12 text-center">

          <!-- Success Icon -->
          <div class="mb-6">
            <div class="inline-flex items-center justify-center w-24 h-24 bg-green-100 rounded-full">
              <span class="text-5xl">✓</span>
            </div>
          </div>

          <!-- Title -->
          <h1 class="text-3xl font-bold text-gray-900 mb-4">
            Narudžbina uspešno poslata!
          </h1>

          <!-- Order Number -->
          <p class="text-lg text-gray-600 mb-8">
            Broj narudžbine: <span class="font-semibold text-[#1565c0]">#{{ orderId }}</span>
          </p>

          <!-- Info -->
          <div class="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8 text-left">
            <h2 class="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <span>📋</span>
              <span>Šta dalje?</span>
            </h2>
            <ul class="space-y-2 text-blue-800">
              <li class="flex items-start gap-2">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Vaša narudžbina je uspešno primljena</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Naš tim će vas kontaktirati telefonom u najkraćem roku</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Dogovoriće se finalna cena i uslovi isporuke</span>
              </li>
              <li class="flex items-start gap-2">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Vaša narudžbina će biti realizovana</span>
              </li>
            </ul>
          </div>

          <!-- Contact Info -->
          <div class="bg-gray-50 rounded-xl p-6 mb-8">
            <h3 class="font-semibold text-gray-900 mb-3">Kontakt informacije</h3>
            <div class="space-y-2">
              <a
                href="tel:0653300242"
                class="block text-[#1565c0] hover:text-[#1565c0] font-semibold text-lg"
              >
                📞 065/330 02 42
              </a>
              <a
                href="tel:0638757725"
                class="block text-[#1565c0] hover:text-[#1565c0] font-semibold text-lg"
              >
                📞 063/8757 725
              </a>
              <a
                href="mailto:office@betapack.co.rs"
                class="block text-blue-600 hover:text-blue-700"
              >
                ✉️ office@betapack.co.rs
              </a>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              @click="router.push('/')"
              class="bg-[#1976d2] hover:bg-[#1565c0] text-white font-semibold px-8 py-3 rounded-lg transition"
            >
              Vrati se na početnu
            </button>
            <button
              @click="router.push('/kontakt')"
              class="bg-white hover:bg-gray-50 text-gray-900 font-semibold px-8 py-3 rounded-lg border-2 border-gray-300 transition"
            >
              Kontaktirajte nas
            </button>
          </div>

          <!-- Thank you -->
          <p class="text-gray-600 mt-8">
            Hvala vam što ste izabrali našu bravariju! 🔨
          </p>

        </div>
      </div>
    </main>

    <TheFooter />
  </div>
</template>
