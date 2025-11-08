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
      const data = await getOptionData('anh');
      console.log('Anh data received:', data);
      
      // Handle different response formats from backend
      if (Array.isArray(data)) {
        items = data;
      } else if (data && Array.isArray(data.data)) {
        items = data.data;
      } else if (data && Array.isArray(data.items)) {
        items = data.items;
      } else if (data && Array.isArray(data.provinces)) {
        items = data.provinces;
      } else {
        console.warn('Unexpected data format:', data);
        items = [];
      }
    } catch (e) {
      console.error('Error loading Anh data:', e);
      error = `Không tải được dữ liệu Ảnh: ${e.message}`;
    } finally {
      loading = false;
    }
  });

  function clickItem(item) {
    notifyAI(item.ten);
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
            <h3 class="font-medium text-gray-900 group-hover:text-blue-600 transition">
              {item.ten}
            </h3>
            {#if item.mo_ta}
              <p class="text-sm text-gray-600 mt-1 line-clamp-2">
                {item.mo_ta}
              </p>
            {/if}
          </div>
        </button>
      </article>
    {/each}
  </div>
{/if}