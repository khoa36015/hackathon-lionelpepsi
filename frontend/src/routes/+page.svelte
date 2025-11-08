<script>
  import { onMount } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { chosenOption, setChosenOption, ensureData } from '$lib/stores/ChosenOption';
  import { get } from 'svelte/store';
  import { browser } from '$app/environment';
  import Anh from '$lib/components/Anh.svelte';
  import Vat from '$lib/components/Vat.svelte';

  export let show = false;           // parent điều khiển
  export let onClose = () => {};     // callback khi đóng

  let dialogEl;
  let lastFocused;

  function close() {
    show = false;
    onClose();
    if (browser && lastFocused) lastFocused.focus();
  }

  async function choose(option) {
    setChosenOption(option);          // 'anh' | 'vat'
    await ensureData(option);         // fetch nếu cần + cache
    close();
  }

  function keydown(e) {
    if (e.key === 'Escape') close();
  }

  onMount(() => {
    if (!browser) return;
    const current = get(chosenOption);
    // nếu chưa chọn option => ép show modal
    if (!current) show = true;

    const handleFocus = () => {
      if (show) {
        // trap focus đơn giản
        const focusables = dialogEl?.querySelectorAll('button,[href],[tabindex]:not([tabindex="-1"])');
        if (focusables && focusables.length) focusables[0].focus();
      }
    };

    if (show) {
      lastFocused = document.activeElement;
      setTimeout(handleFocus, 0);
    }
  });
</script>

{#if show}
  <div
    class="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm"
    on:keydown={keydown}
    transition:fade={{ duration: 150 }}
    role="presentation"
    aria-hidden="false"
  >
    <div
      bind:this={dialogEl}
      role="dialog"
      aria-modal="true"
      aria-label="Chọn loại dữ liệu"
      class="mx-4 w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-zinc-900"
      transition:scale={{ duration: 180 }}
    >
      <div class="mb-4 flex items-start justify-between">
        <h2 class="text-lg font-semibold">Chọn nguồn dữ liệu</h2>
        <button
          class="rounded-full p-2 hover:bg-black/5 dark:hover:bg-white/5"
          aria-label="Đóng"
          on:click={close}
        >
          ✕
        </button>
      </div>

      <p class="mb-5 text-sm text-zinc-600 dark:text-zinc-400">
        Vui lòng chọn 1 trong 2 tùy chọn bên dưới. Tuỳ chọn sẽ được lưu để không phải chọn lại và dữ liệu được cache 2 giờ.
      </p>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          class="group rounded-xl border border-zinc-200 p-4 text-left shadow-sm transition hover:shadow-md active:scale-[.98] dark:border-zinc-800"
          on:click={() => {choose('anh'), close()}}
        >
          <div class="mb-2 text-xl">🖼️</div>
          <div class="font-medium">Ảnh</div>
          <div class="text-xs text-zinc-500 group-hover:text-zinc-600 dark:text-zinc-400">
            Gọi Anh() từ backend
          </div>
        </button>

        <button
          class="group rounded-xl border border-zinc-200 p-4 text-left shadow-sm transition hover:shadow-md active:scale-[.98] dark:border-zinc-800"
          on:click={() => {choose('vat'), close()}}
        >
          <div class="mb-2 text-xl">📦</div>
          <div class="font-medium">Vật</div>
          <div class="text-xs text-zinc-500 group-hover:text-zinc-600 dark:text-zinc-400">
            Gọi Vat() từ backend
          </div>
        </button>
      </div>

    </div>
  </div>
{/if}

{#if $chosenOption === 'anh'}
  <Anh />
{:else}
  <Vat />
{/if}