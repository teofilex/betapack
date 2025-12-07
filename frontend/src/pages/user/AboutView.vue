<script setup>
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'

const features = [
  {
    icon: '⚒️',
    title: 'Kvalitet',
    description: 'Koristimo samo najkvalitetnije materijale i moderne tehnologije obrade metala.'
  },
  {
    icon: '🎯',
    title: 'Preciznost',
    description: 'Svaki proizvod se izrađuje sa pažnjom na detalje i prema specifikacijama naručioca.'
  },
  {
    icon: '⚡',
    title: 'Brzina',
    description: 'Efikasna proizvodnja i brza isporuka bez kompromisa na kvalitetu.'
  },
  {
    icon: '💰',
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
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <TheHeader />

    <main class="flex-1">

      <!-- Hero sekcija -->
      <div class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white py-8">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 class="text-xl lg:text-2xl font-bold mb-2">O nama</h1>
          <p class="text-xs lg:text-sm text-gray-300 max-w-3xl mx-auto">
            Vaš pouzdan partner za kvalitetne bravarijske proizvode već 25 godina
          </p>
        </div>
      </div>

      <!-- O kompaniji -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 items-center">

          <div>
            <h2 class="text-lg lg:text-xl font-bold text-gray-900 mb-3">Beta Pack d.o.o.</h2>
            <div class="space-y-3 text-sm text-gray-700 leading-relaxed">
              <p>
                <strong>Beta Pack d.o.o.</strong> je kompanija sa dugogodišnjim iskustvom u oblasti obrade kovanog gvožđa i proizvodnje bravarskih proizvoda.
                Od našeg osnivanja posvećeni smo pružanju vrhunskog kvaliteta i pouzdane usluge našim klijentima.
              </p>
              <p>             
                 Specijalizovani smo za proizvodnju širokog spektra bravarskih proizvoda. Naši materijali koriste se za izradu kvalitetnih ograda, kapija, gelendera, profila i dekorativnih elemenata od kovanog gvožđa.
              </p>
              <p>
                Naš tim stručnjaka koristi moderne tehnologije i tradicionalne tehnike obrade metala kako bi
                svakom klijentu pružio proizvod koji u potpunosti zadovoljava njihove potrebe i standarde kvaliteta.
              </p>
              <p>
                Nalazimo se u Zemun-Batajnici, gde raspolažemo modernim proizvodnim pogonima i
                skladištem kvalitetnih materijala, što nam omogućava brzu i efikasnu realizaciju vaših projekata.
              </p>
            </div>
          </div>

          <div class="bg-gradient-to-br from-#1976d2 to-#1565c0 rounded-2xl p-6 shadow-2xl">
            <h3 class="text-xl font-bold mb-5">Zašto izabrati nas?</h3>
            <ul class="space-y-3">
              <li class="flex items-start gap-2.5">
                <span class="text-xl">✓</span>
                <span>Višegodišnje iskustvo u bravаriji</span>
              </li>
              <li class="flex items-start gap-2.5">
                <span class="text-xl">✓</span>
                <span>Visok kvalitet materijala i izrade</span>
              </li>
              <li class="flex items-start gap-2.5">
                <span class="text-xl">✓</span>
                <span>Konkurentne cene</span>
              </li>
              <li class="flex items-start gap-2.5">
                <span class="text-xl">✓</span>
                <span>Brza isporuka</span>
              </li>
              <li class="flex items-start gap-2.5">
                <span class="text-xl">✓</span>
                <span>Stručan tim i profesionalna podrška</span>
              </li>
              <li class="flex items-start gap-2.5">
                <span class="text-xl">✓</span>
                <span>Mogućnost prilagođavanja po meri</span>
              </li>
            </ul>
          </div>

        </div>
      </div>

      <!-- Vrednosti -->
      <div class="bg-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-2xl font-bold text-center text-gray-900 mb-9">Naše vrednosti</h2>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div
              v-for="feature in features"
              :key="feature.title"
              class="text-center p-5 bg-gray-50 rounded-xl hover:shadow-lg transition"
            >
              <div class="text-4xl mb-3">{{ feature.icon }}</div>
              <h3 class="text-lg font-bold text-gray-900 mb-2">{{ feature.title }}</h3>
              <p class="text-gray-600">{{ feature.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Proizvodi -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 class="text-2xl font-bold text-center text-gray-900 mb-9">Naši proizvodi i usluge</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-4xl mx-auto">
          <div
            v-for="product in products"
            :key="product"
            class="flex items-center gap-2.5 bg-white p-3 rounded-lg shadow hover:shadow-md transition"
          >
            <span class="text-[#1976d2] text-lg">✓</span>
            <span class="text-sm text-gray-700">{{ product }}</span>
          </div>
        </div>
      </div>

      <!-- CTA sekcija -->
      <div class="bg-gradient-to-r from-#1976d2 to-#1565c0 py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 class="text-2xl font-bold mb-5">
            Spremni da započnemo saradnju?
          </h2>
          <p class="text-lg mb-6 max-w-2xl mx-auto">
            Kontaktirajte nas za besplatnu konsultaciju i ponudu prilagođenu vašim potrebama
          </p>
          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <a
              href="tel:0653300242"
              class="inline-flex items-center justify-center gap-2 bg-white text-[#1565c0] font-semibold px-6 py-3 rounded-lg hover:bg-gray-100 transition text-base"
            >
              <span>📞</span>
              <span>Pozovite nas</span>
            </a>
            <router-link
              to="/kontakt"
              class="inline-flex items-center justify-center gap-2 bg-gray-900 text-white font-semibold px-6 py-3 rounded-lg hover:bg-gray-800 transition text-base"
            >
              <span>✉️</span>
              <span>Pošaljite upit</span>
            </router-link>
          </div>
        </div>
      </div>

    </main>

    <TheFooter />
  </div>
</template>
