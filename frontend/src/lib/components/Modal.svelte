<script>
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  export let show = false;
  export let onClose = () => {};
</script>

{#if show}
  <div
    class="fixed inset-0 backdrop-blur-md bg-white/70 bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn"
    transition:fade={{ duration: 300, easing: cubicOut }}
    on:click={onClose}
    role="presentation"
  >
    <div
      class="bg-white rounded-2xl p-6 w-full max-w-md relative shadow-2xl animate-scaleIn"
      transition:scale={{ duration: 300, easing: cubicOut, start: 0.95 }}
      on:click|stopPropagation
      role="dialog"
      aria-modal="true"
    >
      <button
        class="absolute top-3 right-3 text-gray-400 hover:text-gray-600 font-black cursor-pointer w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-all duration-200 hover:rotate-90"
        on:click={onClose}
        aria-label="Close"
      >
        ✕
      </button>
      <slot />
    </div>
  </div>
{/if}