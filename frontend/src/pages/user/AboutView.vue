<script setup>
import { useHead } from '@unhead/vue'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'

useHead({
  title: 'O Nama - BetaPack | Bravarija i Ambalaža',
  meta: [
    { name: 'description', content: 'Beta Pack posluje u prodaji bravarskog materijala i kovanog gvožđa, kao i ambalaže za ugostiteljstvo, dostavu hrane i prehrambene objekte.' },
    { name: 'keywords', content: 'BetaPack, o nama, bravarija Beograd, kovano gvožđe, ambalaža za hranu, ambalaža ugostiteljstvo, Beta Pack Batajnica' },
    { property: 'og:site_name', content: 'BetaPack' },
    { property: 'og:title', content: 'O Nama - BetaPack' },
    { property: 'og:description', content: 'Beta Pack — bravarski materijali i ambalaža za hranu. Kvalitet, brza isporuka i pouzdana saradnja.' },
    { property: 'og:url', content: 'https://www.betapack.co.rs/o-nama' },
    { property: 'og:type', content: 'website' },
    { property: 'og:locale', content: 'sr_RS' }
  ],
  link: [
    { rel: 'canonical', href: 'https://www.betapack.co.rs/o-nama' }
  ]
})

const features = [
  {
    image: '/assets/kvalitet.png',
    fallbackIcon: '🏆',
    title: 'Kvalitet',
    description: 'Kvalitetni proizvodi iz oblasti bravarije i ambalaže za hranu.'
  },
  {
    image: '/assets/brzina.png',
    fallbackIcon: '⚡',
    title: 'Brza isporuka',
    description: 'Efikasna logistika i brza isporuka bez kompromisa na kvalitetu.'
  },
  {
    image: '/assets/cene.png',
    fallbackIcon: '💰',
    title: 'Pristupačne cene',
    description: 'Povoljne cene i pouzdana saradnja za vaše poslovanje.'
  },
  {
    image: '/assets/preciznost.png',
    fallbackIcon: '🤝',
    title: 'Pouzdan partner',
    description: 'Dve oblasti poslovanja — jedan pouzdan partner za vaš biznis.'
  }
]
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1">

      <!-- Hero sekcija -->
      <div class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white py-12 lg:py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4">O nama</h1>
          <p class="text-sm sm:text-base lg:text-lg text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Beta Pack — rešenja za vaš biznis
          </p>
        </div>
      </div>

      <!-- O kompaniji -->
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 lg:py-14">
        <div class="space-y-6 text-sm sm:text-base text-gray-700 leading-relaxed">
          <p class="text-base sm:text-lg text-gray-800">
            <strong class="text-gray-900">Beta Pack</strong> je firma koja posluje kroz dve oblasti: prodaju bravarskog materijala i elemenata od kovanog gvožđa, kao i prodaju ambalaže za ugostiteljstvo, dostavu hrane i prehrambene objekte.
          </p>

          <div class="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-gray-100 border-l-4 border-[#1976d2]">
            <h2 class="text-lg sm:text-xl font-bold text-gray-900 mb-3">Bravarski materijal</h2>
            <p>
              U oblasti bravarskog materijala nudimo elemente od kovanog gvožđa, dekorativne elemente i proizvode namenjene izradi kapija, ograda, gelendera i metalnih konstrukcija.
            </p>
          </div>

          <div class="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-gray-100 border-l-4 border-[#1976d2]">
            <h2 class="text-lg sm:text-xl font-bold text-gray-900 mb-3">Ambalaža</h2>
            <p>
              U oblasti ambalaže nudimo širok asortiman proizvoda za restorane, kafiće, pekare, poslastičarnice, mesare, fast food objekte, maloprodaju i dostavu hrane. Na jednom mestu možete pronaći PET i PP ambalažu, papirnu i kartonsku ambalažu, aluminijumske posude, stiropor ambalažu, kese, čaše, folije i dodatnu opremu.
            </p>
          </div>

          <p class="text-base sm:text-lg text-gray-800">
            Naš cilj je jednostavan — da kupcima obezbedimo kvalitetne proizvode, brzu isporuku, pristupačne cene i pouzdanu saradnju.
          </p>

          <p class="text-center text-xl sm:text-2xl font-bold text-[#1976d2] pt-2">
            Beta Pack — rešenja za vaš biznis.
          </p>
        </div>
      </div>

      <!-- Vrednosti -->
      <div class="bg-gradient-to-b from-white via-gray-50 to-white py-12 lg:py-16 relative overflow-hidden">
        <div class="absolute inset-0 opacity-5">
          <div class="absolute top-0 left-1/4 w-96 h-96 bg-[#1976d2] rounded-full blur-3xl"></div>
          <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-[#1565c0] rounded-full blur-3xl"></div>
        </div>

        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div class="text-center mb-12">
            <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-3">
              Zašto <span class="text-[#1976d2]">Beta Pack</span>?
            </h2>
            <div class="w-24 h-1 bg-gradient-to-r from-[#1976d2] to-[#1565c0] mx-auto rounded-full"></div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            <div
              v-for="feature in features"
              :key="feature.title"
              class="group relative text-center p-8 bg-white/80 backdrop-blur-sm rounded-3xl hover:shadow-2xl transition-all duration-500 border border-gray-200/50 hover:border-gray-300 hover:-translate-y-3 overflow-hidden"
            >
              <div class="relative z-10">
                <div class="flex justify-center mb-6">
                  <div class="relative p-6 rounded-2xl bg-gradient-to-br from-gray-50 via-white to-gray-50 border-2 border-gray-200/50 group-hover:border-gray-300 transition-all duration-500 shadow-lg group-hover:shadow-xl group-hover:scale-110">
                    <img
                      :src="feature.image"
                      :alt="feature.title"
                      class="relative w-20 h-20 sm:w-24 sm:h-24 object-contain transition-all duration-500 group-hover:scale-110"
                      @error="(e) => {
                        e.target.style.display = 'none';
                        const fallback = e.target.parentElement.querySelector('.fallback-icon');
                        if (fallback) fallback.style.display = 'block';
                      }"
                    />
                    <span class="text-5xl hidden fallback-icon relative z-10">{{ feature.fallbackIcon }}</span>
                  </div>
                </div>
                <h3 class="text-lg sm:text-xl font-bold text-gray-900 mb-3">{{ feature.title }}</h3>
                <p class="text-sm sm:text-base text-gray-600 leading-relaxed">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA sekcija -->
      <div class="bg-gradient-to-r from-[#1976d2] to-[#1565c0] py-12 lg:py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold mb-4 lg:mb-6 text-white">
            Spremni da započnemo saradnju?
          </h2>
          <p class="text-sm sm:text-base lg:text-lg mb-8 max-w-2xl mx-auto text-blue-100 leading-relaxed">
            Kontaktirajte nas za ponudu prilagođenu vašim potrebama
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="tel:0653300242"
              class="inline-flex items-center justify-center gap-2 bg-white text-[#1565c0] font-bold px-6 py-3 rounded-xl hover:bg-gray-100 transition-all duration-300 text-sm sm:text-base shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              <span class="text-lg">📞</span>
              <span>Pozovite nas</span>
            </a>
            <router-link
              to="/kontakt"
              class="inline-flex items-center justify-center gap-2 bg-gray-900 text-white font-bold px-6 py-3 rounded-xl hover:bg-gray-800 transition-all duration-300 text-sm sm:text-base shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              <span class="text-lg">✉️</span>
              <span>Pošaljite upit</span>
            </router-link>
          </div>
        </div>
      </div>

    </main>

    <TheFooter />
  </div>
</template>
