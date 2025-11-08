<script>
  import { onMount, tick } from 'svelte';
  import { writable, get } from 'svelte/store';
  import { fade, fly, scale } from 'svelte/transition';
  import { goto } from '$app/navigation';

  // Giữ nguyên API/Component theo project hiện có
  import Modal from '$lib/components/Modal.svelte';
  import AuthForm from '$lib/components/Auth.svelte';
  import VoiceInteractionModal from '$lib/components/VoiceInteractionModal.svelte';
  import { checkSession, logout } from '$lib/api';

  // State đăng nhập
  const username = writable(null);
  const isLoggedIn = writable(false);

  // UI state
  let mobileOpen = false;      // mở menu mobile
  let accountOpen = false;     // mở dropdown tài khoản
  let authOpen = false;        // mở modal đăng nhập/đăng ký
  let aiAgentOpen = false;     // mở modal AI agent

  // refs để đóng khi click outside
  let accountBtnRef;
  let accountMenuRef;
  let mobileMenuRef;
  let headerRef;

  // Mount: kiểm tra phiên
  onMount(async () => {
    try {
      const res = await checkSession();
      if (res && res.username) {
        username.set(res.username);
        isLoggedIn.set(true);
      } else {
        username.set(null);
        isLoggedIn.set(false);
      }
    } catch (e) {
      console.error('checkSession error:', e);
      username.set(null);
      isLoggedIn.set(false);
    }

    // Lắng nghe click outside
    const onDocClick = (e) => {
      if (accountOpen) {
        const isInsideBtn = accountBtnRef?.contains(e.target);
        const isInsideMenu = accountMenuRef?.contains(e.target);
        if (!isInsideBtn && !isInsideMenu) accountOpen = false;
      }
      if (mobileOpen) {
        const isInsideMobile = mobileMenuRef?.contains(e.target);
        const isInsideHeader = headerRef?.contains(e.target);
        if (!isInsideMobile && !isInsideHeader) mobileOpen = false;
      }
    };

    const onKey = (e) => {
      if (e.key === 'Escape') {
        accountOpen = false;
        mobileOpen = false;
        authOpen = false;
      }
    };

    document.addEventListener('click', onDocClick, true);
    document.addEventListener('keydown', onKey);

    return () => {
      document.removeEventListener('click', onDocClick, true);
      document.removeEventListener('keydown', onKey);
    };
  });

  // Đăng xuất
  async function handleLogout() {
    try {
      await logout();
    } catch (e) {
      console.error('logout error:', e);
    } finally {
      username.set(null);
      isLoggedIn.set(false);
      accountOpen = false;
      goto('/'); // tuỳ chỉnh route sau logout
    }
  }

  // Điều hướng an toàn cho button
  function navTo(path) {
    goto(path);
    mobileOpen = false;
  }

  // Giảm chuyển động nếu user chọn "reduced motion"
  const prefersReduced =
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Kết hợp fade + scale thành một transition để tránh lỗi "multiple transition directives"
  function fadeScale(node, params) {
    const f = fade(node, params);
    const s = scale(node, params);
    return {
      delay: Math.max(f.delay || 0, s.delay || 0),
      duration: Math.max(f.duration || 0, s.duration || 0),
      css: (t, u) => {
        const a = f.css ? f.css(t, u) : '';
        const b = s.css ? s.css(t, u) : '';
        return [a, b].filter(Boolean).join('; ');
      }
    };
  }

  // Navigation items
  const navItems = [
    { title: 'Trang chủ', href: '/' },
    { title: 'Lộ Trình', href: '/tours' },
    { title: 'Feedback', href: '/feedback' }
  ];
</script>

