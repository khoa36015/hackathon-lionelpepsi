<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { chosenOption, setChosenOption, ensureData } from '$lib/stores/ChosenOption';
  import { get } from 'svelte/store';
  import { browser } from '$app/environment';
  import Anh from '$lib/components/Anh.svelte';
  import Vat from '$lib/components/Vat.svelte';

  let currentOption = 'anh'; // Default to 'anh'
  let isTransitioning = false;

  // Initialize from store
  onMount(() => {
    if (!browser) return;
    const stored = get(chosenOption);
    if (stored) {
      currentOption = stored;
    } else {
      // Set default
      setChosenOption('anh');
      ensureData('anh');
    }
  });

  async function switchOption(option) {
    if (option === currentOption || isTransitioning) return;

    isTransitioning = true;
    setChosenOption(option);
    await ensureData(option);

    // Smooth transition
    setTimeout(() => {
      currentOption = option;
      isTransitioning = false;
    }, 300);
  }

  // Reactive statement to sync with store
  $: if (browser && $chosenOption && $chosenOption !== currentOption && !isTransitioning) {
    currentOption = $chosenOption;
  }
</script>

<!-- Hero Section -->
<section class="relative h-[500px] overflow-hidden bg-gradient-to-br from-[#1a1a1a] via-[#2a2a2a] to-[#3a3a3a]">
  <!-- Background Image (placeholder - you'll add URL later) -->
  <div class="absolute inset-0 bg-cover bg-center opacity-30" style="background-image: url('https://placeholder-url.com/hero-image.jpg');"></div>

  <!-- Overlay -->
  <div class="absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-[#2a2a2a]"></div>

  <!-- Content -->
  <div class="relative z-10 flex h-full flex-col items-center justify-center px-4 text-center">
    <h1 class="mb-4 text-5xl font-bold text-white animate-fadeIn md:text-6xl lg:text-7xl" style="text-shadow: 2px 2px 8px rgba(0,0,0,0.5);">
      Bảo tàng vì Hoà bình
    </h1>
    <p class="mb-8 max-w-2xl text-lg text-gray-200 animate-slideInUp md:text-xl" style="animation-delay: 0.2s; text-shadow: 1px 1px 4px rgba(0,0,0,0.5);">
      Cùng Bảo tàng Chứng tích Chiến Tranh lan tỏa khát vọng hòa bình
    </p>

    <!-- Option Toggle -->
    <div class="flex gap-4 animate-scaleIn" style="animation-delay: 0.4s;">
      <button
        on:click={() => switchOption('anh')}
        class="group relative px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 {currentOption === 'anh' ? 'bg-[#c4a574] text-[#1a1a1a] shadow-lg' : 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm'}"
        disabled={isTransitioning}
      >
        <span class="flex items-center gap-2">
          🖼️ Ảnh
        </span>
        {#if currentOption === 'anh'}
          <div class="absolute -bottom-1 left-1/2 h-1 w-3/4 -translate-x-1/2 rounded-full bg-[#c4a574] animate-smoothPulse"></div>
        {/if}
      </button>

      <button
        on:click={() => switchOption('vat')}
        class="group relative px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 {currentOption === 'vat' ? 'bg-[#c4a574] text-[#1a1a1a] shadow-lg' : 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm'}"
        disabled={isTransitioning}
      >
        <span class="flex items-center gap-2">
          📦 Vật
        </span>
        {#if currentOption === 'vat'}
          <div class="absolute -bottom-1 left-1/2 h-1 w-3/4 -translate-x-1/2 rounded-full bg-[#c4a574] animate-smoothPulse"></div>
        {/if}
      </button>
    </div>
  </div>

  <!-- Bottom fade to content -->
  <div class="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#2a2a2a] to-transparent"></div>
</section>

<!-- Content Section with matching background -->
<div class="min-h-screen bg-[#2a2a2a]">
  {#key currentOption}
    <div
      in:fly={{ y: 50, duration: 500, easing: cubicOut, delay: 100 }}
      out:fade={{ duration: 300 }}
      class="animate-fadeIn"
    >
      {#if currentOption === 'anh'}
        <Anh />
      {:else if currentOption === 'vat'}
        <Vat />
      {/if}
    </div>
  {/key}
</div>