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
  <div class="container mx-auto px-4 py-8">
    <div class="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
      {#each Array(6) as _}
        <div class="h-80 rounded-3xl bg-linear-to-br from-gray-100 to-gray-50 animate-pulse shadow-soft"></div>
      {/each}
    </div>
  </div>
{:else if error}
  <div class="container mx-auto px-4 py-8">
    <div class="rounded-3xl bg-red-50 border-2 border-red-200 p-6 text-red-700 shadow-soft">
      <p class="font-medium">{error}</p>
    </div>
  </div>
{:else}
  <div class="container mx-auto px-4 py-8">
    <div class="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
      {#each items as item}
        <article class="group relative rounded-3xl overflow-hidden bg-white shadow-soft hover:shadow-fluffy transition-all duration-300 hover:-translate-y-1">
          <button class="block w-full text-left" on:click={() => clickItem(item)}>
            <div class="relative overflow-hidden">
              {#if Array.isArray(item.hinh_anh)}
                <img
                  src={item.hinh_anh[0]}
                  alt={item.ten}
                  class="w-full h-56 object-cover transition-transform duration-500 group-hover:scale-105"
                  loading="lazy"
                />
              {:else}
                <img
                  src={item.hinh_anh}
                  alt={item.ten}
                  class="w-full h-56 object-cover transition-transform duration-500 group-hover:scale-105"
                  loading="lazy"
                />
              {/if}
              <div class="absolute inset-0 bg-linear-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </div>
            <div class="p-5">
              <h3 class="font-semibold text-lg text-gray-900 group-hover:text-indigo-600 transition-colors duration-200 mb-2">
                {item.ten}
              </h3>
              {#if item.mo_ta}
                <p class="text-sm text-gray-600 leading-relaxed line-clamp-2">
                  {item.mo_ta}
                </p>
              {/if}
            </div>
          </button>
        </article>
      {/each}
    </div>
  </div>
{/if}

<style>
  .shadow-soft {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
  }

  .shadow-fluffy {
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.08), 0 8px 10px -6px rgb(0 0 0 / 0.08);
  }
</style>