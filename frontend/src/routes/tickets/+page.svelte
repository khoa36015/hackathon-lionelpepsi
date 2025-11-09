<script>
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { checkSession, getBankAccounts, purchaseTicket, getTicketStatus, getTicketQR } from '$lib/api';

  let isLoggedIn = false;
  let username = '';
  let loading = true;
  let hasTicket = false;
  let ticketInfo = null;

  // QR code
  let qrImage = '';
  let loadingQR = false;

  // Purchase form
  let bankAccounts = [];
  let selectedAccount = '';
  let bankPassword = '';
  let purchasing = false;
  let error = '';
  let success = '';
  let showPassword = false;

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
    
    // Load bank accounts
    const bankData = await getBankAccounts();
    if (bankData.ok) {
      bankAccounts = bankData.accounts;
      if (bankAccounts.length > 0) {
        selectedAccount = bankAccounts[0].account_number;
      }
    }
    
    // Check ticket status
    await loadTicketStatus();
    
    loading = false;
  });

  async function loadTicketStatus() {
    const status = await getTicketStatus();
    if (status.ok) {
      hasTicket = status.has_ticket;
      if (hasTicket) {
        ticketInfo = {
          code: status.ticket_code,
          purchaseDate: status.purchase_date,
          amountPaid: status.amount_paid
        };
        // Load QR code
        await loadQRCode();
      }
    }
  }

  async function loadQRCode() {
    if (!hasTicket) return;

    loadingQR = true;
    try {
      const qrData = await getTicketQR();
      if (qrData.ok) {
        qrImage = qrData.qr_image;
      }
    } catch (err) {
      console.error('Failed to load QR code:', err);
    } finally {
      loadingQR = false;
    }
  }

  async function handlePurchase() {
    if (!selectedAccount || !bankPassword) {
      error = 'Vui lòng chọn tài khoản và nhập mật khẩu';
      return;
    }
    
    error = '';
    success = '';
    purchasing = true;
    
    try {
      const result = await purchaseTicket(selectedAccount, bankPassword);
      
      if (result.ok) {
        success = 'Mua vé thành công!';
        bankPassword = '';
        // Reload ticket status to get latest ticket info
        await loadTicketStatus();
      } else {
        error = result.error || 'Có lỗi xảy ra';
      }
    } catch (err) {
      error = 'Không thể kết nối với server';
    } finally {
      purchasing = false;
    }
  }

  function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', { 
      style: 'currency', 
      currency: 'VND' 
    }).format(amount);
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function copyTicketCode() {
    if (browser && ticketInfo?.code) {
      navigator.clipboard.writeText(ticketInfo.code);
      success = 'Đã copy mã vé!';
      setTimeout(() => success = '', 2000);
    }
  }
</script>

<svelte:head>
  <title>Mua Vé - Bảo Tàng Chứng Tích Chiến Tranh</title>
</svelte:head>

