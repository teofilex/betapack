<script setup>
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import { useRouter } from 'vue-router'
import { useHead } from '@unhead/vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

// SEO Meta Tags for 404 page
useHead({
  title: 'Stranica nije pronađena - 404 | BetaPack',
  meta: [
    { name: 'description', content: 'Stranica koju tražite ne postoji ili je uklonjena. Vratite se na početnu stranicu BetaPack-a i pronađite kvalitetne bravarijske materijale.' },
    { name: 'robots', content: 'noindex, nofollow' }
  ]
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1 flex items-center justify-center py-12 px-4">
      <div class="text-center max-w-2xl mx-auto">
        <!-- 404 Number -->
        <div class="mb-8">
          <h1 class="text-9xl sm:text-[12rem] font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#1976d2] to-[#1565c0] leading-none">
            404
          </h1>
        </div>

        <!-- Message -->
        <div class="mb-8">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Stranica nije pronađena
          </h2>
          <p class="text-lg text-gray-600 mb-2">
            Izvinjavamo se, ali stranica koju tražite ne postoji.
          </p>
          <p class="text-base text-gray-500">
            Možda je uklonjena, premeštena ili je adresa pogrešna.
          </p>
        </div>

        <!-- Illustration -->
        <div class="mb-8">
          <div class="inline-block text-8xl sm:text-9xl opacity-20">
            🔍
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            @click="goHome"
            class="px-8 py-3 bg-[#1976d2] hover:bg-[#1565c0] text-white font-bold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            ← Nazad na početnu
          </button>
          <button
            @click="router.go(-1)"
            class="px-8 py-3 bg-white hover:bg-gray-50 text-gray-900 font-bold rounded-xl border-2 border-gray-300 transition-all duration-300 shadow-md hover:shadow-lg"
          >
            ← Nazad
          </button>
        </div>

        <!-- Helpful Links -->
        <div class="mt-12 pt-8 border-t border-gray-200">
          <p class="text-sm text-gray-500 mb-4">Možda tražite:</p>
          <div class="flex flex-wrap justify-center gap-4">
            <router-link
              to="/"
              class="text-[#1976d2] hover:text-[#1565c0] hover:underline font-medium text-sm"
            >
              🏠 Početna
            </router-link>
            <router-link
              to="/kontakt"
              class="text-[#1976d2] hover:text-[#1565c0] hover:underline font-medium text-sm"
            >
              📞 Kontakt
            </router-link>
            <router-link
              to="/o-nama"
              class="text-[#1976d2] hover:text-[#1565c0] hover:underline font-medium text-sm"
            >
              ℹ️ O nama
            </router-link>
          </div>
        </div>
      </div>
    </main>

    <TheFooter />
  </div>
</template>

