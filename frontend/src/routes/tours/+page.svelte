<script>
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { checkSession, getTourLocations, getLocationInfo, getItemsByLocation, createTour, getMyTours } from '$lib/api';

  let isLoggedIn = false;
  let username = '';
  let loading = true;

  // Step 1: Location selection
  let locations = [];
  let selectedLocations = [];
  let locationInfos = {};
  let loadingLocations = false;
  let loadingLocationInfo = {};

  // Step 2: Item selection
  let photos = [];
  let artifacts = [];
  let loadingItems = false;

  // Tour creation
  let tourName = '';
  let tourDescription = '';
  let selectedItems = [];
  let creating = false;
  let error = '';
  let success = '';

  // My tours
  let myTours = [];
  let loadingTours = false;

  // UI state
  let activeTab = 'create'; // 'create' | 'my-tours'
  let createStep = 1; // 1: chọn địa điểm, 2: chọn items

  onMount(async () => {
    if (!browser) return;

    // Check login status
    const session = await checkSession();
    isLoggedIn = session.isLoggedIn;
    username = session.username;

    if (!isLoggedIn) {
      goto('/');
      return;
    }

    // Load locations and tours
    await Promise.all([loadLocations(), loadMyTours()]);

    loading = false;
  });

  async function loadLocations() {
    loadingLocations = true;
    try {
      const result = await getTourLocations();
      if (result.ok) {
        locations = result.locations || [];
      }
    } catch (err) {
      console.error('Failed to load locations:', err);
    } finally {
      loadingLocations = false;
    }
  }

  async function toggleLocation(locationName) {
    const isSelected = selectedLocations.includes(locationName);

    if (isSelected) {
      selectedLocations = selectedLocations.filter(l => l !== locationName);
    } else {
      selectedLocations = [...selectedLocations, locationName];

      // Load info for this location if not already loaded
      if (!locationInfos[locationName]) {
        loadingLocationInfo[locationName] = true;
        try {
          const result = await getLocationInfo(locationName);
          if (result.ok) {
            locationInfos[locationName] = result.info;
          }
        } catch (err) {
          console.error('Failed to load location info:', err);
        } finally {
          loadingLocationInfo[locationName] = false;
        }
      }
    }
  }

  async function handleNextStep() {
    if (selectedLocations.length === 0) {
      error = 'Vui lòng chọn ít nhất một địa điểm';
      return;
    }

    error = '';
    loadingItems = true;

    try {
      console.log('Loading items for locations:', selectedLocations);
      const result = await getItemsByLocation(selectedLocations);
      console.log('Items result:', result);

      if (result.ok) {
        photos = result.photos || [];
        artifacts = result.artifacts || [];
        console.log('Loaded photos:', photos.length, 'artifacts:', artifacts.length);
        createStep = 2;
      } else {
        error = result.error || 'Có lỗi khi tải dữ liệu';
      }
    } catch (err) {
      console.error('Failed to load items:', err);
      error = 'Không thể kết nối với server';
    } finally {
      loadingItems = false;
    }
  }

  function handleBackStep() {
    createStep = 1;
    error = '';
  }

  function handleTabChange(tab) {
    activeTab = tab;
    if (tab === 'create') {
      // Reset create form
      createStep = 1;
      selectedLocations = [];
      selectedItems = [];
      tourName = '';
      tourDescription = '';
      error = '';
      success = '';
    }
  }

  async function loadMyTours() {
    loadingTours = true;
    try {
      const result = await getMyTours();
      if (result.ok) {
        myTours = result.tours || [];
      }
    } catch (err) {
      console.error('Failed to load tours:', err);
    } finally {
      loadingTours = false;
    }
  }

  function toggleItem(type, id) {
    const itemIndex = selectedItems.findIndex(item => item.type === type && item.id === id);
    if (itemIndex >= 0) {
      selectedItems = selectedItems.filter((_, i) => i !== itemIndex);
    } else {
      selectedItems = [...selectedItems, { type, id }];
    }
  }

  function isSelected(type, id) {
    return selectedItems.some(item => item.type === type && item.id === id);
  }

  function getItemOrder(type, id) {
    const index = selectedItems.findIndex(item => item.type === type && item.id === id);
    return index >= 0 ? index + 1 : null;
  }

  async function handleCreateTour() {
    if (!tourName.trim()) {
      error = 'Vui lòng nhập tên lộ trình';
      return;
    }
    
    if (selectedItems.length === 0) {
      error = 'Vui lòng chọn ít nhất 1 điểm tham quan';
      return;
    }
    
    error = '';
    success = '';
    creating = true;
    
    try {
      const result = await createTour(tourName, tourDescription, selectedItems);
      
      if (result.ok) {
        success = result.message || 'Đã tạo lộ trình thành công!';
        // Reset form
        tourName = '';
        tourDescription = '';
        selectedItems = [];
        // Reload tours
        await loadMyTours();
        // Switch to my tours tab
        setTimeout(() => {
          activeTab = 'my-tours';
          success = '';
        }, 2000);
      } else {
        error = result.error || 'Có lỗi xảy ra';
      }
    } catch (err) {
      console.error('Create tour error:', err);
      error = 'Không thể kết nối với server';
    } finally {
      creating = false;
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
</script>

<svelte:head>
  <title>Lộ Trình Tham Quan - Bảo Tàng Chứng Tích Chiến Tranh</title>
</svelte:head>

<div class="min-h-screen bg-[#1a1a1a] py-12 px-4">
  {#if loading}
    <div class="flex items-center justify-center min-h-[60vh]">
      <div class="text-center">
        <div class="w-16 h-16 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-400">Đang tải...</p>
      </div>
    </div>
  {:else}
    <div class="max-w-7xl mx-auto space-y-8 animate-fadeIn">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 animate-slideDown">
          🗺️ Lộ Trình Tham Quan
        </h1>
        <p class="text-gray-400 text-lg animate-slideDown" style="animation-delay: 0.1s;">
          Tạo lộ trình riêng để khám phá các di vật và ảnh lịch sử hào hùng
        </p>
      </div>

      <!-- Tabs -->
      <div class="flex gap-4 mb-8 animate-slideDown" style="animation-delay: 0.2s;">
        <button
          on:click={() => handleTabChange('create')}
          class="flex-1 px-6 py-4 rounded-xl font-bold transition-all duration-300 transform hover:scale-105
            {activeTab === 'create'
              ? 'bg-[#c4a574] text-[#1a1a1a]'
              : 'bg-[#2a2a2a] text-gray-400 hover:bg-[#3a3a3a] hover:text-white'}"
        >
          ✨ Tạo Lộ Trình Mới
        </button>
        <button
          on:click={() => handleTabChange('my-tours')}
          class="flex-1 px-6 py-4 rounded-xl font-bold transition-all duration-300 transform hover:scale-105
            {activeTab === 'my-tours'
              ? 'bg-[#c4a574] text-[#1a1a1a]'
              : 'bg-[#2a2a2a] text-gray-400 hover:bg-[#3a3a3a] hover:text-white'}"
        >
          📋 Lộ Trình Của Tôi ({myTours.length})
        </button>
      </div>

      {#if activeTab === 'create'}
        <!-- Create Tour -->
        <div class="space-y-8">
          <!-- Progress Steps -->
          <div class="flex items-center justify-center gap-4 mb-8 animate-slideDown" style="animation-delay: 0.3s;">
            <div class="flex items-center gap-2">
              <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold
                {createStep === 1 ? 'bg-[#c4a574] text-[#1a1a1a]' : 'bg-[#2a2a2a] text-gray-400'}">
                1
              </div>
              <span class="text-white font-semibold">Chọn Địa Điểm</span>
            </div>
            <div class="w-16 h-1 bg-[#2a2a2a] rounded-full">
              <div class="h-full bg-[#c4a574] rounded-full transition-all duration-300"
                style="width: {createStep === 2 ? '100%' : '0%'}"></div>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold
                {createStep === 2 ? 'bg-[#c4a574] text-[#1a1a1a]' : 'bg-[#2a2a2a] text-gray-400'}">
                2
              </div>
              <span class="text-white font-semibold">Chọn Điểm Tham Quan</span>
            </div>
          </div>

          {#if error}
            <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg animate-shake">
              ⚠️ {error}
            </div>
          {/if}

          {#if success}
            <div class="bg-green-500/20 border border-green-500 text-green-400 px-4 py-3 rounded-lg animate-slideDown">
              ✅ {success}
            </div>
          {/if}

          {#if createStep === 1}
            <!-- Step 1: Select Locations -->
            <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn">
              <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <span class="text-3xl">📍</span>
                Chọn Địa Điểm Tham Quan
              </h2>

              <p class="text-gray-400 mb-6">
                Chọn các địa điểm bạn muốn khám phá. Mỗi địa điểm có nhiều ảnh và di vật lịch sử.
              </p>

              {#if loadingLocations}
                <div class="text-center py-12">
                  <div class="w-12 h-12 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                  <p class="text-gray-400">Đang tải địa điểm...</p>
                </div>
              {:else}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {#each locations as location}
                    <button
                      on:click={() => toggleLocation(location.name)}
                      class="relative bg-[#1a1a1a] rounded-xl p-6 border-2 transition-all duration-300 transform hover:scale-105 text-left
                        {selectedLocations.includes(location.name)
                          ? 'border-[#c4a574] shadow-lg shadow-[#c4a574]/20'
                          : 'border-[#4a4a4a] hover:border-[#c4a574]/50'}"
                    >
                      <div class="flex items-start justify-between mb-3">
                        <h3 class="text-lg font-bold text-white pr-8">{location.name}</h3>
                        {#if selectedLocations.includes(location.name)}
                          <div class="absolute top-4 right-4 bg-[#c4a574] text-[#1a1a1a] w-8 h-8 rounded-full flex items-center justify-center">
                            ✓
                          </div>
                        {/if}
                      </div>

                      <p class="text-gray-400 text-sm mb-3">
                        📊 {location.count} hiện vật/ảnh
                      </p>

                      {#if selectedLocations.includes(location.name)}
                        {#if loadingLocationInfo[location.name]}
                          <div class="flex items-center gap-2 text-gray-400 text-sm">
                            <div class="w-4 h-4 border-2 border-[#c4a574] border-t-transparent rounded-full animate-spin"></div>
                            <span>Đang tải thông tin...</span>
                          </div>
                        {:else if locationInfos[location.name]}
                          <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-3 mt-3">
                            <p class="text-gray-300 text-sm leading-relaxed">
                              💡 {locationInfos[location.name]}
                            </p>
                          </div>
                        {/if}
                      {/if}
                    </button>
                  {/each}
                </div>

                <div class="mt-8 flex items-center justify-between bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4">
                  <p class="text-gray-300 flex items-center gap-2">
                    <span class="text-xl">✅</span>
                    <span>Đã chọn: <strong class="text-[#c4a574]">{selectedLocations.length}</strong> địa điểm</span>
                  </p>
                  <button
                    on:click={handleNextStep}
                    disabled={selectedLocations.length === 0}
                    class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-3 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center gap-2"
                  >
                    <span>Tiếp Theo</span>
                    <span>→</span>
                  </button>
                </div>
              {/if}
            </div>
          {:else}
            <!-- Step 2: Tour Info & Select Items -->
            <div class="space-y-8">
              <!-- Tour Info Form -->
              <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn">
                <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                  <span class="text-3xl">📝</span>
                  Thông Tin Lộ Trình
                </h2>

                <div class="space-y-4">
                  <div>
                    <label class="block text-gray-300 font-semibold mb-2">
                      Tên Lộ Trình <span class="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      bind:value={tourName}
                      placeholder="VD: Hành Trình Chiến Tranh Việt Nam"
                      class="w-full px-4 py-3 bg-[#1a1a1a] border-2 border-[#4a4a4a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#c4a574] transition-colors duration-200"
                      required
                    />
                  </div>

                  <div>
                    <label class="block text-gray-300 font-semibold mb-2">
                      Mô Tả
                    </label>
                    <textarea
                      bind:value={tourDescription}
                      rows="3"
                      placeholder="Mô tả ngắn về lộ trình của bạn..."
                      class="w-full px-4 py-3 bg-[#1a1a1a] border-2 border-[#4a4a4a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#c4a574] transition-colors duration-200"
                    ></textarea>
                  </div>

                  <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4">
                    <p class="text-gray-300 text-sm flex items-center gap-2">
                      <span class="text-xl">📍</span>
                      <span>Địa điểm: <strong class="text-[#c4a574]">{selectedLocations.join(', ')}</strong></span>
                    </p>
                    <p class="text-gray-300 text-sm flex items-center gap-2 mt-2">
                      <span class="text-xl">🎯</span>
                      <span>Đã chọn: <strong class="text-[#c4a574]">{selectedItems.length}</strong> điểm tham quan</span>
                    </p>
                  </div>
                </div>
              </div>

              <!-- Select Items -->
              <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn" style="animation-delay: 0.1s;">
                <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                  <span class="text-3xl">🖼️</span>
                  Chọn Điểm Tham Quan
                </h2>

                {#if loadingItems}
                  <div class="text-center py-12">
                    <div class="w-12 h-12 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                    <p class="text-gray-400">Đang tải...</p>
                  </div>
                {:else}
                  {#if photos.length === 0 && artifacts.length === 0}
                    <div class="text-center py-12">
                      <div class="text-6xl mb-4">📭</div>
                      <p class="text-gray-400 text-lg mb-2">Không có hiện vật/ảnh tại các địa điểm đã chọn</p>
                      <p class="text-gray-500 text-sm">Vui lòng quay lại và chọn địa điểm khác</p>
                    </div>
                  {:else}
                    <div class="space-y-8">
                      <!-- Photos -->
                      {#if photos.length > 0}
                        <div>
                          <h3 class="text-xl font-bold text-[#c4a574] mb-4">📷 Ảnh Lịch Sử ({photos.length})</h3>
                          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {#each photos as photo}
                              <button
                                on:click={() => toggleItem('photo', photo.id)}
                                class="relative bg-[#1a1a1a] rounded-xl overflow-hidden border-2 transition-all duration-300 transform hover:scale-105
                                  {isSelected('photo', photo.id)
                                    ? 'border-[#c4a574] shadow-lg shadow-[#c4a574]/20'
                                    : 'border-[#4a4a4a] hover:border-[#c4a574]/50'}"
                              >
                                {#if photo.hinh_anh}
                                  <img src={photo.hinh_anh} alt={photo.ten || 'Photo'} class="w-full h-48 object-cover" />
                                {:else}
                                  <div class="w-full h-48 bg-[#2a2a2a] flex items-center justify-center">
                                    <span class="text-6xl">📷</span>
                                  </div>
                                {/if}
                                <div class="p-4">
                                  <h4 class="text-white font-semibold mb-1 line-clamp-2">{photo.ten || 'Ảnh lịch sử'}</h4>
                                  {#if photo.dia_diem}
                                    <p class="text-gray-400 text-sm">📍 {photo.dia_diem}</p>
                                  {/if}
                                </div>
                                {#if isSelected('photo', photo.id)}
                                  <div class="absolute top-2 right-2 bg-[#c4a574] text-[#1a1a1a] w-8 h-8 rounded-full flex items-center justify-center font-bold">
                                    {getItemOrder('photo', photo.id)}
                                  </div>
                                {/if}
                              </button>
                            {/each}
                          </div>
                        </div>
                      {/if}

                      <!-- Artifacts -->
                      {#if artifacts.length > 0}
                        <div>
                          <h3 class="text-xl font-bold text-[#c4a574] mb-4">🏺 Di Vật Lịch Sử ({artifacts.length})</h3>
                          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {#each artifacts as artifact}
                              <button
                                on:click={() => toggleItem('artifact', artifact.id)}
                                class="relative bg-[#1a1a1a] rounded-xl overflow-hidden border-2 transition-all duration-300 transform hover:scale-105
                                  {isSelected('artifact', artifact.id)
                                    ? 'border-[#c4a574] shadow-lg shadow-[#c4a574]/20'
                                    : 'border-[#4a4a4a] hover:border-[#c4a574]/50'}"
                              >
                                {#if artifact.hinh_anh}
                                  <img src={artifact.hinh_anh} alt={artifact.ten || 'Artifact'} class="w-full h-48 object-cover" />
                                {:else}
                                  <div class="w-full h-48 bg-[#2a2a2a] flex items-center justify-center">
                                    <span class="text-6xl">🏺</span>
                                  </div>
                                {/if}
                                <div class="p-4">
                                  <h4 class="text-white font-semibold mb-1 line-clamp-2">{artifact.ten || 'Di vật lịch sử'}</h4>
                                  {#if artifact.dia_diem}
                                    <p class="text-gray-400 text-sm">📍 {artifact.dia_diem}</p>
                                  {/if}
                                </div>
                                {#if isSelected('artifact', artifact.id)}
                                  <div class="absolute top-2 right-2 bg-[#c4a574] text-[#1a1a1a] w-8 h-8 rounded-full flex items-center justify-center font-bold">
                                    {getItemOrder('artifact', artifact.id)}
                                  </div>
                                {/if}
                              </button>
                            {/each}
                          </div>
                        </div>
                      {/if}
                    </div>
                  {/if}
                {/if}
          </div>

              <!-- Action Buttons -->
              <div class="flex justify-between items-center animate-scaleIn" style="animation-delay: 0.2s;">
                <button
                  on:click={handleBackStep}
                  class="bg-[#2a2a2a] hover:bg-[#3a3a3a] text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
                >
                  <span>←</span>
                  <span>Quay Lại</span>
                </button>

                <button
                  on:click={handleCreateTour}
                  disabled={creating || selectedItems.length === 0}
                  class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-4 px-12 rounded-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center gap-3 text-lg"
                >
                  {#if creating}
                    <div class="w-6 h-6 border-2 border-[#1a1a1a] border-t-transparent rounded-full animate-spin"></div>
                    <span>Đang tạo...</span>
                  {:else}
                    <span>🚀</span>
                    <span>Tạo Lộ Trình</span>
                  {/if}
                </button>
              </div>
            </div>
          {/if}
        </div>
      {:else}
        <!-- My Tours -->
        <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn">
          <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <span class="text-3xl">📋</span>
            Lộ Trình Của Tôi
          </h2>

          {#if loadingTours}
            <div class="text-center py-12">
              <div class="w-12 h-12 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p class="text-gray-400">Đang tải...</p>
            </div>
          {:else if myTours.length === 0}
            <div class="text-center py-12">
              <div class="text-6xl mb-4">🗺️</div>
              <p class="text-gray-400 text-lg mb-4">Bạn chưa có lộ trình nào</p>
              <button
                on:click={() => activeTab = 'create'}
                class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105"
              >
                Tạo Lộ Trình Đầu Tiên
              </button>
            </div>
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              {#each myTours as tour, i}
                <div 
                  class="bg-[#1a1a1a] rounded-xl p-6 border border-[#4a4a4a] hover:border-[#c4a574] transition-all duration-300 animate-slideUp"
                  style="animation-delay: {i * 0.05}s;"
                >
                  <h3 class="text-xl font-bold text-white mb-2">{tour.tour_name}</h3>
                  {#if tour.description}
                    <p class="text-gray-400 mb-4">{tour.description}</p>
                  {/if}
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-[#c4a574]">📍 {tour.items?.length || 0} điểm</span>
                    <span class="text-gray-500">{formatDate(tour.created_at)}</span>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes scaleIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  .animate-fadeIn {
    animation: fadeIn 0.5s ease-out;
  }

  .animate-slideDown {
    animation: slideDown 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .animate-slideUp {
    animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .animate-scaleIn {
    animation: scaleIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .animate-shake {
    animation: shake 0.4s ease-in-out;
  }

  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>

