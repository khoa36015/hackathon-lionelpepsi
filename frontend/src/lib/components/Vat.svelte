<script>
  import { onMount } from 'svelte';
  import { getOptionData } from '$lib/dataProvider';
  import { notifyAI } from '$lib/api';

  let items = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      loading = true;
      const data = await getOptionData('vat');
      items = Array.isArray(data) ? data : (data?.items || data?.data || data) || [];
    } catch (e) {
      error = 'Không tải được dữ liệu Vật';
    } finally {
      loading = false;
    }
  });

  function clickItem(item) {
    notifyAI({ name: item.ten});
  }
</script>

{#if loading}
  <div class="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
    {#each Array(6) as _}
      <div class="h-44 rounded-xl bg-gray-100 animate-pulse"></div>
    {/each}
  </div>
{:else if error}
  <div class="text-red-600">{error}</div>
{:else}
  <div class="grid gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
    {#each items as item}
      <article class="group rounded-2xl border overflow-hidden bg-white hover:shadow-lg transition">
        <button class="block w-full text-left" on:click={() => clickItem(item)}>
          {#if Array.isArray(item.hinh_anh)}
            <img src={item.hinh_anh[0]} alt={item.ten} class="w-full h-44 object-cover" loading="lazy" />
          {:else}
            <img src={item.hinh_anh} alt={item.ten} class="w-full h-44 object-cover" loading="lazy" />
          {/if}
          <div class="p-4">
            <h4 class="font-bold text-base">{item.ten}</h4>
            <p class="text-sm text-gray-600 mt-1 line-clamp-3">{item.mo_ta}</p>
          </div>
        </button>
      </article>
    {/each}
  </div>
{/if}
