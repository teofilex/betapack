import { ref } from 'vue'
import { STORES } from '@/config/stores'

export function useAdminStore() {
    const activeStore = ref('steel')

    const setStore = (storeId) => {
        activeStore.value = storeId
    }

    const storeTabs = [
        { id: 'steel', label: STORES.steel.label },
        { id: 'ambalaza', label: STORES.ambalaza.label },
    ]

    return { activeStore, setStore, storeTabs }
}
