<script setup>
import { useHead } from '@unhead/vue'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'

// SEO Meta Tags
useHead({
  title: 'O Nama - BetaPack | 25 Godina Iskustva u Bravariji',
  meta: [
    { name: 'description', content: 'BetaPack - 25 godina iskustva u proizvodnji i prodaji bravarskih materijala. Kvalitet, preciznost, brzina i povoljne cene. Vaš pouzdan partner za kovano gvožđe.' },
    // Open Graph
    { property: 'og:site_name', content: 'BetaPack' },
    { property: 'og:title', content: 'O Nama - BetaPack' },
    { property: 'og:description', content: '25 godina iskustva u bravariji. Kvalitet, preciznost i povoljne cene.' },
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
    image: '/assets/kvalitet.png', // Badge sa checkmark-om - Značka kvaliteta
    fallbackIcon: '🏆',
    title: 'Kvalitet',
    description: 'Koristimo samo najkvalitetnije materijale i moderne tehnologije obrade metala.'
  },
  {
    image: '/assets/preciznost.png', // Meta sa strelicom koja pogada centar
    fallbackIcon: '🎯',
    title: 'Preciznost',
    description: 'Svaki proizvod se izrađuje sa pažnjom na detalje i prema specifikacijama naručioca.'
  },
  {
    image: '/assets/brzina.png', // Brzinomer + štoperica sa checkmark-om
    fallbackIcon: '⚡',
    title: 'Brzina',
    description: 'Efikasna proizvodnja i brza isporuka bez kompromisa na kvalitetu.'
  },
  {
    image: '/assets/cene.png', // Novčići sa strelicom nadole - Smanjenje cene
    fallbackIcon: '💰',
    title: 'Pristupačne cene',
    description: 'Najbolji odnos cene i kvaliteta na tržištu. Direktna prodaja bez posrednika.'
  }
]

const products = [
  'Kovano gvožđe',
  'Kvadratni i pravougaoni profili raznih dimenzija',
  'Grifovani profili i kutije',
  'Dekorativni elementi - cvetovi, listovi, kovanice',
  'Šiljci različitih visina i oblika',
  'Flahovi (obični i grifovani)',
  'L-profili i posebni elementi',
  'Usluge savijanja i obrade metala'
]

const services = [
  'Uvoz i distribucija kvalitetnih materijala za kovane konstrukcije',
  'Obrada gvožđa – sečenje, savijanje, graviranje',
  'Izrada lukova i dekorativnih elemenata',
  'Savetovanje i podrška pri izboru materijala'
]
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1">

      <!-- Hero sekcija -->
      <div class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white py-12 lg:py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold mb-4">O Nama</h1>
          <p class="text-sm sm:text-base lg:text-lg text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Vaš pouzdan partner za kvalitetne bravarijske proizvode već <span class="font-bold text-white">25 godina</span>
          </p>
        </div>
      </div>

      <!-- O kompaniji -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-start">

          <div class="space-y-6">
            <div>
              <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-4 leading-tight">
                Dobrodošli u <span class="text-[#1976d2]">Betapack</span> – mesto gde se tradicija susreće sa kvalitetom!
              </h2>
              <div class="space-y-4 text-sm sm:text-base text-gray-700 leading-relaxed">
                <p class="text-base sm:text-lg">
                  Već <strong class="text-gray-900 font-semibold">25 godina</strong> uspešno poslujemo u oblasti trgovine i obrade gvožđa, specijalizovani za materijale namenjene izradi kovanih ograda, gelendera, nadstrešnica, prozorskih i balkonskih rešetki. Naša ponuda obuhvata širok asortiman proizvoda, od osnovnih elemenata do dekorativnih detalja, uz mogućnost izrade lukova i graviranja po meri.
                </p>
              </div>
            </div>

            <!-- Šta radimo sekcija -->
            <div class="bg-gray-50 rounded-xl p-6 sm:p-8 border-l-4 border-[#1976d2]">
              <h3 class="text-lg sm:text-xl font-bold text-gray-900 mb-4">
                Šta radimo:
              </h3>
              <ul class="space-y-3">
                <li
                  v-for="service in services"
                  :key="service"
                  class="flex items-start gap-3 text-sm sm:text-base text-gray-700"
                >
                  <span class="text-[#1976d2] font-bold flex-shrink-0 mt-0.5">•</span>
                  <span>{{ service }}</span>
                </li>
              </ul>
            </div>
             
            <div class="bg-gray-50 rounded-xl p-5 sm:p-6 border-l-4 border-[#1976d2]">
              <p class="text-sm sm:text-base text-gray-700 leading-relaxed italic">
                U <strong class="text-gray-900 font-semibold">Betapack</strong>-u verujemo da <strong class="text-gray-900">kvalitet</strong>, <strong class="text-gray-900">pouzdanost</strong> i <strong class="text-gray-900">dugovečnost</strong> nisu samo reči; to su vrednosti koje gradimo svakim projektom. <span class="font-semibold text-gray-900">Dobrodošli!</span>
              </p>
            </div>
          </div>

          <div class="bg-gradient-to-br from-[#1976d2] to-[#1565c0] rounded-2xl p-6 sm:p-8 shadow-2xl text-white">
            <h3 class="text-lg sm:text-xl font-bold mb-6">Zašto izabrati nas?</h3>
            <ul class="space-y-4">
              <li class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">✓</span>
                <span class="text-sm sm:text-base">Višegodišnje iskustvo u bravariji</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">✓</span>
                <span class="text-sm sm:text-base">Visok kvalitet materijala i izrade</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">✓</span>
                <span class="text-sm sm:text-base">Konkurentne cene</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">✓</span>
                <span class="text-sm sm:text-base">Brza isporuka</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">✓</span>
                <span class="text-sm sm:text-base">Stručan tim i profesionalna podrška</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">✓</span>
                <span class="text-sm sm:text-base">Mogućnost prilagođavanja po meri</span>
              </li>
            </ul>
          </div>

        </div>
      </div>

      <!-- Vrednosti -->
      <div class="bg-gradient-to-b from-white via-gray-50 to-white py-12 lg:py-16 relative overflow-hidden">
        <!-- Decorative background elements -->
        <div class="absolute inset-0 opacity-5">
          <div class="absolute top-0 left-1/4 w-96 h-96 bg-[#1976d2] rounded-full blur-3xl"></div>
          <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-[#1565c0] rounded-full blur-3xl"></div>
        </div>
        
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div class="text-center mb-12">
            <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-3">
              Naše <span class="text-[#1976d2]">vrednosti</span>
            </h2>
            <div class="w-24 h-1 bg-gradient-to-r from-[#1976d2] to-[#1565c0] mx-auto rounded-full"></div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            <div
              v-for="(feature, index) in features"
              :key="feature.title"
              class="group relative text-center p-8 bg-white/80 backdrop-blur-sm rounded-3xl hover:shadow-2xl transition-all duration-500 border border-gray-200/50 hover:border-gray-300 hover:-translate-y-3 overflow-hidden"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="relative z-10">
                <div class="flex justify-center mb-6">
                  <div class="relative">
                    <!-- Icon container with modern glass effect -->
                    <div class="relative p-6 rounded-2xl bg-gradient-to-br from-gray-50 via-white to-gray-50 border-2 border-gray-200/50 group-hover:border-gray-300 transition-all duration-500 shadow-lg group-hover:shadow-xl group-hover:scale-110 backdrop-blur-sm">
                      <div class="absolute inset-0 bg-gradient-to-br from-white/50 to-transparent rounded-2xl"></div>
                      <img 
                        :src="feature.image" 
                        :alt="feature.title"
                        class="relative w-20 h-20 sm:w-24 sm:h-24 object-contain transition-all duration-500 group-hover:scale-110 group-hover:rotate-3"
                        @error="(e) => { 
                          e.target.style.display = 'none';
                          const fallback = e.target.parentElement.querySelector('.fallback-icon');
                          if (fallback) fallback.style.display = 'block';
                        }"
                      />
                      <span 
                        class="text-5xl hidden fallback-icon relative z-10"
                      >{{ feature.fallbackIcon || '📦' }}</span>
                    </div>
                  </div>
                </div>
                
                <h3 class="text-lg sm:text-xl font-bold text-gray-900 mb-3 transition-colors duration-300 relative">
                  <span class="relative z-10">{{ feature.title }}</span>
                </h3>
                <p class="text-sm sm:text-base text-gray-600 leading-relaxed relative z-10 group-hover:text-gray-700 transition-colors duration-300">
                  {{ feature.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Proizvodi -->
      <div class="bg-gray-50 py-12 lg:py-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-xl sm:text-2xl lg:text-3xl font-bold text-center text-gray-900 mb-8 lg:mb-12">
            Naši <span class="text-[#1976d2]">proizvodi i usluge</span>
          </h2>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 sm:gap-5 max-w-5xl mx-auto">
            <div
              v-for="product in products"
              :key="product"
              class="flex items-start gap-3 bg-white p-4 sm:p-5 rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100 hover:border-[#1976d2]"
            >
              <span class="text-[#1976d2] text-xl sm:text-2xl font-bold flex-shrink-0 mt-0.5">✓</span>
              <span class="text-sm sm:text-base text-gray-700 font-medium leading-relaxed">{{ product }}</span>
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
            Kontaktirajte nas za <strong class="text-white">besplatnu konsultaciju</strong> i ponudu prilagođenu vašim potrebama
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
