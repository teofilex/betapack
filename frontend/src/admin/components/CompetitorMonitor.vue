<template>
    <div class="space-y-6">
        <!-- Header -->
        <div class="flex justify-between items-center">
            <div>
                <h2 class="text-2xl font-bold text-gray-900">Konkurencija - Praćenje Cena</h2>
                <p class="text-sm text-gray-500 mt-1">
                    Ukupno proizvoda: {{ filteredProducts.length }}
                </p>
            </div>
            <button
                @click="triggerScraping"
                :disabled="scraping"
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
                <span v-if="scraping" class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                <span>{{ scraping ? 'Scraping u toku...' : '🕷️ Pokreni Scraping' }}</span>
            </button>
        </div>

        <!-- Filters -->
        <div class="bg-white p-4 rounded-lg shadow-sm space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <!-- Site Filter -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Sajt
                    </label>
                    <select v-model="filters.site" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">Svi sajtovi</option>
                        <option v-for="site in activeSites" :key="site.id" :value="site.id">
                            {{ site.name }}
                        </option>
                    </select>
                </div>

                <!-- Category Filter -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Kategorija
                    </label>
                    <select v-model="filters.category" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">Sve kategorije</option>
                        <option v-for="category in categories" :key="category" :value="category">
                            {{ category }}
                        </option>
                    </select>
                </div>

                <!-- Stock Filter -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Status
                    </label>
                    <select v-model="filters.in_stock" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">Svi proizvodi</option>
                        <option value="true">Na stanju</option>
                        <option value="false">Nije na stanju</option>
                    </select>
                </div>

                <!-- On Sale Filter -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Akcija
                    </label>
                    <select v-model="filters.on_sale" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">Svi proizvodi</option>
                        <option value="true">Na akciji</option>
                        <option value="false">Regularna cena</option>
                    </select>
                </div>
            </div>

            <!-- Search -->
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    Pretraga
                </label>
                <input
                    v-model="filters.search"
                    type="text"
                    placeholder="Pretraži po nazivu proizvoda..."
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
            </div>

            <!-- Reset Filters -->
            <div class="flex justify-end">
                <button
                    @click="resetFilters"
                    class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition"
                >
                    Poništi filtere
                </button>
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-2 text-gray-600">Učitavam podatke...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            <p class="font-medium">Greška prilikom učitavanja podataka</p>
            <p class="text-sm mt-1">{{ error }}</p>
        </div>

        <!-- Products Table -->
        <div v-else-if="filteredProducts.length > 0" class="bg-white rounded-lg shadow-sm overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Proizvod
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Sajt
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Kategorija
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Cena
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Poslednji Update
                            </th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Akcije
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="product in filteredProducts" :key="product.id" class="hover:bg-gray-50">
                            <td class="px-6 py-4">
                                <div class="flex items-center">
                                    <img
                                        v-if="product.image_url"
                                        :src="product.image_url"
                                        :alt="product.name"
                                        class="h-10 w-10 rounded object-cover mr-3"
                                    >
                                    <div>
                                        <div class="text-sm font-medium text-gray-900">
                                            {{ product.name }}
                                        </div>
                                        <div v-if="product.description" class="text-xs text-gray-500 max-w-xs truncate">
                                            {{ product.description }}
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-sm text-gray-900">{{ product.site_name }}</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="text-sm text-gray-600">{{ product.category || '-' }}</span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm">
                                    <div class="font-semibold text-gray-900">
                                        {{ formatPrice(product.effective_price) }}
                                    </div>
                                    <div v-if="product.on_sale" class="text-xs">
                                        <span class="line-through text-gray-400">{{ formatPrice(product.original_price) }}</span>
                                        <span class="ml-1 text-red-600 font-medium">-{{ product.discount_percentage }}%</span>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex flex-col gap-1">
                                    <span v-if="product.in_stock" class="inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 px-2 py-1">
                                        Na stanju
                                    </span>
                                    <span v-else class="inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800 px-2 py-1">
                                        Nema na stanju
                                    </span>
                                    <span v-if="product.on_sale" class="inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800 px-2 py-1">
                                        🔥 Akcija
                                    </span>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{ formatDate(product.last_seen_at) }}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <div class="flex justify-end gap-2">
                                    <button
                                        @click="viewPriceHistory(product)"
                                        class="text-purple-600 hover:text-purple-900"
                                    >
                                        📊 Graf
                                    </button>
                                    <a
                                        :href="product.product_url"
                                        target="_blank"
                                        class="text-blue-600 hover:text-blue-900"
                                    >
                                        Pogledaj
                                    </a>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Empty State -->
        <div v-else class="bg-white rounded-lg shadow-sm p-12 text-center">
            <div class="text-gray-400 text-6xl mb-4">🔍</div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Nema pronađenih proizvoda</h3>
            <p class="text-gray-500">Promenite filtere ili pokrenite scraping da biste videli podatke.</p>
        </div>

        <!-- Price History Modal -->
        <div
            v-if="showPriceHistoryModal"
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            @click.self="closePriceHistoryModal"
        >
            <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <!-- Modal Header -->
                <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-900">Istorija Cena</h3>
                        <p class="text-sm text-gray-600 mt-1">{{ selectedProduct?.name }}</p>
                    </div>
                    <button
                        @click="closePriceHistoryModal"
                        class="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                    >
                        &times;
                    </button>
                </div>

                <!-- Modal Body -->
                <div class="p-6">
                    <!-- Loading State -->
                    <div v-if="loadingHistory" class="text-center py-12">
                        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        <p class="mt-2 text-gray-600">Učitavam istoriju cena...</p>
                    </div>

                    <!-- Chart -->
                    <div v-else-if="priceHistory.length > 0" class="space-y-6">
                        <div class="bg-gray-50 p-4 rounded-lg">
                            <Line :data="chartData" :options="chartOptions" />
                        </div>

                        <!-- Stats -->
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-blue-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-600">Trenutna Cena</div>
                                <div class="text-2xl font-bold text-blue-600">
                                    {{ formatPrice(priceHistory[0]?.price) }}
                                </div>
                            </div>
                            <div class="bg-green-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-600">Najniža Cena</div>
                                <div class="text-2xl font-bold text-green-600">
                                    {{ formatPrice(Math.min(...priceHistory.map(h => h.price))) }}
                                </div>
                            </div>
                            <div class="bg-red-50 p-4 rounded-lg">
                                <div class="text-sm text-gray-600">Najviša Cena</div>
                                <div class="text-2xl font-bold text-red-600">
                                    {{ formatPrice(Math.max(...priceHistory.map(h => h.price))) }}
                                </div>
                            </div>
                        </div>

                        <!-- History Table -->
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Datum</th>
                                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Cena</th>
                                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    <tr v-for="(record, index) in priceHistory" :key="index">
                                        <td class="px-4 py-2 text-sm text-gray-900">
                                            {{ formatDate(record.recorded_at) }}
                                        </td>
                                        <td class="px-4 py-2 text-sm">
                                            <span class="font-semibold">{{ formatPrice(record.price) }}</span>
                                            <span v-if="record.on_sale" class="ml-2 text-xs text-red-600">🔥 Akcija</span>
                                        </td>
                                        <td class="px-4 py-2 text-sm">
                                            <span v-if="record.in_stock" class="text-green-600">✓ Na stanju</span>
                                            <span v-else class="text-red-600">✗ Nije na stanju</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- No Data State -->
                    <div v-else class="text-center py-12">
                        <div class="text-gray-400 text-4xl mb-4">📊</div>
                        <p class="text-gray-600">Nema dostupne istorije cena za ovaj proizvod.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import { Line } from 'vue-chartjs'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
)

