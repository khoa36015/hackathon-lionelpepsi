<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { checkSession, getProfile } from '$lib/api';

  let loading = true;
  let isLoggedIn = false;
  let userInfo = {
    username: '',
    ticketCode: '',
    rewardPoints: 0,
    accountStatus: '',
    isAdmin: false
  };

  onMount(async () => {
    if (!browser) return;
    
    // Check login status
    const session = await checkSession();
    isLoggedIn = session.isLoggedIn;
    
    if (!isLoggedIn) {
      goto('/');
      return;
    }
    
    // Load user profile
    await loadProfile();
    
    loading = false;
  });

  async function loadProfile() {
    try {
      const res = await fetch('http://localhost:3000/api/profile', {
        method: 'GET',
        credentials: 'include'
      });
      
      const data = await res.json();
      
      if (data.ok) {
        userInfo = {
          username: data.username,
          ticketCode: data.ticket_code || 'Chưa mua vé',
          rewardPoints: data.reward_points || 0,
          accountStatus: data.account_status || 'active',
          isAdmin: data.is_admin === true
        };
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  }
</script>

<svelte:head>
  <title>Hồ Sơ - Bảo Tàng Chứng Tích Chiến Tranh</title>
</svelte:head>

<div class="min-h-screen bg-[#2a2a2a] py-12 px-4">
  <div class="max-w-4xl mx-auto">
    {#if loading}
      <div class="flex items-center justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#c4a574]"></div>
      </div>
    {:else}
      <!-- Profile Header -->
      <div 
        class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] mb-8"
        in:fade={{ duration: 300 }}
      >
        <div class="flex items-center gap-6">
          <!-- Avatar -->
          <div class="w-24 h-24 rounded-full bg-gradient-to-br from-[#c4a574] to-[#8b7355] flex items-center justify-center shadow-lg">
            <span class="text-4xl font-bold text-[#1a1a1a]">
              {userInfo.username.charAt(0).toUpperCase()}
            </span>
          </div>
          
          <!-- User Info -->
          <div class="flex-1">
            <h1 class="text-3xl font-bold text-white mb-2">
              {userInfo.username}
            </h1>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="px-3 py-1 rounded-full text-xs font-semibold bg-green-500/20 text-green-400 border border-green-500/30">
                Tài khoản hoạt động
              </span>
              {#if userInfo.isAdmin}
                <span class="px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  👑 Admin
                </span>
              {/if}
              <span class="px-3 py-1 rounded-full text-xs font-semibold bg-[#c4a574]/20 text-[#c4a574] border border-[#c4a574]/30">
                ⭐ {userInfo.rewardPoints} điểm thưởng
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Profile Details -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Ticket Info Card -->
        <div 
          class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-6 shadow-2xl border border-[#4a4a4a]"
          in:fly={{ y: 20, duration: 300, delay: 100 }}
        >
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-12 rounded-lg bg-[#c4a574]/20 flex items-center justify-center">
              <span class="text-2xl">🎫</span>
            </div>
            <h2 class="text-xl font-bold text-white">Thông Tin Vé</h2>
          </div>
          
          <div class="space-y-3">
            <div class="flex justify-between items-center py-3 border-b border-[#4a4a4a]">
              <span class="text-gray-400">Mã số vé:</span>
              <span class="text-white font-semibold">{userInfo.ticketCode}</span>
            </div>
            
            {#if userInfo.ticketCode !== 'Chưa mua vé'}
              <div class="mt-4">
                <a 
                  href="/tickets"
                  class="block w-full text-center px-4 py-2 rounded-lg bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-semibold transition-colors"
                >
                  Xem Chi Tiết Vé
                </a>
              </div>
            {:else}
              <div class="mt-4">
                <a 
                  href="/tickets"
                  class="block w-full text-center px-4 py-2 rounded-lg bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-semibold transition-colors"
                >
                  Mua Vé Ngay
                </a>
              </div>
            {/if}
          </div>
        </div>

        <!-- Account Info Card -->
        <div 
          class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-6 shadow-2xl border border-[#4a4a4a]"
          in:fly={{ y: 20, duration: 300, delay: 200 }}
        >
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-12 rounded-lg bg-[#c4a574]/20 flex items-center justify-center">
              <span class="text-2xl">👤</span>
            </div>
            <h2 class="text-xl font-bold text-white">Thông Tin Tài Khoản</h2>
          </div>
          
          <div class="space-y-3">
            <div class="flex justify-between items-center py-3 border-b border-[#4a4a4a]">
              <span class="text-gray-400">Tên tài khoản:</span>
              <span class="text-white font-semibold">{userInfo.username}</span>
            </div>
            
            <div class="flex justify-between items-center py-3 border-b border-[#4a4a4a]">
              <span class="text-gray-400">Điểm thưởng:</span>
              <span class="text-[#c4a574] font-semibold">⭐ {userInfo.rewardPoints}</span>
            </div>
            
            <div class="flex justify-between items-center py-3">
              <span class="text-gray-400">Trạng thái:</span>
              <span class="text-green-400 font-semibold">Hoạt động</span>
            </div>
          </div>
        </div>

        <!-- Quick Actions Card -->
        <div 
          class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-6 shadow-2xl border border-[#4a4a4a] md:col-span-2"
          in:fly={{ y: 20, duration: 300, delay: 300 }}
        >
          <div class="flex items-center gap-3 mb-4">
            <div class="w-12 h-12 rounded-lg bg-[#c4a574]/20 flex items-center justify-center">
              <span class="text-2xl">⚡</span>
            </div>
            <h2 class="text-xl font-bold text-white">Thao Tác Nhanh</h2>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a 
              href="/tours"
              class="flex items-center gap-3 p-4 rounded-lg bg-[#1a1a1a] hover:bg-[#4a4a4a] border border-[#4a4a4a] hover:border-[#c4a574] transition-all group"
            >
              <span class="text-3xl">🗺️</span>
              <div>
                <div class="text-white font-semibold group-hover:text-[#c4a574] transition-colors">Lộ Trình</div>
                <div class="text-xs text-gray-400">Tạo lộ trình tham quan</div>
              </div>
            </a>
            
            <a 
              href="/feedback"
              class="flex items-center gap-3 p-4 rounded-lg bg-[#1a1a1a] hover:bg-[#4a4a4a] border border-[#4a4a4a] hover:border-[#c4a574] transition-all group"
            >
              <span class="text-3xl">💬</span>
              <div>
                <div class="text-white font-semibold group-hover:text-[#c4a574] transition-colors">Feedback</div>
                <div class="text-xs text-gray-400">Gửi phản hồi</div>
              </div>
            </a>
            
            <a 
              href="/tickets"
              class="flex items-center gap-3 p-4 rounded-lg bg-[#1a1a1a] hover:bg-[#4a4a4a] border border-[#4a4a4a] hover:border-[#c4a574] transition-all group"
            >
              <span class="text-3xl">🎫</span>
              <div>
                <div class="text-white font-semibold group-hover:text-[#c4a574] transition-colors">Vé Của Tôi</div>
                <div class="text-xs text-gray-400">Quản lý vé tham quan</div>
              </div>
            </a>
            
            {#if userInfo.isAdmin}
              <a 
                href="/admin-scan"
                class="flex items-center gap-3 p-4 rounded-lg bg-[#1a1a1a] hover:bg-[#4a4a4a] border border-[#4a4a4a] hover:border-[#c4a574] transition-all group md:col-span-3"
              >
                <span class="text-3xl">📷</span>
                <div>
                  <div class="text-white font-semibold group-hover:text-[#c4a574] transition-colors">Quét QR Code - Admin</div>
                  <div class="text-xs text-gray-400">Quét QR code của khách để xác nhận check-in</div>
                </div>
              </a>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>

