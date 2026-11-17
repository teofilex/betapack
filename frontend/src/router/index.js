import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/store/auth";
// Pocetna, prodavnica i strana proizvoda su ulazne strane (pretraga vodi pravo na njih),
// pa ostaju u glavnom fajlu: lazy ucitavanje bi im dodalo jos jedan krug ka serveru.
// Sve ostalo se ucitava tek kad zatreba. Admin (Chart.js, vuedraggable, PrimeVue
// komponente) je najveci deo koda, a posetioci ga nikad ne otvaraju.
import HomeView from "@/pages/user/HomeView.vue";
import ShopView from "@/pages/user/ShopView.vue";
import ProductDetailView from "@/pages/user/ProductDetailView.vue";
import NotFoundView from "@/pages/user/NotFoundView.vue";

const CartView = () => import("@/pages/user/CartView.vue");
const CheckoutView = () => import("@/pages/user/CheckoutView.vue");
const OrderSuccessView = () => import("@/pages/user/OrderSuccessView.vue");
const ContactView = () => import("@/pages/user/ContactView.vue");
const AboutView = () => import("@/pages/user/AboutView.vue");
const Login = () => import("../admin/pages/Login.vue");
const AdminView = () => import("../admin/pages/AdminView.vue");

// Pri povratku (Nazad) strana je cesto jos kratka jer se proizvodi ucitavaju sa API-ja:
// sacekaj (najvise ~1,5 s) da dovoljno poraste, pa tek onda skoci na sacuvanu poziciju.
const whenPageIsTallEnough = (position) =>
    new Promise((resolve) => {
        const deadline = performance.now() + 1500
        const check = () => {
            const needed = (position.top || 0) + window.innerHeight
            if (document.documentElement.scrollHeight >= needed || performance.now() > deadline) {
                resolve(position)
            } else {
                requestAnimationFrame(check)
            }
        }
        check()
    })

const storeChildRoutes = (store) => [
    {
        path: '',
        name: `${store}-shop`,
        component: ShopView,
        meta: { store }
    },
    {
        path: 'proizvod/:slugOrId',
        name: `${store}-product-detail`,
        component: ProductDetailView,
        meta: { store }
    },
    {
        path: 'cart',
        name: `${store}-cart`,
        component: CartView,
        meta: { store }
    },
    {
        path: 'checkout',
        name: `${store}-checkout`,
        component: CheckoutView,
        meta: { store }
    },
    {
        path: 'order-success/:orderId',
        name: `${store}-order-success`,
        component: OrderSuccessView,
        meta: { store }
    },
    {
        path: 'kontakt',
        name: `${store}-contact`,
        component: ContactView,
        meta: { store }
    },
    {
        path: 'o-nama',
        name: `${store}-about`,
        component: AboutView,
        meta: { store }
    },
]

const router = createRouter({
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/steel',
            children: storeChildRoutes('steel')
        },
        {
            path: '/ambalaza',
            children: storeChildRoutes('ambalaza')
        },
        // Legacy redirects
        { path: '/proizvod/:slugOrId', redirect: to => `/steel/proizvod/${to.params.slugOrId}` },
        { path: '/cart', redirect: '/steel/cart' },
        { path: '/checkout', redirect: '/steel/checkout' },
        { path: '/order-success/:orderId', redirect: to => `/steel/order-success/${to.params.orderId}` },
        { path: '/kontakt', redirect: '/steel/kontakt' },
        { path: '/o-nama', redirect: '/steel/o-nama' },
        {
            path: '/admin',
            redirect: '/admin/login'
        },
        {
            path: '/admin/login',
            name: 'admin-login',
            component: Login
        },
        {
            path: '/admin/panel',
            name: 'admin-panel',
            component: AdminView,
            meta: { requiresAuth: true }
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'not-found',
            component: NotFoundView
        }
    ],
    history: createWebHistory(import.meta.env.BASE_URL),
    scrollBehavior(to, from, savedPosition) {
        // Nazad/Napred: vrati sacuvanu poziciju (kad se strana napuni podacima i bude dovoljno visoka)
        if (savedPosition) {
            return whenPageIsTallEnough(savedPosition)
        }
        // Link sa #sidrom: na sidro, ispod lepljivog zaglavlja
        if (to.hash) {
            return { el: to.hash, top: 80, behavior: 'smooth' }
        }
        // Ista strana, drugi query (npr. /steel?category=N): ne skroluje; listu proizvoda
        // pri promeni kategorije pomera sam ShopView (scrollToProducts)
        if (to.path === from.path) {
            return false
        }
        // Druga strana: na vrh. Ruter ovo poziva tek kad je navigacija zavrsena, pa kod lazy
        // ruta i posle ucitavanja i iscrtavanja nove strane (stara strana se ne trza ranije)
        return { top: 0, left: 0 }
    }
})

router.beforeEach(async (to, from, next) => {
    // Admin ima svoj paket (PrimeVue tema i ikone) koji se ucitava tek ovde
    if (to.path.startsWith('/admin')) {
        const { installAdminPlugins } = await import('@/admin/setup')
        installAdminPlugins()
    }
    const authStore = useAuthStore()
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/admin/login')
    } else if (to.path === '/admin/login' && authStore.isAuthenticated) {
        next('/admin/panel')
    } else {
        next()
    }
})

export default router
