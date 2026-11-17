<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { useHead } from '@unhead/vue'

const route = useRoute()

// Admin deo sajta ne sme u pretragu
const isAdminRoute = computed(() => route.path.startsWith('/admin'))

useHead(() => ({
  // Isto kao u index.html. Unhead bi inace pri prerenderu upisao svoje podrazumevane
  // vrednosti (lang="en", viewport bez ".0").
  htmlAttrs: { lang: 'sr' },
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1.0' },
    ...(isAdminRoute.value ? [{ name: 'robots', content: 'noindex, nofollow' }] : [])
  ]
}))
</script>

<template>
  <RouterView />
</template>
