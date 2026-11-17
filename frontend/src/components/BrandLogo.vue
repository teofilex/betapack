<script setup>
// Logo (WebP uz PNG rezervu). class i ostali atributi idu na <img>.
import ResponsivePicture from '@/components/ResponsivePicture.vue'
</script>

<template>
  <ResponsivePicture
    src="/betapack-logo.png"
    :sources="[{ srcset: '/betapack-logo.webp', type: 'image/webp' }]"
    alt="Beta Pack Logo"
    :width="160"
    :height="156"
    eager
  />
</template>
