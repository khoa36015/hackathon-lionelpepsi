<script>
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { generateCheckinQR, submitQuiz } from '$lib/api';
  import { browser } from '$app/environment';

  export let show = false;
  export let locationName = '';
  export let onClose = () => {};

  let loading = false;
  let error = '';
  let success = '';

  // QR code data
  let qrImage = '';
  let qrData = '';
  let maVe = '';
  let timestamp = '';

  // Check-in data (after scan)
  let alreadyVisited = false;
  let checkinTime = '';
  let locationInfo = '';
  let quiz = [];
  let quizCompleted = false;
  let previousScore = 0;

  // Quiz state
  let currentStep = 'loading'; // 'loading' | 'show-qr' | 'info' | 'quiz' | 'result' | 'already-visited'
  let userAnswers = [];
  let quizResult = null;

  $: if (show && locationName) {
    handleGenerateQR();
  }

  async function handleGenerateQR() {
    if (!browser) return;

    loading = true;
    error = '';
    currentStep = 'loading';
    userAnswers = [];
    quizResult = null;

    try {
      const result = await generateCheckinQR(locationName);
      console.log('Generate QR result:', result);

      if (result.ok) {
        qrImage = result.qr_image;
        qrData = result.qr_data;
        maVe = result.ma_ve;
        timestamp = result.timestamp;
        currentStep = 'show-qr';
      } else {
        // Check if error is about login or ticket
        if (result.error && (result.error.includes('đăng nhập') || result.error.includes('mua vé'))) {
          error = result.error;
        } else {
          error = result.error || 'Có lỗi xảy ra';
        }
        currentStep = 'error';
      }
    } catch (err) {
      console.error('Generate QR error:', err);
      error = `Không thể kết nối với server: ${err.message}`;
      currentStep = 'error';
    } finally {
      loading = false;
    }
  }

  function startQuiz() {
    currentStep = 'quiz';
  }

  function selectAnswer(questionIndex, optionIndex) {
    userAnswers[questionIndex] = optionIndex;
    userAnswers = [...userAnswers]; // Trigger reactivity
  }

  async function handleSubmitQuiz() {
    // Check all questions answered
    if (userAnswers.includes(-1)) {
      error = 'Vui lòng trả lời tất cả câu hỏi';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      const correctAnswers = quiz.map(q => q.correct);
      const result = await submitQuiz(locationName, userAnswers, correctAnswers);
      
      if (result.ok) {
        quizResult = result;
        currentStep = 'result';
      } else {
        error = result.error || 'Có lỗi xảy ra';
      }
    } catch (err) {
      error = 'Không thể gửi câu trả lời';
    } finally {
      loading = false;
    }
  }

  function handleClose() {
    show = false;
    onClose();
  }
</script>

