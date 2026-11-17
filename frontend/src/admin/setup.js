// PrimeVue (preset teme i ikone) koristi samo admin (Login.vue). Javne strane
// ga ne ucitavaju: ovaj modul se uvozi tek kad se otvori /admin ruta (router/index.js).
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import 'primeicons/primeicons.css'
import { app } from '@/app'

let installed = false

export function installAdminPlugins() {
    if (installed) return
    installed = true

    app.use(PrimeVue, {
        theme: {
            preset: Aura,
            options: {
                // Bez ovoga PrimeVue vezuje tamnu temu za sistemsko podesenje korisnika
                // i ubacuje `:root { color-scheme: dark }`. Pozadine u aplikaciji su
                // svetle, pa bi nasledjen tekst (npr. sadrzaj input polja) postao beo
                // na beloj podlozi. Selektor se namerno nikad ne primenjuje.
                darkModeSelector: '.app-dark'
            }
        }
    })
}
