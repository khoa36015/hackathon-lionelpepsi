<script>
    import { onMount } from 'svelte';
    import { writable } from 'svelte/store';
    import Modal from '$lib/components/Modal.svelte';
    import AuthForm from '$lib/components/Auth.svelte';
    import { checkSession, logout } from '$lib/api';

    const username = writable(null);
    const isLoggedIn = writable(false);
    let showModal = false;
    let showMenu = false;
    let showAuthForm = false;

    onMount(async () => {
        try {
        const res = await checkSession();
        if (res.isLoggedIn) {
            session.set({ isLoggedIn: true, username: res.username });
            username.set(res.username);
            isLoggedIn.set(true);
        } else {
            session.set({ isLoggedIn: false, username: null });
            username.set(null);
            isLoggedIn.set(false);
        }
        } catch (err) {
        console.error('Chưa đăng nhập!');
        }
    });

    async function handleLogout() {
        await logout();
        username.set(null);
        isLoggedIn.set(false);
        location.reload();
    }
</script>

<div class="relative bg-white/50 bg-cover bg-center bg-no-repeat flex items-center justify-center">
  <!-- Lớp phủ nhẹ để tăng độ tương phản -->
  <div class="absolute inset-0 bg-black/20">
    <nav class="backdrop-blur-md bg-white/40 border-gray-200 shadow-sm transition-all duration-300 ease-in-out fixed top-0 left-0 w-full z-20">
      <div class="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
        
        <!-- Logo -->
        <a href="/" class="flex items-center gap-3 transition-all duration-300 ease-in-out">
          <img src="/images/logo.png" class="h-10 w-auto" alt="Logo" />
          <span class="text-2xl font-bold text-sky-800 tracking-wide">BẢO TÀNG CHỨNG TÍCH CHIẾN TRANH</span>
        </a>

        <!-- Toggle button -->
        <button
          on:click={() => showMenu = !showMenu}
          class="p-2 rounded-lg text-gray-600 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-sky-300 transition-all duration-300 ease-in-out cursor-pointer"
          aria-controls="navbar-default"
          aria-expanded={showMenu}
          aria-label="Show Menu"
        >
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

    

      <!-- Menu -->
      <div class={`transition-all duration-500 ease-in-out ${showMenu ? 'relative' : 'hidden'} `} id="navbar-default">
        <ul class="flex flex-col md:flex-col gap-3 md:gap-6 px-4 md:py-0 z-10 text-gray-800  border-b border-gray-200 font-medium justify-end md:items-end items-end">
          {#if $isLoggedIn}
            <li><span class="text-sm">Xin chào, <strong>{$username}</strong></span></li>
            <li><a on:click={handleLogout} href="/" class="block hover:text-red-500 transition duration-300">ĐĂNG XUẤT</a></li>
          {:else}
            <li><a href="/" 
              on:click={() => {showAuthForm = true; showMenu = false}} 
              class="block hover:text-sky-600 border-y border-gray-600 transition duration-300 md:px-3 md:mr-25">ĐĂNG KÝ</a></li>
          {/if}
          
        </ul>
      </div>
    </nav>

    


  <!-- Modal đăng ký -->
  <Modal show={showAuthForm} onClose={() => showAuthForm = false}>
    <AuthForm />
  </Modal>

  </div>
</div>