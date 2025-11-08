<script>
  import { onMount } from 'svelte';
  import { getOptionData } from '$lib/dataProvider';
  import VoiceInteractionModal from './VoiceInteractionModal.svelte';

  let items = [];
  let loading = true;
  let error = '';
  let showVoiceModal = false;
  let selectedItem = null;

  onMount(async () => {
    try {
      loading = true;
      const data = await getOptionData('vat');
      console.log('Vat data received:', data);

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
      console.error('Error loading Vat data:', e);
      error = `Không tải được dữ liệu Vật: ${e.message}`;
    } finally {
      loading = false;
    }
  });

  function clickItem(item) {
    selectedItem = item;
    showVoiceModal = true;
  }

  function closeVoiceModal() {
    showVoiceModal = false;
    selectedItem = null;
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
      {#each items as item, index}
        <article class="stagger-item group relative rounded-3xl overflow-hidden bg-white shadow-smooth hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 transform-smooth">
          <button class="block w-full text-left" on:click={() => clickItem(item)}>
            <div class="relative overflow-hidden">
              {#if Array.isArray(item.hinh_anh)}
                <img
                  src={item.hinh_anh[0]}
                  alt={item.ten}
                  class="w-full h-56 object-cover transition-transform duration-700 group-hover:scale-110"
                  loading="lazy"
                />
              {:else}
                <img
                  src={item.hinh_anh}
                  alt={item.ten}
                  class="w-full h-56 object-cover transition-transform duration-700 group-hover:scale-110"
                  loading="lazy"
                />
              {/if}
              <div class="absolute inset-0 bg-linear-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div class="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 text-xs font-semibold text-gray-700 opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                Xem chi tiết
              </div>
            </div>
            <div class="p-5">
              <h3 class="font-semibold text-lg text-gray-900 group-hover:text-indigo-600 transition-colors duration-300 mb-2">
                {item.ten}
              </h3>
              {#if item.mo_ta}
                <p class="text-sm text-gray-600 leading-relaxed line-clamp-2 group-hover:text-gray-700 transition-colors duration-300">
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

<!-- Voice Interaction Modal -->
{#if selectedItem}
  <VoiceInteractionModal
    show={showVoiceModal}
    itemName={selectedItem.ten}
    onClose={closeVoiceModal}
  />
{/if}

<style>
  .shadow-soft {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
  }

  .shadow-fluffy {
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.08), 0 8px 10px -6px rgb(0 0 0 / 0.08);
  }
</style>