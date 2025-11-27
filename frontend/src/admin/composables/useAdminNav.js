import { ref } from 'vue'

export function useAdminNav() {
    const activeView = ref('products')

    const setView = (view) => {
        activeView.value = view
    }

    const views = [
        { id: 'categories', label: 'Kategorije', icon: '📁' },
        { id: 'products', label: 'Proizvodi', icon: '📦' },
        { id: 'orders', label: 'Narudžbine', icon: '🛒' },
        { id: 'contact', label: 'Kontakt poruke', icon: '✉️' }
    ]

    return { activeView, setView, views }
}
