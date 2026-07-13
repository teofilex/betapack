<script setup>
import { useHead } from '@unhead/vue'
import { useRouter } from 'vue-router'
import { STORES } from '@/config/stores'
import StoreIcon from '@/components/StoreIcon.vue'

const router = useRouter()
const HOME_IMAGE = '/betapackHomeNew.jpg'

useHead({
  title: 'BetaPack | Kovano gvožđe i Ambalaža Beograd',
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
    mobileImage: '/steelMobileVersion.jpg',
    align: 'left'
  },
  {
    store: STORES.ambalaza,
    title: 'Ambalaža za ugostiteljstvo i dostavu',
    tags: ['PET', 'PP', 'papir', 'alu', 'folije'],
    buttonText: 'Pogledaj asortiman',
    mobileImage: '/ambalazaMobileVersion.jpg',
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
    <header class="relative z-20 border-b border-white/10 bg-[#0a1628]/90 backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3 cursor-pointer" @click="goTo('/')">
          <img src="/betapack-logo.png" alt="Beta Pack Logo" class="h-10 lg:h-12 w-auto" />
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

    <main class="relative flex-1 flex flex-col min-h-0 bg-[#0a1628]">
      <!-- Hero pozadina -->
      <img
        :src="HOME_IMAGE"
        alt=""
        aria-hidden="true"
        class="home-hero-image absolute inset-0 w-full h-full object-cover object-center hidden md:block"
        fetchpriority="high"
      />

      <!-- Overlay — tamni gradient + blagi vignette -->
      <div class="absolute inset-0 home-overlay hidden md:block"></div>
      <div class="absolute inset-0 home-vignette hidden md:block pointer-events-none"></div>

      <!-- Dijagonalna zlatna linija -->
      <div class="home-diagonal pointer-events-none absolute inset-0 z-[1] hidden md:block" aria-hidden="true"></div>

      <div class="relative z-10 flex flex-col flex-1">
        <div class="text-center pt-8 md:pt-12 px-4 home-header">
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
            class="home-panel group relative overflow-hidden flex flex-col items-stretch cursor-pointer transition-all duration-300 md:hover:bg-black/15"
            :class="[
              section.align === 'left' ? 'md:items-center md:pr-16' : 'md:items-center md:pl-16',
              section.store.id === 'steel' ? 'home-panel-steel' : 'home-panel-ambalaza'
            ]"
          >
            <!-- Mobilni: slika po sekciji -->
            <div
              class="home-panel-visual md:hidden relative w-full flex-shrink-0 overflow-hidden bg-[#0a1628]"
              :class="
                section.store.id === 'ambalaza'
                  ? 'flex items-center justify-center'
                  : 'min-h-[240px] sm:min-h-[280px] h-[240px] sm:h-[280px]'
              "
            >
              <img
                :src="section.mobileImage"
                :alt="section.title"
                class="w-full"
                :class="
                  section.store.id === 'ambalaza'
                    ? 'h-auto object-contain'
                    : 'absolute inset-0 h-full object-cover object-center'
                "
              />
            </div>

            <div
              class="home-panel-body relative z-10 flex flex-col items-center justify-end text-center px-6 sm:px-10 pb-10 md:pb-20 pt-6 md:pt-8 flex-1 max-w-lg mx-auto w-full"
            >
              <div class="home-icon-ring mb-5 text-[#c9a84c] group-hover:scale-105 transition-transform duration-300">
                <StoreIcon :store-id="section.store.id" size="lg" />
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
                <span class="home-btn-arrow text-lg leading-none transition-transform duration-300 group-hover:translate-x-1">→</span>
              </span>
            </div>
          </button>
        </div>
      </div>
    </main>

    <footer class="relative z-20 border-t border-white/10 bg-[#0a1628]/95 py-5 text-center text-gray-400 text-sm">
      <p>BetaPack d.o.o. · Pukovnika Milenka Pavlovića 159 A, Beograd</p>
      <p class="mt-1">📞 +381 65 330 02 42 · ✉️ office@betapack.co.rs</p>
    </footer>
  </div>
</template>

<style scoped>
.home-page {
  font-family: 'Montserrat', 'Inter', sans-serif;
}

.home-hero-image {
  object-position: center 40%;
}

.home-overlay {
  background: linear-gradient(
    180deg,
    rgba(10, 22, 40, 0.82) 0%,
    rgba(10, 22, 40, 0.35) 38%,
    rgba(10, 22, 40, 0.55) 62%,
    rgba(10, 22, 40, 0.88) 100%
  );
}

.home-vignette {
  background: radial-gradient(
    ellipse at center,
    transparent 40%,
    rgba(10, 22, 40, 0.45) 100%
  );
}

.home-header {
  position: relative;
}

.home-icon-ring {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 5rem;
  height: 5rem;
  border-radius: 9999px;
  border: 1.5px solid rgba(201, 168, 76, 0.45);
  background: rgba(10, 22, 40, 0.55);
  backdrop-filter: blur(4px);
  box-shadow: 0 0 24px rgba(201, 168, 76, 0.12);
}

@media (min-width: 768px) {
  .home-icon-ring {
    width: 5.5rem;
    height: 5.5rem;
  }

  .home-panel {
    min-height: 400px;
  }
}

@media (max-width: 767px) {
  .home-header {
    background: linear-gradient(180deg, #0a1628 0%, #0d1a30 100%);
  }

  .home-panel {
    background: #0a1628;
  }

  .home-panel + .home-panel {
    border-top: 1px solid rgba(201, 168, 76, 0.25);
  }

  .home-panel-visual {
    border-bottom: 1px solid rgba(201, 168, 76, 0.12);
    background: linear-gradient(180deg, #0a1628 0%, #0d1a30 100%);
    padding: 0.25rem 0;
  }

  .home-panel-body {
    background: linear-gradient(180deg, #0a1628 0%, #081220 100%);
  }
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
  background: linear-gradient(180deg, transparent, #c9a84c 15%, #e8cc72 50%, #c9a84c 85%, transparent);
  transform: translateX(-50%) rotate(12deg);
  transform-origin: center;
  opacity: 0.75;
  box-shadow: 0 0 16px rgba(201, 168, 76, 0.5);
}

@media (max-width: 767px) {
  .home-btn {
    min-width: 200px;
    width: 100%;
    max-width: 280px;
  }
}
</style>
