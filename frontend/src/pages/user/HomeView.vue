<script setup>
import { useHead } from '@unhead/vue'
import { useRouter } from 'vue-router'
import { STORES } from '@/config/stores'

const router = useRouter()

useHead({
  title: 'BetaPack | Gvožđara i Ambalaža Beograd',
  meta: [
    {
      name: 'description',
      content: 'Beta Pack — izaberite oblast poslovanja: bravarski materijal i kovano gvožđe ili ambalaža za ugostiteljstvo i dostavu hrane.'
    }
  ],
  link: [
    {
      rel: 'stylesheet',
      href: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&display=swap'
    }
  ]
})

const sections = [
  {
    store: STORES.steel,
    title: 'Bravarski materijal i kovano gvožđe',
    tags: ['Kapije', 'Ograde', 'Dekorativni elementi'],
    buttonText: 'Pogledaj ponudu',
    align: 'left'
  },
  {
    store: STORES.ambalaza,
    title: 'Ambalaža za ugostiteljstvo i dostavu',
    tags: ['PET', 'PP', 'papir', 'alu', 'folije'],
    buttonText: 'Pogledaj asortiman',
    align: 'right'
  }
]

const selectStore = (path) => {
  router.push(path)
}

const goTo = (path) => {
  router.push(path)
}
</script>

<template>
  <div class="home-page min-h-screen flex flex-col bg-[#0a1628] text-white">
    <header class="relative z-20 border-b border-white/10 bg-[#0a1628]/80 backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 cursor-pointer" @click="goTo('/')">
          <img src="/betapack-logo.png" alt="Beta Pack Logo" class="h-10 w-auto" />
          <div class="text-lg font-bold tracking-wide">BETA PACK</div>
        </div>
        <nav class="flex items-center gap-1 sm:gap-3">
          <button
            @click="goTo('/o-nama')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition font-semibold text-sm cursor-pointer"
          >
            O nama
          </button>
          <button
            @click="goTo('/kontakt')"
            class="text-gray-300 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition font-semibold text-sm cursor-pointer"
          >
            Kontakt
          </button>
        </nav>
      </div>
    </header>

    <main class="relative flex-1 flex flex-col min-h-0">
      <img
        src="/Betapack-home.jpeg"
        alt="Beta Pack — bravarski materijal i ambalaža"
        class="absolute inset-0 w-full h-full object-cover"
        fetchpriority="high"
      />
      <div class="absolute inset-0 bg-gradient-to-b from-[#0a1628]/70 via-[#0a1628]/25 to-[#0a1628]/75"></div>

      <!-- Diagonal accent -->
      <div class="home-diagonal pointer-events-none absolute inset-0 z-[1]" aria-hidden="true"></div>

      <div class="relative z-10 flex flex-col flex-1">
        <div class="text-center pt-8 md:pt-12 px-4">
          <p class="home-brand text-[#c9a84c] text-xl md:text-2xl tracking-[0.2em] uppercase mb-2">Beta Pack</p>
          <h1 class="home-title text-white text-3xl sm:text-3xl md:text-4xl lg:text-5xl leading-tight tracking-tight">
            Izaberite oblast poslovanja
          </h1>
        </div>

        <div class="flex-1 grid grid-cols-1 md:grid-cols-2 gap-0 mt-6 md:mt-10">
          <button
            v-for="section in sections"
            :key="section.store.id"
            @click="selectStore(section.store.path)"
            class="home-panel group flex flex-col items-center justify-end px-6 sm:px-10 pb-12 md:pb-20 pt-8 min-h-[340px] md:min-h-0 cursor-pointer transition-all duration-300 hover:bg-black/20"
            :class="section.align === 'left' ? 'md:items-center md:pr-16' : 'md:items-center md:pl-16'"
          >
            <div class="flex flex-col items-center text-center max-w-lg">
              <!-- Icons -->
              <div
                v-if="section.store.id === 'steel'"
                class="mb-6 text-[#c9a84c] opacity-90 group-hover:scale-105 transition-transform duration-300"
              >
                <svg class="w-16 h-16 md:w-20 md:h-20" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M8 48V20l24-12 24 12v28" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M8 20l24 12 24-12M32 32v16" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M20 36c4-8 8-12 12-12s8 4 12 12" stroke-linecap="round"/>
                </svg>
              </div>
              <div
                v-else
                class="mb-6 text-[#c9a84c] opacity-90 group-hover:scale-105 transition-transform duration-300"
              >
                <svg class="w-16 h-16 md:w-20 md:h-20" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M16 24h32l-4 28H20L16 24z" stroke-linejoin="round"/>
                  <path d="M24 24V16a8 8 0 0 1 16 0v8" stroke-linecap="round"/>
                  <path d="M28 36h8M32 32v8" stroke-linecap="round"/>
                </svg>
              </div>

              <h2 class="home-section-title text-lg sm:text-xl md:text-2xl lg:text-3xl text-white mb-3 leading-snug drop-shadow-lg">
                {{ section.title }}
              </h2>

              <p class="home-tags text-[#c9a84c] text-sm sm:text-base md:text-lg tracking-wide mb-6">
                {{ section.tags.join(' • ') }}
              </p>

              <span
                class="home-btn inline-flex items-center gap-3 text-sm md:text-base px-8 py-3.5 rounded-sm transition-all duration-300 group-hover:gap-4"
                :class="section.store.id === 'steel' ? 'home-btn-steel' : 'home-btn-ambalaza'"
              >
                {{ section.buttonText }}
                <span
                  class="home-btn-arrow text-lg leading-none transition-transform duration-300 group-hover:translate-x-1"
                >→</span>
              </span>
            </div>
          </button>
        </div>
      </div>
    </main>

    <footer class="relative z-20 border-t border-white/10 bg-[#0a1628]/90 py-5 text-center text-gray-400 text-sm">
      <p>BetaPack d.o.o. · Pukovnika Milenka Pavlovića 159 A, Beograd</p>
      <p class="mt-1">📞 +381 65 330 02 42 · ✉️ office@betapack.co.rs</p>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  font-family: 'Montserrat', 'Inter', sans-serif;
}

.home-brand {
  font-weight: 700;
}

.home-title {
  font-weight: 800;
}

.home-section-title {
  font-weight: 800;
}

.home-tags {
  font-weight: 700;
}

.home-btn {
  font-weight: 700;
  letter-spacing: 0.04em;
  min-width: 220px;
  justify-content: center;
}

.home-btn-steel {
  background: rgba(8, 18, 36, 0.92);
  border: 1.5px solid #c9a84c;
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}

.home-btn-steel .home-btn-arrow {
  color: #c9a84c;
}

.home-panel:hover .home-btn-steel {
  background: rgba(10, 22, 44, 0.98);
  border-color: #dfc56a;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.45);
}

.home-btn-ambalaza {
  background: linear-gradient(180deg, #e2c878 0%, #c9a84c 45%, #a8843a 100%);
  border: none;
  color: #0a1628;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.home-btn-ambalaza .home-btn-arrow {
  color: #0a1628;
}

.home-panel:hover .home-btn-ambalaza {
  background: linear-gradient(180deg, #ebd896 0%, #d4b35a 45%, #b8944a 100%);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
}

.home-diagonal::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  background: linear-gradient(180deg, transparent, #c9a84c 20%, #c9a84c 80%, transparent);
  transform: translateX(-50%) rotate(12deg);
  transform-origin: center;
  opacity: 0.6;
  box-shadow: 0 0 12px rgba(201, 168, 76, 0.4);
}

@media (max-width: 767px) {
  .home-diagonal::after {
    display: none;
  }
}
</style>
