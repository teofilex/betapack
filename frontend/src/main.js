import '../assets/style.css'
import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';
import 'primeicons/primeicons.css';
import ConfirmationService from 'primevue/confirmationservice'
import ToastService from 'primevue/toastservice'
import { createHead } from '@unhead/vue/client'

const app = createApp(App)
const head = createHead()

app.use(head)
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
});
app.use(createPinia())
app.use(router)
app.mount('#app')
