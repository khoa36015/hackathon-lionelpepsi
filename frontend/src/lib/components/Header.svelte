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

  // Fake nav items — thay bằng dữ liệu thực tế của Lead
  const navItems = [
    { title: 'Trang chủ', href: '/' },
    { title: 'Địa danh', href: '/places' },
    { title: 'Bộ sưu tập', href: '/gallery' },
    { title: 'Liên hệ', href: '/contact' }
  ];
</script>

<!-- Header sticky với blur nền, dark mode, shadow nhẹ -->
<header bind:this={headerRef} class="sticky top-0 z-40 bg-white/70 dark:bg-neutral-900/60 backdrop-blur supports-[backdrop-filter]:bg-white/50 border-b border-black/5 dark:border-white/10">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div class="flex h-16 items-center justify-between">
      <!-- Logo -->
      <div class="flex items-center gap-3">
        <button
          class="inline-flex items-center gap-2 rounded-xl px-2 py-1 focus:outline-none focus-visible:ring ring-offset-2 ring-neutral-300 dark:ring-neutral-600"
          on:click={() => navTo('/')}
          aria-label="Về trang chủ"
        >
          <!-- Placeholder Logo -->
          <div class="size-8 rounded-lg bg-linear-to-tr from-indigo-500 to-cyan-400"></div>
          <span class="text-base font-semibold tracking-tight select-none">AI TOUR GUI</span>
        </button>
      </div>

      <div class="">
         °C
      </div>

      <!-- Desktop Nav -->
      <nav class="md:flex items-center gap-1">
        {#each navItems as item}
          <button
            class="px-3 py-2 rounded-lg text-sm font-medium hover:bg-black/5 dark:hover:bg-white/10 transition"
            on:click={() => navTo(item.href)}
          >
            {item.title}
          </button>
        {/each}

        <!-- Divider -->
        <span class="mx-2 h-6 w-px bg-neutral-200 dark:bg-neutral-700" aria-hidden="true"></span>

        <!-- AI Agent Button -->
        <button
          class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg focus:outline-none focus-visible:ring-2 ring-offset-2 ring-indigo-500"
          on:click={() => aiAgentOpen = true}
          aria-label="Mở AI Agent"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span>AI Trợ Lý</span>
        </button>

        <!-- Divider -->
        <span class="mx-2 h-6 w-px bg-neutral-200 dark:bg-neutral-700" aria-hidden="true"></span>

        <!-- Account -->
        {#if $isLoggedIn}
          <div class="relative">
            <button
              bind:this={accountBtnRef}
              class="group inline-flex items-center gap-2 rounded-lg px-3 py-2 focus:outline-none focus-visible:ring ring-offset-2 ring-neutral-300 dark:ring-neutral-600 hover:bg-black/5 dark:hover:bg-white/10 transition"
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
                class="absolute right-0 mt-2 w-56 rounded-xl border border-black/5 dark:border-white/10 bg-white dark:bg-neutral-900 shadow-lg overflow-hidden"
              >
                <div class="p-1">
                  <a role="menuitem" tabindex="0" href="/dashboard"
                     class="block rounded-lg px-3 py-2 text-sm hover:bg-black/5 dark:hover:bg-white/10">Bảng điều khiển</a>
                  <a role="menuitem" tabindex="0" href="/profile"
                     class="block rounded-lg px-3 py-2 text-sm hover:bg-black/5 dark:hover:bg-white/10">Hồ sơ</a>
                  <button role="menuitem" class="w-full text-left rounded-lg px-3 py-2 text-sm hover:bg-black/5 dark:hover:bg-white/10"
                          on:click={handleLogout}>Đăng xuất</button>
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <div class="flex items-center gap-2">
            <button
              class="rounded-lg px-3 py-2 text-sm font-medium hover:bg-black/5 dark:hover:bg-white/10 transition focus:outline-none focus-visible:ring ring-offset-2 ring-neutral-300 dark:ring-neutral-600"
              on:click={() => authOpen = true}
            >
              Đăng ký
            </button>
          </div>
        {/if}
      </nav>

      <!-- Mobile toggles -->
      <div class="flex md:hidden items-center gap-2">

        <button
          class="inline-flex items-center justify-center rounded-lg p-2 hover:bg-black/5 dark:hover:bg-white/10 transition focus:outline-none focus-visible:ring ring-offset-2 ring-neutral-300 dark:ring-neutral-600"
          aria-label="Mở menu"
          aria-expanded={mobileOpen}
          aria-controls="mobile-menu"
          on:click={() => (mobileOpen = !mobileOpen)}
        >
          <svg class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 6h16M4 12h16M4 18h16"/>
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
      class="md:hidden border-t border-black/5 dark:border-white/10"
      transition:fade={{ duration: prefersReduced ? 0 : 150 }}
    >
      <div
        class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-3 space-y-1"
        transition:fly={{ y: prefersReduced ? 0 : 8, duration: prefersReduced ? 0 : 180 }}
      >
        {#each navItems as item}
          <button
            class="block w-full text-left rounded-lg px-3 py-2 text-sm font-medium hover:bg-black/5 dark:hover:bg-white/10 transition"
            on:click={() => navTo(item.href)}
          >
            {item.title}
          </button>
        {/each}

        <div class="h-px bg-neutral-200 dark:bg-neutral-700 my-2" aria-hidden="true"></div>

        <!-- AI Agent Button (Mobile) -->
        <button
          class="w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 shadow-md"
          on:click={() => { aiAgentOpen = true; mobileOpen = false; }}
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <span>AI Trợ Lý</span>
        </button>

        <div class="h-px bg-neutral-200 dark:bg-neutral-700 my-2" aria-hidden="true"></div>

        {#if $isLoggedIn}
          <div class="rounded-xl bg-black/2 dark:bg-white/4 p-2">
            <div class="flex items-center gap-2 px-2 py-1.5">
              <div class="size-7 rounded-full bg-linear-to-tr from-fuchsia-500 to-amber-400"></div>
              <div class="text-sm font-semibold">{$username}</div>
            </div>
            <div class="mt-1 grid grid-cols-2 gap-1">
              <button class="rounded-lg px-3 py-2 text-sm hover:bg-black/5 dark:hover:bg-white/10 transition" on:click={() => navTo('/dashboard')}>Bảng điều khiển</button>
              <button class="rounded-lg px-3 py-2 text-sm hover:bg-black/5 dark:hover:bg-white/10 transition" on:click={() => navTo('/profile')}>Hồ sơ</button>
              <button class="col-span-2 rounded-lg px-3 py-2 text-sm hover:bg-black/5 dark:hover:bg-white/10 transition" on:click={handleLogout}>Đăng xuất</button>
            </div>
          </div>
        {:else}
          <button class="w-full rounded-lg px-3 py-2 text-sm font-medium hover:bg-black/5 dark:hover:bg-white/10 transition" on:click={() => { authOpen = true; mobileOpen = false; }}>
            Đăng nhập / Đăng ký
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
  onClose={() => (aiAgentOpen = false)}
/>

<style>
  /* Giữ bóng nhẹ cho header, tránh đổ bóng quá đậm */
  header { box-shadow: 0 2px 10px 0 color(display-p3 0 0 0 / 0.02); }
</style>
