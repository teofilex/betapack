<template>
  <transition name="modal-fade">
    <div
      v-if="show"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[2000]"
      @click.self="$emit('cancel')"
    >
      <div
        class="bg-white rounded-lg shadow-xl w-full max-w-[380px] p-7 
               transform transition-all duration-200 modal-animation"
      >
        <!-- Title -->
        <h2 class="text-base font-bold text-gray-900 text-center mb-5">
          {{ title }}
        </h2>

        <!-- Message -->
        <p class="text-gray-600 text-center mb-7 leading-relaxed text-xs">
          {{ message }}
        </p>

        <!-- Buttons -->
        <div class="flex gap-3 justify-center">
          <button
            @click="$emit('confirm')"
            class="px-5 py-2.5 rounded-lg bg-[#1976d2] text-white font-semibold text-xs
                   shadow hover:bg-[#1565c0] active:scale-95 transition cursor-pointer"
          >
            {{ confirmText }}
          </button>

          <button
            v-if="cancelText"
            @click="$emit('cancel')"
            class="px-5 py-2.5 rounded-lg bg-gray-200 text-gray-800 font-semibold text-xs
                   shadow hover:bg-gray-300 active:scale-95 transition cursor-pointer"
          >
            {{ cancelText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  show: Boolean,
  title: { type: String, default: "Potvrda" },
  message: String,
  confirmText: { type: String, default: "Da" },
  cancelText: { type: String, default: "Odustani" },
})
</script>

<style scoped>
/* Fade za pozadinu */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Scale animacija za modal */
.modal-animation {
  opacity: 1;
  transform: scale(1);
}

.modal-fade-enter-from .modal-animation {
  transform: scale(0.9);
  opacity: 0;
}

.modal-fade-leave-to .modal-animation {
  transform: scale(0.95);
  opacity: 0;
}
</style>
