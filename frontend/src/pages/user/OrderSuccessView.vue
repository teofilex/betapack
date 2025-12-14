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

    <main class="flex-1 flex items-center justify-center py-8">
      <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="bg-white rounded-xl shadow-xl p-6 lg:p-8 text-center">

          <!-- Success Icon -->
          <div class="mb-4">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full">
              <span class="text-3xl">✓</span>
            </div>
          </div>

          <!-- Title -->
          <h1
 class="text-xl lg:text-2xl font-bold text-gray-900 mb-3">
            Uspešno ste poručili robu! 
          </h1>
<p class="text-sm lg:text-base text-gray-600 mb-4">
           Uskoro ćemo vas kontaktirati da potvrdimo porudžbinu.
          </p>
          <!-- Order Number -->
          <p class="text-sm lg:text-base text-gray-600 mb-4">
            Broj narudžbine: <span class="font-semibold text-[#1565c0]">#{{ orderId }}</span>
          </p>

          <!-- Info -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 text-left">
            <h2 class="font-semibold text-sm text-blue-900 mb-2 flex items-center gap-1.5">
              <span>📋</span>
              <span>Šta dalje?</span>
            </h2>
            <ul class="space-y-1.5 text-xs text-blue-800">
              <li class="flex items-start gap-1.5">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Vaša narudžbina je uspešno primljena</span>
              </li>
              <li class="flex items-start gap-1.5">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Naš tim će vas kontaktirati telefonom u najkraćem roku</span>
              </li>
              <li class="flex items-start gap-1.5">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Potvrđujemo porudžbinu i uslove isporuke</span>
              </li>
              <li class="flex items-start gap-1.5">
                <span class="text-green-600 mt-0.5">✓</span>
                <span>Vaša narudžbina će biti realizovana</span>
              </li>
            </ul>
          </div>

          <!-- Contact Info -->
          <div class="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 class="font-semibold text-sm text-gray-900 mb-2">Kontakt informacije</h3>
            <div class="space-y-1.5">
              <a
                href="tel:0653300242"
                class="block text-[#1565c0] hover:text-[#1565c0] font-semibold text-sm cursor-pointer"
              >
                📞 065/330 02 42
              </a>
              <a
                href="tel:0638757725"
                class="block text-[#1565c0] hover:text-[#1565c0] font-semibold text-sm cursor-pointer"
              >
                📞 063/8757 725
              </a>
              <a
                href="mailto:office@betapack.co.rs"
                class="block text-sm text-blue-600 hover:text-blue-700 cursor-pointer"
              >
                ✉️ office@betapack.co.rs
              </a>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-2 justify-center">
            <button
              @click="router.push('/')"
              class="bg-[#1976d2] hover:bg-[#1565c0] text-white font-semibold px-4 py-2 rounded-lg transition cursor-pointer text-sm"
            >
              Vrati se na početnu
            </button>
            <button
              @click="router.push('/kontakt')"
              class="bg-white hover:bg-gray-50 text-gray-900 font-semibold px-4 py-2 rounded-lg border border-gray-300 transition cursor-pointer text-sm"
            >
              Kontaktirajte nas
            </button>
          </div>

          <!-- Thank you -->
          <p class="text-sm text-gray-600 mt-4">
            Hvala vam što ste izabrali našu bravariju!
          </p>

        </div>
      </div>
    </main>

    <TheFooter />
  </div>
</template>