{#if show}
  <div 
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fadeIn"
    on:click={handleClose}
    transition:fade={{ duration: 300 }}
  >
    <div 
      class="bg-gradient-to-br from-[#3a3a3a] to-[#2a2a2a] rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl border border-[#4a4a4a] animate-scaleIn"
      on:click|stopPropagation
      transition:scale={{ duration: 300, start: 0.95 }}
    >
      <!-- Header -->
      <div class="sticky top-0 bg-[#2a2a2a] border-b border-[#4a4a4a] p-6 flex items-center justify-between z-10">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-[#c4a574] rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-[#1a1a1a]" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-bold text-[#c4a574]">Check-in Địa Điểm</h2>
            <p class="text-sm text-gray-400">{locationName}</p>
          </div>
        </div>
        <button
          on:click={handleClose}
          class="text-gray-400 hover:text-white transition-colors p-2 hover:bg-[#3a3a3a] rounded-lg"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        {#if currentStep === 'loading'}
          <div class="flex flex-col items-center justify-center py-12">
            <div class="w-16 h-16 border-4 border-[#c4a574] border-t-transparent rounded-full animate-smoothSpin mb-4"></div>
            <p class="text-gray-300">Đang check-in...</p>
          </div>
        
        {:else if currentStep === 'error'}
          <div class="space-y-4">
            <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
               {error}
            </div>

            <div class="text-center">
              {#if error.includes('đăng nhập')}
                <p class="text-gray-400 mb-4">Bạn cần đăng nhập để sử dụng tính năng check-in</p>
              {:else if error.includes('mua vé')}
                <p class="text-gray-400 mb-4">Bạn cần mua vé trước khi check-in</p>
              {/if}
              <button
                on:click={handleClose}
                class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-6 py-3 rounded-lg transition-all duration-300 transform hover:scale-105"
              >
                Đóng
              </button>
            </div>
          </div>

        {:else if currentStep === 'show-qr'}
          <div class="text-center py-8 space-y-6 animate-fadeIn">
            <div>
              <h3 class="text-2xl font-bold text-white mb-2">Mã QR Check-in</h3>
              <p class="text-gray-400">Vui lòng đưa mã QR này cho nhân viên để check-in</p>
            </div>

            <!-- QR Code Image -->
            <div class="bg-white rounded-xl p-6 inline-block mx-auto">
              <img src={qrImage} alt="QR Code" class="w-64 h-64" />
            </div>

            <!-- Ticket Info -->
            <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a] max-w-md mx-auto">
              <div class="grid grid-cols-2 gap-4 text-left">
                <div>
                  <p class="text-gray-400 text-sm">Mã Vé</p>
                  <p class="text-[#c4a574] font-semibold">{maVe}</p>
                </div>
                <div>
                  <p class="text-gray-400 text-sm">Địa Điểm</p>
                  <p class="text-white font-semibold">{locationName}</p>
                </div>
                <div class="col-span-2">
                  <p class="text-gray-400 text-sm">Thời Gian Tạo</p>
                  <p class="text-gray-300 text-sm">{timestamp}</p>
                </div>
              </div>
            </div>

            <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4">
              <p class="text-gray-300 text-sm">
                💡 Sau khi nhân viên quét mã, bạn sẽ nhận được thông tin về địa điểm và quiz để nhận điểm thưởng!
              </p>
            </div>

            <button
              on:click={handleClose}
              class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-8 py-3 rounded-lg transition-all duration-300 transform hover:scale-105"
            >
              Đóng
            </button>
          </div>

        {:else if currentStep === 'already-visited'}
          <div class="text-center py-8">
            <div class="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-12 h-12 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-white mb-2">Đã Check-in Trước Đó</h3>
            <p class="text-gray-400 mb-4">Bạn đã ghé thăm địa điểm này vào {checkinTime}</p>
            
            {#if quizCompleted}
              <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4 inline-block">
                <p class="text-gray-300 mb-1">Điểm Quiz</p>
                <p class="text-3xl font-bold text-[#c4a574]">{previousScore}/100</p>
              </div>
            {:else}
              <p class="text-gray-500">Bạn chưa hoàn thành quiz cho địa điểm này</p>
            {/if}
          </div>
        
        {:else if currentStep === 'info'}
          <div class="space-y-6 animate-fadeIn">
            <div class="bg-[#1a1a1a] rounded-xl p-6 border border-[#4a4a4a]">
              <div class="flex items-center gap-2 mb-3">
                <svg class="w-5 h-5 text-[#c4a574]" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <h3 class="text-lg font-semibold text-[#c4a574]">Thông Tin Địa Điểm</h3>
              </div>
              <p class="text-gray-300 leading-relaxed">{locationInfo}</p>
            </div>
            
            <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4">
              <p class="text-gray-300 text-sm">
                 Check-in thành công lúc <span class="font-semibold text-[#c4a574]">{checkinTime}</span>
              </p>
            </div>
            
            <button
              on:click={startQuiz}
              class="w-full bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-4 rounded-lg transition-all duration-300 transform hover:scale-105"
            >
               Bắt Đầu Quiz
            </button>
          </div>
        
        {:else if currentStep === 'quiz'}
          <div class="space-y-6 animate-fadeIn">
            <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4 mb-6">
              <p class="text-gray-300 text-sm text-center">
                 Trả lời đúng để nhận điểm thưởng!
              </p>
            </div>
            
            {#each quiz as question, qIndex}
              <div class="bg-[#1a1a1a] rounded-xl p-6 border border-[#4a4a4a]">
                <h4 class="text-white font-semibold mb-4">
                  Câu {qIndex + 1}: {question.question}
                </h4>
                
                <div class="space-y-3">
                  {#each question.options as option, oIndex}
                    <button
                      on:click={() => selectAnswer(qIndex, oIndex)}
                      class="w-full text-left px-4 py-3 rounded-lg border transition-all duration-300 {
                        userAnswers[qIndex] === oIndex
                          ? 'bg-[#c4a574] border-[#c4a574] text-[#1a1a1a] font-semibold'
                          : 'bg-[#2a2a2a] border-[#4a4a4a] text-gray-300 hover:border-[#c4a574] hover:bg-[#3a3a3a]'
                      }"
                    >
                      <span class="font-mono mr-2">{String.fromCharCode(65 + oIndex)}.</span>
                      {option}
                    </button>
                  {/each}
                </div>
              </div>
            {/each}
            
            {#if error}
              <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
                 {error}
              </div>
            {/if}
            
            <button
              on:click={handleSubmitQuiz}
              disabled={loading}
              class="w-full bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold py-4 rounded-lg transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {#if loading}
                <span class="flex items-center justify-center gap-2">
                  <div class="w-5 h-5 border-2 border-[#1a1a1a] border-t-transparent rounded-full animate-smoothSpin"></div>
                  Đang xử lý...
                </span>
              {:else}
                 Nộp Bài
              {/if}
            </button>
          </div>
        
        {:else if currentStep === 'result'}
          <div class="text-center py-8 space-y-6 animate-fadeIn">
            <div class="w-24 h-24 bg-[#c4a574]/20 rounded-full flex items-center justify-center mx-auto">
              <span class="text-5xl">
                {#if quizResult.score === 100}
                  🎉
                {:else if quizResult.score >= 66}
                  👍
                {:else if quizResult.score >= 33}
                  💪
                {:else}
                  📚
                {/if}
              </span>
            </div>
            
            <div>
              <h3 class="text-3xl font-bold text-white mb-2">Kết Quả Quiz</h3>
              <p class="text-gray-400">{quizResult.feedback}</p>
            </div>
            
            <div class="grid grid-cols-2 gap-4 max-w-md mx-auto">
              <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
                <p class="text-gray-400 text-sm mb-1">Điểm Số</p>
                <p class="text-3xl font-bold text-[#c4a574]">{quizResult.score}/100</p>
              </div>
              
              <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
                <p class="text-gray-400 text-sm mb-1">Trả Lời Đúng</p>
                <p class="text-3xl font-bold text-green-400">{quizResult.correct_count}/{quizResult.total_questions}</p>
              </div>
              
              <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
                <p class="text-gray-400 text-sm mb-1">Điểm Thưởng</p>
                <p class="text-3xl font-bold text-yellow-400">+{quizResult.points_earned}</p>
              </div>
              
              <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
                <p class="text-gray-400 text-sm mb-1">Tổng Điểm</p>
                <p class="text-3xl font-bold text-[#c4a574]">{quizResult.total_points}</p>
              </div>
            </div>
            
            <div class="bg-[#c4a574]/10 border border-[#c4a574]/30 rounded-lg p-4">
              <p class="text-gray-300 text-sm">
                💡 Điểm thưởng có thể dùng để giảm giá vé lần sau!
              </p>
            </div>
            
            <button
              on:click={handleClose}
              class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-8 py-3 rounded-lg transition-all duration-300 transform hover:scale-105"
            >
              Đóng
            </button>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

