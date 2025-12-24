import { createRouter, createWebHistory } from "vue-router";
import { nextTick } from "vue";
import Login from "../admin/pages/Login.vue";
import AdminView from "../admin/pages/AdminView.vue";
import ShopView from "@/pages/user/ShopView.vue";
import CartView from "@/pages/user/CartView.vue";
import ProductDetailView from "@/pages/user/ProductDetailView.vue";
import CheckoutView from "@/pages/user/CheckoutView.vue";
import OrderSuccessView from "@/pages/user/OrderSuccessView.vue";
import ContactView from "@/pages/user/ContactView.vue";
import AboutView from "@/pages/user/AboutView.vue";
import NotFoundView from "@/pages/user/NotFoundView.vue";
import { useAuthStore } from "@/store/auth";

const router = createRouter({
    routes: [
        {
            path: '/',
            name: 'shop',
            component: ShopView
        },
        {
            path: '/proizvod/:slugOrId',
            name: 'product-detail',
            component: ProductDetailView
        },
        {
            path: '/cart',
            name: 'cart',
            component: CartView
        },
        {
            path: '/checkout',
            name: 'checkout',
            component: CheckoutView
        },
        {
            path: '/order-success/:orderId',
            name: 'order-success',
            component: OrderSuccessView
        },
        {
            path: '/kontakt',
            name: 'contact',
            component: ContactView
        },
        {
            path: '/o-nama',
            name: 'about',
            component: AboutView
        },
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
        // Ako korisnik koristi back/forward dugme, vrati na prethodnu poziciju
        if (savedPosition) {
            return savedPosition
        }

        // Ako je hash (anchor link), scroll na taj element
        if (to.hash) {
            return {
                el: to.hash,
                behavior: 'smooth',
            }
        }

        // Za sve ostale slučajeve, forsiraj scroll na vrh
        // Koristi window.scrollTo kao fallback za maksimalnu kompatibilnost
        return new Promise((resolve) => {
            setTimeout(() => {
                window.scrollTo(0, 0)
                resolve({ top: 0, left: 0 })
            }, 100) // 100ms delay garantuje da se DOM učitao
        })
    }
})

router.beforeEach((to, from, next) => {
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