// Data
const products = ref([])
const sites = ref([])
const loading = ref(true)
const error = ref(null)
const scraping = ref(false)

// Price History Modal
const showPriceHistoryModal = ref(false)
const selectedProduct = ref(null)
const priceHistory = ref([])
const loadingHistory = ref(false)

const filters = ref({
    site: '',
    category: '',
    in_stock: '',
    on_sale: '',
    search: ''
})

// Computed
const activeSites = computed(() => {
    return sites.value.filter(site => site.is_active)
})

const categories = computed(() => {
    const cats = products.value.map(p => p.category).filter(Boolean)
    return [...new Set(cats)].sort()
})

const filteredProducts = computed(() => {
    let filtered = products.value

    // Filter by site
    if (filters.value.site) {
        filtered = filtered.filter(p => p.site === parseInt(filters.value.site))
    }

    // Filter by category
    if (filters.value.category) {
        filtered = filtered.filter(p => p.category === filters.value.category)
    }

    // Filter by stock
    if (filters.value.in_stock !== '') {
        filtered = filtered.filter(p => p.in_stock === (filters.value.in_stock === 'true'))
    }

    // Filter by sale
    if (filters.value.on_sale !== '') {
        filtered = filtered.filter(p => p.on_sale === (filters.value.on_sale === 'true'))
    }

    // Filter by search
    if (filters.value.search) {
        const search = filters.value.search.toLowerCase()
        filtered = filtered.filter(p =>
            p.name.toLowerCase().includes(search) ||
            (p.description && p.description.toLowerCase().includes(search))
        )
    }

    return filtered
})

