<script>
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { checkSession, submitFeedback, getFeedbackHistory } from '$lib/api';

  let isLoggedIn = false;
  let username = '';
  let loading = true;
  
  // Feedback form
  let rating = 0;
  let comment = '';
  let category = 'general';
  let submitting = false;
  let error = '';
  let success = '';
  
  // Feedback history
  let feedbackHistory = [];
  let loadingHistory = false;
  
  // Categories
  const categories = [
    { value: 'general', label: 'Chung', icon: '💬' },
    { value: 'exhibition', label: 'Triển Lãm', icon: '🖼️' },
    { value: 'service', label: 'Dịch Vụ', icon: '🤝' },
    { value: 'facility', label: 'Cơ Sở Vật Chất', icon: '🏛️' },
    { value: 'staff', label: 'Nhân Viên', icon: '👥' }
  ];

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
    
    // Load feedback history
    await loadHistory();
    
    loading = false;
  });

  async function loadHistory() {
    loadingHistory = true;
    try {
      const result = await getFeedbackHistory();
      if (result.ok) {
        feedbackHistory = result.feedbacks || [];
      }
    } catch (err) {
      console.error('Failed to load feedback history:', err);
    } finally {
      loadingHistory = false;
    }
  }

  async function handleSubmit() {
    if (rating === 0) {
      error = 'Vui lòng chọn đánh giá';
      return;
    }
    
    if (!comment.trim()) {
      error = 'Vui lòng nhập nhận xét';
      return;
    }
    
    error = '';
    success = '';
    submitting = true;
    
    try {
      const result = await submitFeedback(rating, comment, category);
      
      if (result.ok) {
        success = result.message || 'Cảm ơn bạn đã gửi feedback!';
        // Reset form
        rating = 0;
        comment = '';
        category = 'general';
        // Reload history
        await loadHistory();
        
        // Clear success message after 3s
        setTimeout(() => {
          success = '';
        }, 3000);
      } else {
        error = result.error || 'Có lỗi xảy ra';
      }
    } catch (err) {
      console.error('Submit feedback error:', err);
      error = 'Không thể kết nối với server';
    } finally {
      submitting = false;
    }
  }

  function getCategoryLabel(value) {
    const cat = categories.find(c => c.value === value);
    return cat ? `${cat.icon} ${cat.label}` : value;
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<svelte:head>
  <title>Feedback - Bảo Tàng Chứng Tích Chiến Tranh</title>
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
    <div class="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 animate-slideDown">
          📝 Feedback
        </h1>
        <p class="text-gray-400 text-lg animate-slideDown" style="animation-delay: 0.1s;">
          Chia sẻ trải nghiệm của bạn với chúng tôi
        </p>
      </div>

      <!-- Feedback Form -->
      <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn" style="animation-delay: 0.2s;">
        <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <span class="text-3xl"></span>
          Gửi Feedback Mới
        </h2>

        {#if error}
          <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-6 animate-shake">
            ⚠️ {error}
          </div>
        {/if}

        {#if success}
          <div class="bg-green-500/20 border border-green-500 text-green-400 px-4 py-3 rounded-lg mb-6 animate-slideDown">
            ✅ {success}
          </div>
        {/if}

        <form on:submit|preventDefault={handleSubmit} class="space-y-6">
          <!-- Rating -->
          <div>
            <label class="block text-gray-300 font-semibold mb-3">
              Đánh Giá <span class="text-red-400">*</span>
            </label>
            <div class="flex gap-2">
              {#each [1, 2, 3, 4, 5] as star}
                <button
                  type="button"
                  on:click={() => rating = star}
                  class="text-4xl transition-all duration-200 transform hover:scale-110 focus:outline-none focus-visible:ring-2 ring-[#c4a574] rounded"
                  aria-label="{star} sao"
                >
                  {#if rating >= star}
                    <span class="text-yellow-400">⭐</span>
                  {:else}
                    <span class="text-gray-600">⭐</span>
                  {/if}
                </button>
              {/each}
              {#if rating > 0}
                <span class="ml-3 text-[#c4a574] font-semibold self-center">
                  {rating}/5
                </span>
              {/if}
            </div>
          </div>

          <!-- Category -->
          <div>
            <label class="block text-gray-300 font-semibold mb-3">
              Danh Mục
            </label>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
              {#each categories as cat}
                <button
                  type="button"
                  on:click={() => category = cat.value}
                  class="px-4 py-3 rounded-lg border-2 transition-all duration-200 transform hover:scale-105 focus:outline-none focus-visible:ring-2 ring-[#c4a574]
                    {category === cat.value 
                      ? 'bg-[#c4a574] border-[#c4a574] text-[#1a1a1a] font-bold' 
                      : 'bg-[#2a2a2a] border-[#4a4a4a] text-gray-300 hover:border-[#c4a574]'}"
                >
                  <div class="text-2xl mb-1">{cat.icon}</div>
                  <div class="text-sm">{cat.label}</div>
                </button>
              {/each}
            </div>
          </div>

          <!-- Comment -->
          <div>
            <label class="block text-gray-300 font-semibold mb-3">
              Nhận Xét <span class="text-red-400">*</span>
            </label>
            <textarea
              bind:value={comment}
              rows="6"
              placeholder="Chia sẻ trải nghiệm của bạn..."
              class="w-full px-4 py-3 bg-[#1a1a1a] border-2 border-[#4a4a4a] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#c4a574] transition-colors duration-200"
              required
            ></textarea>
            <p class="text-gray-500 text-sm mt-2">
              {comment.length} ký tự
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            disabled={submitting}
            class="w-full bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-4 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-3"
          >
            {#if submitting}
              <div class="w-5 h-5 border-2 border-[#1a1a1a] border-t-transparent rounded-full animate-spin"></div>
              <span>Đang gửi...</span>
            {:else}
      
              <span>Gửi Feedback</span>
            {/if}
          </button>
        </form>
      </div>

      <!-- Feedback History -->
      <div class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl p-8 shadow-2xl border border-[#4a4a4a] animate-scaleIn" style="animation-delay: 0.3s;">
        <h2 class="text-2xl font-bold text-white mb-6 flex items-center gap-3">
          <span class="text-3xl">📋</span>
          Lịch Sử Feedback
        </h2>

        {#if loadingHistory}
          <div class="text-center py-8">
            <div class="w-12 h-12 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p class="text-gray-400">Đang tải...</p>
          </div>
        {:else if feedbackHistory.length === 0}
          <div class="text-center py-12">
            <div class="text-6xl mb-4">📭</div>
            <p class="text-gray-400 text-lg">Bạn chưa có feedback nào</p>
          </div>
        {:else}
          <div class="space-y-4">
            {#each feedbackHistory as fb, i}
              <div 
                class="bg-[#1a1a1a] rounded-xl p-6 border border-[#4a4a4a] hover:border-[#c4a574] transition-all duration-300 animate-slideUp"
                style="animation-delay: {i * 0.05}s;"
                transition:fly={{ y: 20, duration: 300, delay: i * 50 }}
              >
                <div class="flex items-start justify-between mb-3">
                  <div class="flex items-center gap-3">
                    <div class="flex">
                      {#each Array(5) as _, idx}
                        <span class="text-xl">
                          {#if idx < fb.rating}
                            ⭐
                          {:else}
                            <span class="text-gray-600">⭐</span>
                          {/if}
                        </span>
                      {/each}
                    </div>
                    <span class="text-[#c4a574] font-semibold">{fb.rating}/5</span>
                  </div>
                  <span class="text-sm text-gray-500">{getCategoryLabel(fb.category)}</span>
                </div>
                
                <p class="text-gray-300 mb-3 leading-relaxed">{fb.comment}</p>
                
                <div class="text-sm text-gray-500">
                  {formatDate(fb.created_at)}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
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
</style>

