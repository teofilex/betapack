<script setup>
// <picture> za lokalne slike iz public/: WebP izvori (po potrebi samo za odredjenu sirinu
// ekrana) uz JPEG/PNG kao rezervu. class i ostali atributi idu na <img>.
//
// sources: [{ srcset, media?, sizes?, type? }]
// Za sliku koja treba da se skida samo na jednoj sirini ekrana, 'src' je prazan GIF, a
// izvori imaju media uslov: na drugim sirinama pregledac ne skida nista.
defineOptions({ inheritAttrs: false })

defineProps({
  src: { type: String, required: true },
  sources: { type: Array, default: () => [] },
  alt: { type: String, default: '' },
  width: { type: Number, default: undefined },
  height: { type: Number, default: undefined },
  eager: { type: Boolean, default: false },
})
</script>

<template>
  <picture>
    <source
      v-for="(source, index) in sources"
      :key="index"
      :srcset="source.srcset"
      :media="source.media"
      :sizes="source.sizes"
      :type="source.type"
    />
    <img
      v-bind="$attrs"
      :src="src"
      :alt="alt"
      :width="width"
      :height="height"
      :loading="eager ? 'eager' : 'lazy'"
      :fetchpriority="eager ? 'high' : undefined"
      decoding="async"
    />
  </picture>
</template>

<style scoped>
/* <picture> ne pravi sopstveni box: <img> se ponasa kao da je direktno dete roditelja */
picture {
  display: contents;
}

/* bez ovoga <source> unutar 'contents' elementa postaje prazna stavka flex roditelja */
source {
  display: none;
}
</style>