// Chart Data
const chartData = computed(() => {
    if (!priceHistory.value || priceHistory.value.length === 0) {
        return {
            labels: [],
            datasets: []
        }
    }

    // Reverse to show oldest first
    const history = [...priceHistory.value].reverse()

    return {
        labels: history.map(h => {
            const date = new Date(h.recorded_at)
            return date.toLocaleDateString('sr-RS', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
        }),
        datasets: [
            {
                label: 'Cena (RSD)',
                data: history.map(h => h.price),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.3,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: history.map(h => h.on_sale ? 'rgb(239, 68, 68)' : 'rgb(59, 130, 246)'),
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }
        ]
    }
})

const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
        legend: {
            display: false
        },
        title: {
            display: true,
            text: 'Kretanje Cene',
            font: {
                size: 16,
                weight: 'bold'
            }
        },
        tooltip: {
            callbacks: {
                label: (context) => {
                    const value = context.parsed.y
                    return `Cena: ${formatPrice(value)}`
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: false,
            ticks: {
                callback: (value) => {
                    return new Intl.NumberFormat('sr-RS', {
                        style: 'currency',
                        currency: 'RSD',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    }).format(value)
                }
            }
        }
    }
}

// Methods
const fetchData = async () => {
    loading.value = true
    error.value = null

    try {
        const [productsRes, sitesRes] = await Promise.all([
            api.get('/scraped-products/'),
            api.get('/competitor-sites/')
        ])

        // DRF vraća paginiran response sa 'results' ili direktno array
        products.value = Array.isArray(productsRes.data) ? productsRes.data : (productsRes.data.results || [])
        sites.value = Array.isArray(sitesRes.data) ? sitesRes.data : (sitesRes.data.results || [])
    } catch (err) {
        error.value = err.response?.data?.detail || 'Greška prilikom učitavanja podataka'
        console.error('Error fetching competitor data:', err)
    } finally {
        loading.value = false
    }
}

const resetFilters = () => {
    filters.value = {
        site: '',
        category: '',
        in_stock: '',
        on_sale: '',
        search: ''
    }
}

const formatPrice = (price) => {
    if (!price) return '-'
    return new Intl.NumberFormat('sr-RS', {
        style: 'currency',
        currency: 'RSD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(price)
}

const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('sr-RS', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date)
}

const triggerScraping = async () => {
    if (scraping.value) return

    scraping.value = true

    try {
        const response = await api.post('/competitor-sites/trigger_scraping/')

        alert(response.data.message)

        // Čekaj 15 sekundi pa osvježi podatke
        setTimeout(async () => {
            await fetchData()
            scraping.value = false
        }, 15000)

    } catch (err) {
        console.error('Error triggering scraping:', err)
        alert('Greška prilikom pokretanja scrapinga: ' + (err.response?.data?.detail || err.message))
        scraping.value = false
    }
}

const viewPriceHistory = async (product) => {
    selectedProduct.value = product
    showPriceHistoryModal.value = true
    loadingHistory.value = true
    priceHistory.value = []

    try {
        const response = await api.get(`/scraped-products/${product.id}/price_history/`)
        priceHistory.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
    } catch (err) {
        console.error('Error fetching price history:', err)
        alert('Greška prilikom učitavanja istorije cena: ' + (err.response?.data?.detail || err.message))
    } finally {
        loadingHistory.value = false
    }
}

const closePriceHistoryModal = () => {
    showPriceHistoryModal.value = false
    selectedProduct.value = null
    priceHistory.value = []
}

// Lifecycle
onMounted(() => {
    fetchData()
})
</script>
