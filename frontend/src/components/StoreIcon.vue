<script setup>
defineProps({
  storeId: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'md'
  }
})

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-14 h-14 md:w-[4.5rem] md:h-[4.5rem]'
}
</script>

<template>
  <!-- Kovano gvožđe — kovani scroll / ograda -->
  <svg
    v-if="storeId === 'steel'"
    :class="sizeClasses[size] || sizeClasses.md"
    viewBox="0 0 64 64"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path d="M8 48V28c0-6 4-10 10-10h4" />
    <path d="M56 48V28c0-6-4-10-10-10h-4" />
    <path d="M8 28h48" />
    <path d="M32 18v30" />
    <path d="M20 36c4-8 8-12 12-12s8 4 12 12" />
    <path d="M14 42c6-4 12-6 18-6s12 2 18 6" />
    <circle cx="32" cy="14" r="2" fill="currentColor" stroke="none" />
  </svg>

  <!-- Ambalaža — posuda + kesa -->
  <svg
    v-else-if="storeId === 'ambalaza'"
    :class="sizeClasses[size] || sizeClasses.md"
    viewBox="0 0 64 64"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <rect x="10" y="24" width="22" height="16" rx="2" />
    <path d="M14 24v-4a7 7 0 0 1 14 0v4" />
    <path d="M10 32h22" />
    <path d="M38 22h14v24a3 3 0 0 1-3 3H38" />
    <path d="M38 22l-4-6h10l-4 6" />
    <path d="M42 30h6" />
    <path d="M42 36h6" />
  </svg>
</template>
