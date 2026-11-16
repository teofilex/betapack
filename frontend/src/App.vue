<script setup>
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { useHead } from '@unhead/vue'

const route = useRoute()

// Admin deo sajta ne sme u pretragu
const isAdminRoute = computed(() => route.path.startsWith('/admin'))

useHead(() => ({
  meta: isAdminRoute.value ? [{ name: 'robots', content: 'noindex, nofollow' }] : []
}))
</script>

<template>
  <RouterView />
</template>
