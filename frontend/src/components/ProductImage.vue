<script setup>
// Slika proizvoda: Cloudinary transformacije preko URL-a, srcset/sizes, lazy loading.
// Kontejner oko slike vec ima fiksnu visinu ili aspect-ratio, pa nema pomeranja sadrzaja.
// class i ostali atributi idu na <img>.
import { computed } from 'vue'
import { cloudinaryUrl, cloudinarySrcset } from '@/utils/cloudinary'

const props = defineProps({
  src: { type: String, required: true },
  alt: { type: String, default: '' },
  widths: { type: Array, default: () => [320, 480, 640] },
  sizes: { type: String, default: '50vw' },
  // slika na prvom ekranu (ne lazy, visok prioritet)
  eager: { type: Boolean, default: false },
})

const fallbackSrc = computed(() => cloudinaryUrl(props.src, { width: props.widths[Math.floor(props.widths.length / 2)] }))
const srcset = computed(() => cloudinarySrcset(props.src, props.widths))
</script>

<template>
  <img
    :src="fallbackSrc"
    :srcset="srcset || undefined"
    :sizes="srcset ? sizes : undefined"
    :alt="alt"
    :loading="eager ? 'eager' : 'lazy'"
    :fetchpriority="eager ? 'high' : undefined"
    decoding="async"
  />
</template>
