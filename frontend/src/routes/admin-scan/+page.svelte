<script>
  import { onMount } from 'svelte';
  import { checkSession, getProfile } from '$lib/api';
  import AdminQRScanner from '$lib/components/AdminQRScanner.svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';

  let isLoggedIn = false;
  let username = '';
  let isAdmin = false;
  let loading = true;
  let showScanner = false;
  let selectedLocation = '';
  let error = '';

  // Available locations from data.json
  const locations = [
    'Khu Trưng Bày Trong Nhà',
    'Khu Trưng Bày Ngoài Trời',
    'Khu Trưng Bày Ảnh Quốc Tế',
    'Phòng Trà Tân'
  ];

  onMount(async () => {
    if (!browser) return;

    // Check if Html5Qrcode library is loaded
    const checkLibrary = setInterval(() => {
      if (window.Html5Qrcode) {
        console.log('✅ Html5Qrcode library is ready');
        clearInterval(checkLibrary);
      }
    }, 100);
    
    // Stop checking after 5 seconds
    setTimeout(() => clearInterval(checkLibrary), 5000);

    const session = await checkSession();
    isLoggedIn = session.isLoggedIn;
    username = session.username || '';

    if (!isLoggedIn) {
      goto('/');
      return;
    }

    // Check if user is admin
    try {
      const profile = await getProfile();
      if (profile.ok) {
        isAdmin = profile.is_admin === true;
        if (!isAdmin) {
          error = 'Bạn không có quyền truy cập trang này. Chỉ admin mới có thể sử dụng chức năng quét QR bằng camera.';
        }
      }
    } catch (err) {
      console.error('Error getting profile:', err);
      error = 'Không thể kiểm tra quyền người dùng';
    }

    loading = false;
  });

  function openScanner(location) {
    selectedLocation = location;
    showScanner = true;
    error = '';
  }

  function closeScanner() {
    showScanner = false;
    selectedLocation = '';
  }
</script>

<svelte:head>
  <title>Quét QR Code - Admin | Bảo Tàng Chứng Tích Chiến Tranh</title>
  <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
</svelte:head>

{#if loading}
  <div class="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#2a2a2a] to-[#1a1a1a] flex items-center justify-center">
    <div class="text-center">
      <div class="w-16 h-16 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-gray-400">Đang tải...</p>
    </div>
  </div>
{:else if !isLoggedIn}
  <div class="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#2a2a2a] to-[#1a1a1a] flex items-center justify-center p-4">
    <div class="bg-[#2a2a2a] rounded-xl p-8 max-w-md w-full border border-[#4a4a4a] text-center">
      <h2 class="text-2xl font-bold text-white mb-4">Cần Đăng Nhập</h2>
      <p class="text-gray-400 mb-6">Vui lòng đăng nhập để sử dụng tính năng này</p>
      <a
        href="/"
        class="inline-block bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-6 py-3 rounded-lg transition-all"
      >
        Về Trang Chủ
      </a>
    </div>
  </div>
{:else if !isAdmin}
  <div class="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#2a2a2a] to-[#1a1a1a] flex items-center justify-center p-4">
    <div class="bg-[#2a2a2a] rounded-xl p-8 max-w-md w-full border border-[#4a4a4a] text-center">
      <h2 class="text-2xl font-bold text-red-400 mb-4">Không Có Quyền Truy Cập</h2>
      {#if error}
        <p class="text-gray-400 mb-6">{error}</p>
      {:else}
        <p class="text-gray-400 mb-6">Chỉ admin mới có thể sử dụng chức năng quét QR bằng camera</p>
      {/if}
      <a
        href="/"
        class="inline-block bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-6 py-3 rounded-lg transition-all"
      >
        Về Trang Chủ
      </a>
    </div>
  </div>
{:else}
  <div class="min-h-screen bg-gradient-to-br from-[#1a1a1a] via-[#2a2a2a] to-[#1a1a1a] p-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-[#c4a574] mb-2">Quét QR Code - Admin</h1>
        <p class="text-gray-400">Sử dụng camera để quét QR code của khách và xác nhận check-in</p>
        {#if username}
          <p class="text-sm text-gray-500 mt-2">
            Đăng nhập với: <span class="text-[#c4a574]">{username}</span> 
            <span class="text-green-400">(Admin)</span>
          </p>
        {/if}
      </div>

      {#if error}
        <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6">
          ⚠️ {error}
        </div>
      {/if}

      <!-- Location Selection -->
      <div class="bg-[#2a2a2a] rounded-xl p-6 border border-[#4a4a4a] mb-6">
        <h2 class="text-xl font-bold text-white mb-4">Chọn Địa Điểm</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {#each locations as location}
            <button
              on:click={() => openScanner(location)}
              class="bg-[#1a1a1a] hover:bg-[#3a3a3a] border border-[#4a4a4a] hover:border-[#c4a574] text-white px-6 py-4 rounded-lg transition-all duration-300 transform hover:scale-105 text-left"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-semibold">{location}</p>
                  <p class="text-xs text-gray-500 mt-1">Quét QR code tại địa điểm này</p>
                </div>
                <svg class="w-6 h-6 text-[#c4a574]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </button>
          {/each}
        </div>
      </div>

      <!-- Instructions -->
      <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-xl p-6">
        <h3 class="text-lg font-semibold text-[#c4a574] mb-3">Hướng Dẫn Sử Dụng</h3>
        <ul class="space-y-2 text-gray-300 text-sm">
          <li class="flex items-start gap-2">
            <span class="text-[#c4a574]">1.</span>
            <span>Chọn địa điểm bạn đang đặt camera quét QR</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-[#c4a574]">2.</span>
            <span>Nhấn vào nút địa điểm để mở camera quét QR code</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-[#c4a574]">3.</span>
            <span>Đưa QR code của khách vào khung camera để quét</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-[#c4a574]">4.</span>
            <span>Hệ thống sẽ tự động xác nhận check-in và cộng 1000 điểm thưởng cho khách</span>
          </li>
        </ul>
        <div class="mt-4 p-3 bg-blue-500/20 border border-blue-500/30 rounded">
          <p class="text-blue-400 text-sm">
            <strong>Lưu ý:</strong> Chức năng này chỉ dành cho admin. Khách hàng sẽ sử dụng mã QR được tạo từ chức năng check-in để được quét tại địa điểm.
          </p>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- QR Scanner Modal -->
{#if showScanner && selectedLocation}
  <AdminQRScanner
    show={showScanner}
    locationName={selectedLocation}
    onClose={closeScanner}
  />
{/if}

<style>
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>

