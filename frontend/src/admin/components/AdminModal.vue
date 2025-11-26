<script setup>
const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  maxWidth: {
    type: String,
    default: 'max-w-[650px]'
  },
  zIndex: {
    type: String,
    default: 'z-[1000]'
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}
</script>

<template>
  <div
    v-if="show"
    @click.self="close"
    :class="[zIndex, 'animate-fade-in']"
    class="fixed inset-0 bg-black/40 backdrop-blur-sm flex justify-center items-center p-4"
  >
    <div
      :class="maxWidth"
      class="bg-white rounded-3xl w-full max-h-[90vh] shadow-2xl overflow-hidden animate-slide-up"
    >
      <!-- HEADER -->
      <div class="px-10 py-7 bg-gradient-to-r from-blue-600 to-blue-500 flex justify-between items-center">
        <h3 class="text-2xl font-semibold text-white">
          {{ title }}
        </h3>

        <button
          @click="close"
          class="text-white text-4xl leading-none hover:scale-125 transition cursor-pointer"
        >
          &times;
        </button>
      </div>

      <!-- CONTENT -->
      <div class="px-10 py-8 max-h-[calc(90vh-140px)] overflow-y-auto">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
@layer utilities {
  .animate-fade-in {
    animation: fadeIn 0.25s ease-out;
  }
  .animate-slide-up {
    animation: slideUp 0.3s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0 }
    to   { opacity: 1 }
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(25px); }
    to   { opacity: 1; transform: translateY(0); }
  }
}
</style>

