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
        preset: Aura
    }
});
app.use(createPinia())
app.use(router)
app.mount('#app')
