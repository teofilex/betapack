<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

import CategoryManager from '../components/CategoryManager.vue'
import ProductManager from '../components/ProductManager.vue'
import OrdersManager from '../components/OrdersManager.vue'
import ContactMessagesManager from '../components/ContactMessagesManager.vue'

import { useAdminNav } from '../composables/useAdminNav'
import { useAdminStatsStore } from '../store/adminStats'

const router = useRouter()
const authStore = useAuthStore()

const { activeView, setView, views } = useAdminNav()
const statsStore = useAdminStatsStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/admin/login')
}

const goToHomePage = () => {
  router.push('/')
}

onMounted(() => {
  statsStore.refresh()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">

    <!-- Header -->
    <header class="bg-white px-8 py-6 shadow-lg border-b border-gray-200 flex justify-between items-center sticky top-0 z-[100] backdrop-blur-sm bg-white/95">
      <div class="flex items-center gap-4">
        <div class="bg-[#1976d2] text-white rounded-xl px-4 py-2 shadow-lg">
          <span class="text-2xl font-bold">⚙️</span>
        </div>
        <div>
          <h1 class="text-xl font-bold text-gray-900">Beta Pack</h1>
          <p class="text-xs text-gray-500 font-medium">Admin Panel</p>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <button
          @click="goToHomePage"
          class="px-4 py-2.5 border-2 border-[#1976d2] text-[#1976d2] hover:bg-[#1976d2] hover:text-white rounded-xl font-semibold transition-all duration-300 cursor-pointer flex items-center gap-2"
        >
          <span>🏠</span>
          <span class="hidden sm:inline">Glavna stranica</span>
        </button>
        <div class="flex items-center gap-3 bg-gray-50 px-4 py-2 rounded-xl border border-gray-200">
          <div class="w-10 h-10 bg-[#1976d2] rounded-full flex items-center justify-center text-white font-bold shadow-md">
            {{ authStore.user?.username?.charAt(0).toUpperCase() }}
          </div>
          <span class="font-semibold text-gray-800">{{ authStore.user?.username }}</span>
        </div>
        <button
          @click="handleLogout"
          class="px-6 py-2.5 border-2 border-red-500 text-red-600 hover:bg-red-500 hover:text-white rounded-xl font-semibold transition-all duration-300 cursor-pointer flex items-center gap-2"
        >
          <span>🚪</span>
          <span>Logout</span>
        </button>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden flex-col md:flex-row md:-mt-0">

      <!-- Sidebar -->
      <aside class="w-full md:w-[300px] bg-white border-r-2 border-gray-200 overflow-y-auto md:fixed md:top-[88px] md:left-0 md:h-[calc(100vh-88px)] shadow-lg z-40">
        <nav class="p-6 pt-8">

          <h3 class="text-xs uppercase text-gray-500 font-bold mb-4 ml-2 tracking-wider">
            📋 Katalog
          </h3>

          <!-- Dinamička navigacija -->
          <div class="space-y-2">
            <button
              v-for="v in views"
              :key="v.id"
              @click="setView(v.id)"
              :class="activeView === v.id
                ? 'bg-[#1976d2] text-white shadow-lg scale-[1.02]'
                : 'bg-transparent text-gray-700 hover:bg-gray-50 hover:text-gray-900'"
              class="w-full flex items-center gap-3 px-5 py-4 rounded-xl cursor-pointer transition-all duration-300 font-semibold border-2"
              :style="activeView === v.id ? { borderColor: 'transparent' } : { borderColor: '#e5e7eb' }"
            >
              <span class="text-2xl">{{ v.icon }}</span>
              <span class="flex-1 text-left">{{ v.label }}</span>

              <span
                class="px-3 py-1 rounded-full text-sm font-bold min-w-[32px] text-center"
                :class="activeView === v.id ? 'bg-white/30 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{
                  v.id === 'categories' ? statsStore.categories :
                  v.id === 'subcategories' ? statsStore.subcategories :
                  v.id === 'orders' ? statsStore.orders :

                  statsStore.products
                }}
              </span>
            </button>
          </div>

          <!-- Statistika -->
          <div class="mt-8 bg-[#1976d2] p-6 rounded-2xl text-white shadow-xl border-2 border-[#1976d2]/30">
            <h4 class="text-sm font-bold uppercase mb-4 opacity-90 tracking-wider">📊 Statistika</h4>
            <div class="space-y-4">
              <div class="flex justify-between items-center bg-white/10 rounded-xl p-3 backdrop-blur-sm">
                <div class="flex items-center gap-2">
                  <span class="text-xl">📦</span>
                  <span class="text-sm font-semibold opacity-90">Proizvoda</span>
                </div>
                <span class="text-2xl font-bold">{{ statsStore.products }}</span>
              </div>

              <div class="flex justify-between items-center bg-white/10 rounded-xl p-3 backdrop-blur-sm">
                <div class="flex items-center gap-2">
                  <span class="text-xl">📁</span>
                  <span class="text-sm font-semibold opacity-90">Kategorija</span>
                </div>
                <span class="text-2xl font-bold">{{ statsStore.categories }}</span>
              </div>

              <div class="flex justify-between items-center bg-white/10 rounded-xl p-3 backdrop-blur-sm">
                <div class="flex items-center gap-2">
                  <span class="text-xl">📋</span>
                  <span class="text-sm font-semibold opacity-90">Narudžbina</span>
                </div>
                <span class="text-2xl font-bold">{{ statsStore.orders }}</span>
              </div>
            </div>
          </div>

        </nav>
      </aside>
        
      <!-- Main content -->
      <main class="flex-1 overflow-y-auto max-w-[1600px] mx-auto md:ml-[300px]" :class="activeView === 'orders' ? 'p-8 pt-0' : 'p-8'">

        <CategoryManager
          v-if="activeView === 'categories'"
          @update-count="statsStore.refresh"
        />

        <ProductManager
          v-if="activeView === 'products'"
          @update-count="statsStore.refresh"
        />

        <OrdersManager
          v-if="activeView === 'orders'"
          @update-count="statsStore.refresh"
        />

        <ContactMessagesManager
          v-if="activeView === 'contact'"
          @update-count="statsStore.refresh"
        />

      </main>
    </div>
  </div>
</template>