<div class="min-h-screen bg-[#2a2a2a] py-12">
  <div class="container mx-auto px-4 max-w-4xl">
    
    {#if loading}
      <div class="flex items-center justify-center py-20 animate-fadeIn">
        <div class="w-16 h-16 border-4 border-[#c4a574] border-t-transparent rounded-full animate-smoothSpin"></div>
      </div>
    {:else if hasTicket && ticketInfo}
      <!-- Ticket Display -->
      <div class="animate-fadeIn">
        <h1 class="text-4xl font-bold text-[#c4a574] mb-8 text-center animate-slideInUp">
          🎫 Vé Của Bạn
        </h1>
        
        <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn" style="animation-delay: 0.2s;">
          <!-- Ticket Header -->
          <div class="text-center mb-8 pb-6 border-b border-[#4a4a4a]">
            <div class="inline-block bg-[#c4a574] text-[#1a1a1a] px-6 py-2 rounded-full font-bold text-sm uppercase tracking-wider mb-4">
              Vé Hợp Lệ
            </div>
            <h2 class="text-2xl font-bold text-white mb-2">Bảo Tàng Chứng Tích Chiến Tranh</h2>
            <p class="text-gray-400 text-sm">28 Võ Văn Tần, Phường 6, Quận 3, TP.HCM</p>
          </div>
          
          <!-- Ticket Code -->
          <div class="bg-[#1a1a1a] rounded-xl p-6 mb-6 border border-[#c4a574]/30">
            <p class="text-gray-400 text-sm mb-2 text-center">Mã Vé</p>
            <div class="flex items-center justify-center gap-3">
              <p class="text-3xl font-mono font-bold text-[#c4a574] tracking-wider">
                {ticketInfo.code}
              </p>
              <button
                on:click={copyTicketCode}
                class="p-2 hover:bg-[#3a3a3a] rounded-lg transition-all duration-300 transform hover:scale-110"
                title="Copy mã vé"
              >
                <svg class="w-6 h-6 text-[#c4a574]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Ticket Details -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
              <p class="text-gray-400 text-sm mb-1">Chủ Vé</p>
              <p class="text-white font-semibold text-lg">{username}</p>
            </div>
            
            <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
              <p class="text-gray-400 text-sm mb-1">Ngày Mua</p>
              <p class="text-white font-semibold">{formatDate(ticketInfo.purchaseDate)}</p>
            </div>
            
            <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
              <p class="text-gray-400 text-sm mb-1">Số Tiền</p>
              <p class="text-[#c4a574] font-bold text-xl">{formatCurrency(ticketInfo.amountPaid)}</p>
            </div>
            
            <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
              <p class="text-gray-400 text-sm mb-1">Loại Vé</p>
              <p class="text-white font-semibold">Vé Người Lớn</p>
            </div>
          </div>
          
          <!-- QR Code -->
          <div class="bg-white rounded-xl p-6 flex items-center justify-center mb-6">
            {#if loadingQR}
              <div class="text-center py-8">
                <div class="w-12 h-12 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                <p class="text-gray-600 text-sm">Đang tạo mã QR...</p>
              </div>
            {:else if qrImage}
              <div class="text-center">
                <img src={qrImage} alt="QR Code" class="w-48 h-48 mx-auto mb-3" />
                <p class="text-gray-600 text-sm">Quét mã QR tại cổng vào</p>
              </div>
            {:else}
              <div class="text-center">
                <div class="w-48 h-48 bg-gray-200 rounded-lg flex items-center justify-center mb-3">
                  <svg class="w-32 h-32 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M3 11h8V3H3v8zm2-6h4v4H5V5zm-2 8h8v8H3v-8zm2 2v4h4v-4H5zm8-12v8h8V3h-8zm2 2h4v4h-4V5zm0 8h2v2h-2v-2zm2 2h2v2h-2v-2zm-2 2h2v2h-2v-2zm4-4h2v4h-2v-4zm0 6h2v2h-2v-2z"/>
                  </svg>
                </div>
                <p class="text-gray-600 text-sm">Không thể tạo mã QR</p>
              </div>
            {/if}
          </div>
          
          <!-- Instructions -->
          <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4">
            <h3 class="text-[#c4a574] font-semibold mb-2 flex items-center gap-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              Hướng Dẫn Sử Dụng
            </h3>
            <ul class="text-gray-300 text-sm space-y-1">
              <li>• Xuất trình mã vé hoặc QR code tại cổng vào</li>
              <li>• Vé có hiệu lực trong vòng 30 ngày kể từ ngày mua</li>
              <li>• Không được chuyển nhượng hoặc bán lại vé</li>
              <li>• Liên hệ: (028) 3930 5587 nếu cần hỗ trợ</li>
            </ul>
          </div>
        </div>
        
        {#if success}
          <div class="mt-4 bg-green-500/20 border border-green-500 text-green-400 px-4 py-3 rounded-lg animate-slideInUp">
            {success}
          </div>
        {/if}
        
        <!-- Purchase New Ticket Section -->
        <div class="mt-8 bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn">
          <h2 class="text-2xl font-bold text-[#c4a574] mb-6 text-center">
            🛒 Mua Vé Mới
          </h2>
          <p class="text-gray-400 text-center mb-6">
            Bạn có thể mua vé mới bất cứ lúc nào. Vé mới sẽ thay thế vé hiện tại.
          </p>
          
          <form on:submit|preventDefault={handlePurchase} class="space-y-6">
            <!-- Bank Account Selection -->
            <div>
              <label class="block text-gray-300 font-semibold mb-3">
                🏦 Chọn Tài Khoản Ngân Hàng
              </label>
              <select
                bind:value={selectedAccount}
                class="w-full bg-[#1a1a1a] border border-[#4a4a4a] text-white rounded-lg px-4 py-3 focus:border-[#c4a574] focus:ring-2 focus:ring-[#c4a574]/50 focus:outline-none transition-all duration-300"
                required
              >
                {#each bankAccounts as account}
                  <option value={account.account_number}>
                    {account.account_number} - {account.name} ({formatCurrency(account.balance)})
                  </option>
                {/each}
              </select>
            </div>
            
            <!-- Bank Password -->
            <div>
              <label class="block text-gray-300 font-semibold mb-3">
                🔒 Smart OTP
              </label>
              <div class="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  bind:value={bankPassword}
                  placeholder="Nhập mật khẩu (demo: 123456)"
                  class="w-full bg-[#1a1a1a] border border-[#4a4a4a] text-white rounded-lg px-4 py-3 pr-12 focus:border-[#c4a574] focus:ring-2 focus:ring-[#c4a574]/50 focus:outline-none transition-all duration-300"
                  required
                />
                <button
                  type="button"
                  on:click={() => showPassword = !showPassword}
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#c4a574] transition-colors"
                >
                  {#if showPassword}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  {:else}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  {/if}
                </button>
              </div>
            </div>
            
            <!-- Error Message -->
            {#if error}
              <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg animate-slideInUp">
                ⚠️ {error}
              </div>
            {/if}
            
            <!-- Submit Button -->
            <button
              type="submit"
              disabled={purchasing}
              class="w-full bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-4 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {#if purchasing}
                <span class="flex items-center justify-center gap-2">
                  <div class="w-5 h-5 border-2 border-[#1a1a1a] border-t-transparent rounded-full animate-smoothSpin"></div>
                  Đang xử lý...
                </span>
              {:else}
                💳 Mua Vé Mới - 50,000đ
              {/if}
            </button>
          </form>
        </div>
      </div>
    {:else}
      <!-- Purchase Form -->
      <div class="animate-fadeIn">
        <h1 class="text-4xl font-bold text-[#c4a574] mb-4 text-center animate-slideInUp">
          🎫 Mua Vé Tham Quan
        </h1>
        <p class="text-gray-400 text-center mb-8 animate-slideInUp" style="animation-delay: 0.1s;">
          Bảo Tàng Chứng Tích Chiến Tranh
        </p>
        
        <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn" style="animation-delay: 0.2s;">
          <!-- Price Info -->
          <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-xl p-6 mb-8">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-400 text-sm mb-1">Giá Vé</p>
                <p class="text-[#c4a574] text-3xl font-bold">50,000đ</p>
                <p class="text-gray-500 text-sm mt-1">/ người lớn</p>
              </div>
              <div class="text-right">
                <div class="bg-[#c4a574] text-[#1a1a1a] px-4 py-2 rounded-full font-bold text-sm">
                  Vé Người Lớn
                </div>
              </div>
            </div>
          </div>
          
          <form on:submit|preventDefault={handlePurchase} class="space-y-6">
            <!-- Bank Account Selection -->
            <div>
              <label class="block text-gray-300 font-semibold mb-3">
                🏦 Chọn Tài Khoản Ngân Hàng
              </label>
              <select
                bind:value={selectedAccount}
                class="w-full bg-[#1a1a1a] border border-[#4a4a4a] text-white rounded-lg px-4 py-3 focus:border-[#c4a574] focus:ring-2 focus:ring-[#c4a574]/50 focus:outline-none transition-all duration-300"
                required
              >
                {#each bankAccounts as account}
                  <option value={account.account_number}>
                    {account.account_number} - {account.name} ({formatCurrency(account.balance)})
                  </option>
                {/each}
              </select>
              <p class="text-gray-500 text-sm mt-2">
                💡 Đây là tài khoản giả lập cho mục đích demo
              </p>
            </div>
            
            <!-- Bank Password -->
            <div>
              <label class="block text-gray-300 font-semibold mb-3">
                🔒 Mật Khẩu Ngân Hàng
              </label>
              <div class="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  bind:value={bankPassword}
                  placeholder="Nhập mật khẩu (demo: 123456)"
                  class="w-full bg-[#1a1a1a] border border-[#4a4a4a] text-white rounded-lg px-4 py-3 pr-12 focus:border-[#c4a574] focus:ring-2 focus:ring-[#c4a574]/50 focus:outline-none transition-all duration-300"
                  required
                />
                <button
                  type="button"
                  on:click={() => showPassword = !showPassword}
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#c4a574] transition-colors"
                >
                  {#if showPassword}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  {:else}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  {/if}
                </button>
              </div>
            </div>
            
            <!-- Error Message -->
            {#if error}
              <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg animate-slideInUp">
                ⚠️ {error}
              </div>
            {/if}
            
            <!-- Success Message -->
            {#if success}
              <div class="bg-green-500/20 border border-green-500 text-green-400 px-4 py-3 rounded-lg animate-slideInUp">
                ✅ {success}
              </div>
            {/if}
            
            <!-- Submit Button -->
            <button
              type="submit"
              disabled={purchasing}
              class="w-full bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-4 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {#if purchasing}
                <span class="flex items-center justify-center gap-2">
                  <div class="w-5 h-5 border-2 border-[#1a1a1a] border-t-transparent rounded-full animate-smoothSpin"></div>
                  Đang xử lý...
                </span>
              {:else}
                💳 Thanh Toán 50,000đ
              {/if}
            </button>
          </form>
          
          <!-- Info Box -->
          <div class="mt-6 bg-[#1a1a1a] border border-[#4a4a4a] rounded-lg p-4">
            <h3 class="text-[#c4a574] font-semibold mb-2 flex items-center gap-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              Thông Tin Demo
            </h3>
            <ul class="text-gray-400 text-sm space-y-1">
              <li>• Mật khẩu tất cả tài khoản: <span class="text-[#c4a574] font-mono">123456</span></li>
              <li>• Đây là hệ thống thanh toán giả lập</li>
              <li>• Số dư tài khoản chỉ lưu trong bộ nhớ tạm</li>
              <li>• Sau khi mua vé, bạn sẽ nhận được mã vé duy nhất</li>
            </ul>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

