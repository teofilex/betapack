<script setup>
const currentYear = new Date().getFullYear()

const contactInfo = {
  name: 'Beta Pack d.o.o.',
  address: 'Pukovnika Milenka Pavlovića 159 A, Zemun-Batajnica',
  phone1: '065/330 02 42',
  phone2: '063/8757 725',
  email: 'office@betapack.co.rs',
  coordinates: { lat: 44.913252, lng: 20.2595729 }
}
</script>

<template>
  <footer class="bg-gray-900 text-gray-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <!-- O kompaniji -->
        <div>
          <div class="flex items-center gap-2 mb-3">
            <img src="/betapack-logo.png" alt="Beta Pack Logo" class="h-8 w-auto" />
            <h3 class="text-base font-bold text-white">BETA PACK</h3>
          </div>
          <p class="text-xs leading-relaxed">
            Prodaja bravarskih materijala od kovanog gvožđa za proizvodnju ograda, kapija, gelendera i drugih metalnih proizvoda.
            Vaš pouzdan partner za kvalitetne materijale.
          </p>
          <p class="text-xs mt-2 text-gray-400">
            25 godina sa vama
          </p>
        </div>

        <!-- Kontakt -->
        <div>
          <h3 class="text-base font-bold text-white mb-3">Kontakt</h3>
          <div class="space-y-1.5 text-xs">
            <p class="font-semibold">{{ contactInfo.name }}</p>
            <p>{{ contactInfo.address }}</p>

            <div class="pt-1">
              <a
                :href="`tel:${contactInfo.phone1}`"
                class="flex items-center gap-1.5 text-[#42a5f5] hover:text-[#1976d2] transition cursor-pointer"
              >
                <span>📞</span>
                <span>{{ contactInfo.phone1 }}</span>
              </a>
              <a
                :href="`tel:${contactInfo.phone2}`"
                class="flex items-center gap-1.5 text-[#42a5f5] hover:text-[#1976d2] transition cursor-pointer"
              >
                <span>📞</span>
                <span>{{ contactInfo.phone2 }}</span>
              </a>
            </div>

            <a
              :href="`mailto:${contactInfo.email}`"
              class="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 transition cursor-pointer"
            >
              <span>✉️</span>
              <span>{{ contactInfo.email }}</span>
            </a>
          </div>
        </div>

        <!-- Radno vreme -->
        <div>
          <h3 class="text-base font-bold text-white mb-3">Radno vreme</h3>
          <div class="space-y-1.5 text-xs">
            <div class="flex justify-between">
              <span>Ponedeljak - Petak:</span>
              <span class="font-semibold">08:00 - 16:00</span>
            </div>
            <div class="flex justify-between">
              <span>Subota:</span>
              <span class="font-semibold">08:00 - 14:00</span>
            </div>
            <div class="flex justify-between">
              <span>Nedelja:</span>
              <span class="text-red-400">Zatvoreno</span>
            </div>
          </div>

          <div class="mt-4">
            <a
              href="https://www.google.com/maps?q=44.914361,20.258167"
              target="_blank"
              class="inline-flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition text-xs cursor-pointer"
            >
              <span>📍</span>
              <span>Vidi na mapi</span>
            </a>
          </div>
        </div>

      </div>

      <!-- Bottom bar -->
      <div class="border-t border-gray-800 mt-4 pt-3 text-center text-xs">
        <p>&copy; {{ currentYear }} {{ contactInfo.name }}. Sva prava zadržana.</p>
      </div>
    </div>
  </footer>
</template>