<!-- Header - Dark theme inspired by War Remnants Museum -->
<header bind:this={headerRef} class="sticky top-0 z-50 bg-[#2a2a2a] border-b border-[#3a3a3a] backdrop-blur-lg bg-opacity-95 transition-all duration-300">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div class="flex h-20 items-center justify-between animate-fadeIn">
      <!-- Logo & Title -->
      <div class="flex items-center gap-4">
        <button
          class="flex items-center gap-3 focus:outline-none focus-visible:ring-2 ring-[#c4a574] rounded-lg px-2 py-1"
          on:click={() => navTo('/')}
          aria-label="Về trang chủ"
        >
          <!-- Museum Icon -->
          <div class="w-10 h-10 flex items-center justify-center">
            <svg class="w-8 h-8 text-[#c4a574]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3L2 9v2h20V9L12 3zm0 2.84L18.16 9H5.84L12 5.84zM4 11v9h3v-6h10v6h3v-9H4zm5 9v-4h6v4H9z"/>
            </svg>
          </div>
          <!-- Title -->
          <div class="flex flex-col items-start">
            <span class="text-[#c4a574] text-xs font-medium tracking-wider uppercase">Bảo Tàng</span>
            <span class="text-white text-sm font-bold tracking-wide uppercase" style="font-family: 'Arial', sans-serif; letter-spacing: 0.05em;">Chứng Tích Chiến Tranh</span>
          </div>
        </button>
      </div>

      <!-- Desktop Nav -->
      <nav class="hidden md:flex items-center gap-1">
        {#each navItems as item}
          <button
            class="px-4 py-2 text-sm font-medium text-[#c4a574] hover:text-white hover:bg-[#3a3a3a] rounded transition-all duration-300 uppercase tracking-wide transform hover:scale-105"
            on:click={() => navTo(item.href)}
          >
            {item.title}
          </button>
        {/each}

        <!-- Divider -->
        <span class="mx-2 h-6 w-px bg-[#4a4a4a]" aria-hidden="true"></span>

        <!-- Mua Vé Button -->
        <button
          class="px-5 py-2 bg-[#c4a574] text-[#1a1a1a] text-sm font-bold uppercase tracking-wide hover:bg-[#d4b584] hover:shadow-lg transform hover:scale-105 transition-all duration-300 rounded"
          on:click={() => navTo('/tickets')}
        >
          Mua Vé
        </button>

        <!-- Divider -->
        <span class="mx-2 h-6 w-px bg-[#4a4a4a]" aria-hidden="true"></span>

        <!-- AI Agent Button -->
        <button
          class="inline-flex items-center gap-2 px-4 py-2 bg-[#6b4fa0] text-white text-sm font-medium uppercase tracking-wide hover:bg-[#7b5fb0] hover:shadow-lg transform hover:scale-105 transition-all duration-300 rounded"
          on:click={() => aiAgentOpen = true}
          aria-label="Mở AI Agent"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span>AI Trợ Lý</span>
        </button>

        <!-- Divider -->
        <span class="mx-2 h-6 w-px bg-[#4a4a4a]" aria-hidden="true"></span>

        <!-- Account -->
        {#if $isLoggedIn}
          <div class="relative">
            <button
              bind:this={accountBtnRef}
              class="group inline-flex items-center gap-2 px-3 py-2 text-[#c4a574] hover:text-white transition-colors duration-200 focus:outline-none focus-visible:ring-2 ring-[#c4a574] rounded"
              aria-haspopup="menu"
              aria-expanded={accountOpen}
              on:click={() => (accountOpen = !accountOpen)}
            >
              <span class="text-sm font-medium">{$username}</span>
              <svg class="size-4 opacity-70 group-hover:opacity-100 transition" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 10.94l3.71-3.71a.75.75 0 1 1 1.06 1.06l-4.24 4.24a.75.75 0 0 1-1.06 0L5.25 8.29a.75.75 0 0 1-.02-1.08z" clip-rule="evenodd"/>
              </svg>
            </button>

            {#if accountOpen}
              <div
                bind:this={accountMenuRef}
                id="account-menu"
                role="menu"
                aria-label="Menu tài khoản"
                transition:fade|local={{ start: 0.98, duration: prefersReduced ? 0 : 120 }}
                class="absolute right-0 mt-2 w-56 rounded-lg border border-[#3a3a3a] bg-[#2a2a2a] shadow-xl overflow-hidden"
              >
                <div class="p-1">
                  <a role="menuitem" tabindex="0" href="/profile"
                     class="block rounded px-3 py-2 text-sm text-[#c4a574] hover:bg-[#3a3a3a] hover:text-white transition">Hồ sơ</a>
                  <button role="menuitem" class="w-full text-left rounded px-3 py-2 text-sm text-[#c4a574] hover:bg-[#3a3a3a] hover:text-white transition"
                          on:click={handleLogout}>Đăng xuất</button>
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <div class="flex items-center gap-2">
            <button
              class="px-4 py-2 text-sm font-medium text-[#c4a574] hover:text-white transition-colors duration-200 uppercase tracking-wide focus:outline-none focus-visible:ring-2 ring-[#c4a574] rounded"
              on:click={() => authOpen = true}
            >
              Đăng nhập
            </button>
          </div>
        {/if}
      </nav>

      <!-- Mobile toggles -->
      <div class="flex md:hidden items-center gap-2">
        <button
          class="inline-flex items-center justify-center p-2 text-[#c4a574] hover:text-white transition-colors duration-200 focus:outline-none focus-visible:ring-2 ring-[#c4a574] rounded"
          aria-label="Mở menu"
          aria-expanded={mobileOpen}
          aria-controls="mobile-menu"
          on:click={() => (mobileOpen = !mobileOpen)}
        >
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile panel -->
  {#if mobileOpen}
    <div
      bind:this={mobileMenuRef}
      id="mobile-menu"
      class="md:hidden border-t border-[#3a3a3a] bg-[#2a2a2a]"
      transition:fade={{ duration: prefersReduced ? 0 : 150 }}
    >
      <div
        class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4 space-y-2"
        transition:fly={{ y: prefersReduced ? 0 : 8, duration: prefersReduced ? 0 : 180 }}
      >
        {#each navItems as item}
          <button
            class="block w-full text-left px-4 py-2 text-sm font-medium text-[#c4a574] hover:text-white hover:bg-[#3a3a3a] transition-colors duration-200 rounded uppercase tracking-wide"
            on:click={() => navTo(item.href)}
          >
            {item.title}
          </button>
        {/each}

        <div class="h-px bg-[#3a3a3a] my-2" aria-hidden="true"></div>

        <!-- Mua Vé Button (Mobile) -->
        <button
          class="w-full px-4 py-2 bg-[#c4a574] text-[#1a1a1a] text-sm font-bold uppercase tracking-wide hover:bg-[#d4b584] transition-colors duration-200 rounded"
          on:click={() => { navTo('/tickets'); mobileOpen = false; }}
        >
          Mua Vé
        </button>

        <!-- AI Agent Button (Mobile) -->
        <button
          class="w-full flex items-center justify-center gap-2 px-4 py-2 bg-[#6b4fa0] text-white text-sm font-medium uppercase tracking-wide hover:bg-[#7b5fb0] transition-colors duration-200 rounded"
          on:click={() => { aiAgentOpen = true; mobileOpen = false; }}
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span>AI Trợ Lý</span>
        </button>

        <div class="h-px bg-[#3a3a3a] my-2" aria-hidden="true"></div>

        {#if $isLoggedIn}
          <div class="rounded-lg bg-[#3a3a3a] p-3">
            <div class="flex items-center gap-3 px-2 py-2">
              <div class="w-8 h-8 rounded-full bg-[#c4a574] flex items-center justify-center">
                <span class="text-[#1a1a1a] font-bold text-sm">{$username.charAt(0).toUpperCase()}</span>
              </div>
              <div class="text-sm font-semibold text-white">{$username}</div>
            </div>
            <div class="mt-2 space-y-1">
              <button class="w-full text-left rounded px-3 py-2 text-sm text-[#c4a574] hover:bg-[#4a4a4a] hover:text-white transition" on:click={() => navTo('/profile')}>Hồ sơ</button>
              <button class="w-full text-left rounded px-3 py-2 text-sm text-[#c4a574] hover:bg-[#4a4a4a] hover:text-white transition" on:click={handleLogout}>Đăng xuất</button>
            </div>
          </div>
        {:else}
          <button class="w-full px-4 py-2 text-sm font-medium text-[#c4a574] hover:text-white hover:bg-[#3a3a3a] transition-colors duration-200 rounded uppercase tracking-wide" on:click={() => { authOpen = true; mobileOpen = false; }}>
            Đăng nhập
          </button>
        {/if}
      </div>
    </div>
  {/if}
</header>

<!-- Modal Đăng nhập/Đăng ký -->
<Modal show={authOpen} onClose={() => (authOpen = false)}>
  <AuthForm />
</Modal>

<!-- Modal AI Agent -->
<VoiceInteractionModal
  show={aiAgentOpen}
  itemName="AI Trợ Lý Thông Minh"
  isGeneralAgent={true}
  onClose={() => (aiAgentOpen = false)}
/>

<style>
  /* War Remnants Museum inspired header styling */
  header {
    box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.3);
    font-family: 'Arial', 'Helvetica', sans-serif;
  }

  /* Custom scrollbar for dark theme */
  :global(body) {
    scrollbar-width: thin;
    scrollbar-color: #c4a574 #2a2a2a;
  }

  :global(body::-webkit-scrollbar) {
    width: 8px;
  }

  :global(body::-webkit-scrollbar-track) {
    background: #2a2a2a;
  }

  :global(body::-webkit-scrollbar-thumb) {
    background: #c4a574;
    border-radius: 4px;
  }

  :global(body::-webkit-scrollbar-thumb:hover) {
    background: #d4b584;
  }
</style>
