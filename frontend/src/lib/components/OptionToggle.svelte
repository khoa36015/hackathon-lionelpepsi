<script>
  import { chosenOption, switchOption, ensureData } from '$lib/stores/ChosenOption.js';
  import { get } from 'svelte/store';

  let loading = false;

  async function toggle() {
    if (loading) return;
    loading = true;
    try {
      if (!get(chosenOption)) {
        await ensureData('anh');
      } else {
        await switchOption();
      }
    } finally {
      loading = false;
    }
  }
</script>

<div class="fixed top-20 right-4 z-50">
  <button
    class="px-3 py-1.5 rounded-full border text-sm bg-white shadow hover:shadow-md active:scale-95 transition"
    on:click={toggle}
    disabled={loading}
  >
    {#if loading}
      Đang tải...
    {:else if $chosenOption === 'anh'}
      🖼️ Ảnh
    {:else if $chosenOption === 'vat'}
      📦 Vật
    {:else}
      Chọn kiểu dữ liệu
    {/if}
  </button>
</div>
