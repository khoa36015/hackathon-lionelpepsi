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

<!-- Hero Section with Video Background -->
<section class="relative h-[600px] overflow-hidden bg-[#0a0a0a]">
  <!-- Video Background -->
  <video
    autoplay
    muted
    loop
    playsinline
    class="absolute inset-0 w-full h-full object-cover"
  >
    <source src="/source.mp4" type="video/mp4" />
  </video>

  <!-- Dark Overlay for better text readability -->
  <div class="absolute inset-0 bg-gradient-to-b from-black/70 via-black/60 to-[#1a1a1a]"></div>

  <!-- Content -->
  <div class="relative z-10 flex h-full flex-col items-center justify-center px-4 text-center">
    <h1 class="mb-4 text-5xl font-bold text-white animate-fadeIn md:text-6xl lg:text-7xl" style="text-shadow: 3px 3px 12px rgba(0,0,0,0.8);">
      Bảo tàng vì Hoà bình
    </h1>
    <p class="mb-8 max-w-2xl text-lg text-gray-100 animate-slideInUp md:text-xl" style="animation-delay: 0.2s; text-shadow: 2px 2px 8px rgba(0,0,0,0.8);">
      Cùng Bảo tàng Chứng tích Chiến Tranh lan tỏa khát vọng hòa bình
    </p>

    <!-- Option Toggle with War Theme Colors -->
    <div class="flex gap-4 animate-scaleIn" style="animation-delay: 0.4s;">
      <button
        on:click={() => switchOption('anh')}
        class="group relative px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 {currentOption === 'anh' ? 'bg-gradient-to-r from-[#8b4513] to-[#654321] text-white shadow-2xl border-2 border-[#8b4513]' : 'bg-black/40 text-gray-300 hover:bg-black/60 backdrop-blur-md border-2 border-gray-600 hover:border-[#8b4513]'}"
        disabled={isTransitioning}
      >
        <span class="flex items-center gap-2">
          🖼️ Ảnh Lịch Sử
        </span>
        {#if currentOption === 'anh'}
          <div class="absolute -bottom-1 left-1/2 h-1 w-3/4 -translate-x-1/2 rounded-full bg-[#8b4513] animate-smoothPulse shadow-lg"></div>
        {/if}
      </button>

      <button
        on:click={() => switchOption('vat')}
        class="group relative px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-300 transform hover:scale-105 {currentOption === 'vat' ? 'bg-gradient-to-r from-[#556b2f] to-[#3d4f1f] text-white shadow-2xl border-2 border-[#556b2f]' : 'bg-black/40 text-gray-300 hover:bg-black/60 backdrop-blur-md border-2 border-gray-600 hover:border-[#556b2f]'}"
        disabled={isTransitioning}
      >
        <span class="flex items-center gap-2">
          📦 Di Vật Chiến Tranh
        </span>
        {#if currentOption === 'vat'}
          <div class="absolute -bottom-1 left-1/2 h-1 w-3/4 -translate-x-1/2 rounded-full bg-[#556b2f] animate-smoothPulse shadow-lg"></div>
        {/if}
      </button>
    </div>
  </div>

  <!-- Bottom fade to content -->
  <div class="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#1a1a1a] to-transparent"></div>
</section>

<!-- Content Section with darker background -->
<div class="min-h-screen bg-[#1a1a1a]">
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