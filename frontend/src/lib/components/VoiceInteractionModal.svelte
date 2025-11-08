<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import Modal from './Modal.svelte';
  import { API_AI } from '$lib/api';

  export let show = false;
  export let itemName = '';
  export let onClose = () => {};
  export let isGeneralAgent = false; // New prop: true = general AI, false = museum AI

  let state = 'initial'; // 'initial', 'listening', 'processing', 'speaking', 'error'
  let transcript = '';
  let aiResponse = '';
  let errorMessage = '';
  let isRecording = false;
  let textInput = '';
  let showTextInput = false;
  let debugInfo = ''; // Debug information display

  // Web Speech API
  let recognition = null;
  let synthesis = null;
  let currentUtterance = null;

  // Vietnamese-only voice settings
  let showVoiceSettings = false;

  // FPT.AI TTS voices (Vietnamese only)
  let fptVoices = [
    { code: 'banmai', name: 'Nữ Bắc (Ban Mai)', gender: 'female', region: 'north' },
    { code: 'lannhi', name: 'Nữ Nam (Lan Nhi)', gender: 'female', region: 'south' },
    { code: 'leminh', name: 'Nam Bắc (Lê Minh)', gender: 'male', region: 'north' },
    { code: 'myan', name: 'Nữ Trung (Mỹ An)', gender: 'female', region: 'central' },
    { code: 'thuminh', name: 'Nữ Bắc (Thu Minh)', gender: 'female', region: 'north' },
    { code: 'giahuy', name: 'Nam Trung (Gia Huy)', gender: 'male', region: 'central' },
    { code: 'linhsan', name: 'Nữ Nam (Linh San)', gender: 'female', region: 'south' }
  ];
  let selectedFptVoice = 'banmai'; // Default voice

  // Browser TTS fallback (Vietnamese only)
  let availableVietnameseVoices = [];
  let selectedBrowserVoice = null;

  // Initialize speech recognition and synthesis (Vietnamese only)
  onMount(() => {
    // Only initialize in browser
    if (!browser) return;

    if (typeof window !== 'undefined') {
      // Speech Recognition (Speech-to-Text) - Vietnamese only
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'vi-VN'; // Always Vietnamese
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {
          const speechResult = event.results[0][0].transcript;
          transcript = speechResult;
          console.log('✅ Nhận diện thành công:', speechResult);
          debugInfo = `✅ Đã nghe: "${speechResult}"`;
          handleUserQuestion(speechResult);
        };

        recognition.onerror = (event) => {
          console.error('❌ Lỗi nhận diện giọng nói:', event.error);

          // Handle specific errors
          let errorMsg = 'Không thể nhận diện giọng nói. ';
          if (event.error === 'not-allowed' || event.error === 'permission-denied') {
            errorMsg = 'Vui lòng cho phép truy cập microphone trong trình duyệt.';
          } else if (event.error === 'no-speech') {
            errorMsg = 'Không nghe thấy giọng nói. Vui lòng thử lại.';
          } else if (event.error === 'network') {
            errorMsg = 'Lỗi kết nối mạng. Vui lòng kiểm tra internet.';
          } else {
            errorMsg += `Lỗi: ${event.error}`;
          }

          errorMessage = errorMsg;
          debugInfo = `❌ ${errorMsg}`;
          state = 'error';
          isRecording = false;
        };

        recognition.onend = () => {
          console.log('🎤 Kết thúc ghi âm');
          isRecording = false;
          if (state === 'listening') {
            state = 'processing';
            debugInfo = '⏳ Đang xử lý...';
          }
        };
      } else {
        console.warn('⚠️ Trình duyệt không hỗ trợ nhận diện giọng nói');
        errorMessage = 'Trình duyệt không hỗ trợ nhận diện giọng nói.';
        state = 'error';
      }

      // Speech Synthesis (Text-to-Speech) - Load Vietnamese voices only
      synthesis = window.speechSynthesis;
      loadVietnameseVoices();
      if (synthesis.onvoiceschanged !== undefined) {
        synthesis.onvoiceschanged = loadVietnameseVoices;
      }
    }

    // Don't auto-play - let user control when to start
  });

  onDestroy(() => {
    stopSpeaking();
    if (recognition) {
      recognition.abort();
    }
  });

  // Watch for show prop changes - only reset state, don't auto-play
  $: if (!show) {
    resetState();
  }

  function loadVietnameseVoices() {
    if (!browser || !synthesis) return;

    const allVoices = synthesis.getVoices();

    // Filter for Vietnamese voices only
    availableVietnameseVoices = allVoices.filter(voice =>
      voice.lang.startsWith('vi') || voice.lang.includes('VN')
    );

    console.log('🇻🇳 Giọng tiếng Việt có sẵn:', availableVietnameseVoices.length);

    // Select first Vietnamese voice as default
    if (availableVietnameseVoices.length > 0 && !selectedBrowserVoice) {
      selectedBrowserVoice = availableVietnameseVoices[0];
      console.log('✅ Chọn giọng:', selectedBrowserVoice.name);
    }
  }

  function playInitialPrompt() {
    // Only run in browser
    if (!browser) return;

    // Different greetings for general vs museum agent
    let greetings;

    if (isGeneralAgent) {
      // General AI greetings - can answer anything
      greetings = [
        `Xin chào! Mình là AI Trợ Lý Thông Minh. Bạn có thể hỏi mình bất cứ điều gì!`,
        `Chào bạn! Mình có thể giúp bạn về nhiều chủ đề: học tập, công việc, đời sống. Bạn cần gì?`,
        `Xin chào! Mình sẵn sàng trả lời mọi câu hỏi của bạn. Hãy hỏi mình nhé!`,
        `Chào bạn! Mình là trợ lý AI đa năng. Bạn muốn tìm hiểu về điều gì?`
      ];
    } else {
      // Museum AI greetings - focused on museum items
      greetings = [
        `Xin chào! Mình là trợ lý AI của bảo tàng. Bạn muốn tìm hiểu gì về ${itemName}?`,
        `Chào bạn! Bạn có câu hỏi nào về ${itemName} không?`,
        `Xin chào! Mình có thể giúp bạn tìm hiểu về ${itemName}. Bạn muốn biết điều gì?`,
        `Chào bạn! Đây là ${itemName}. Bạn muốn mình kể gì về nó?`
      ];
    }

    const promptText = greetings[Math.floor(Math.random() * greetings.length)];

    // Set state to speaking first
    state = 'speaking';

    speak(promptText, () => {
      // After prompt finishes, automatically start listening
      startListening();
    });
  }

  async function speak(text, onEnd = null) {
    // Always try FPT.AI first for Vietnamese
    try {
      await speakWithFptAi(text, onEnd);
    } catch (error) {
      console.error('❌ FPT.AI failed, using browser TTS:', error);
      speakWithBrowser(text, onEnd);
    }
  }

  async function speakWithFptAi(text, onEnd = null) {
    // Only run in browser
    if (!browser) return;

    try {
      console.log('🎤 Using FPT.AI TTS with voice:', selectedFptVoice);
      console.log('📝 Text to speak:', text);
      console.log('📏 Text length:', text.length, 'characters');

      // Set state to speaking
      state = 'speaking';
      debugInfo = `⏳ Đang tạo giọng đọc từ FPT.AI...`;

      // Check text length (FPT.AI limit is 5000 chars)
      if (text.length > 5000) {
        console.warn('⚠️ Text too long, truncating to 5000 chars');
        text = text.substring(0, 5000);
      }

      // Try backend endpoint first
      try {
        console.log('🔄 Trying backend TTS endpoint...');
        const backendResponse = await fetch(`${API_AI}/tts`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: text,
            voice: selectedFptVoice,
            speed: 0
          })
        });

        console.log('📡 Backend TTS Response status:', backendResponse.status);

        if (backendResponse.ok) {
          const backendData = await backendResponse.json();
          console.log('📦 Backend TTS Response data:', backendData);

          if (backendData.success && backendData.audio_url) {
            const audioUrl = backendData.audio_url;
            console.log('✅ Got audio URL from backend:', audioUrl);
            await playAudioFromUrl(audioUrl, onEnd);
            return;
          }
        }

        console.warn('⚠️ Backend TTS failed, trying direct FPT.AI call...');
      } catch (backendError) {
        console.warn('⚠️ Backend TTS error:', backendError.message);
        console.log('🔄 Falling back to direct FPT.AI call...');
      }

      // Fallback: Call FPT.AI directly
      const response = await fetch('https://api.fpt.ai/hmi/tts/v5', {
        method: 'POST',
        headers: {
          'api_key': '8OuJvLUvBBfqok7MkamxBelt4yb3JHWF',
          'voice': selectedFptVoice,
          'speed': '0'
        },
        body: text
      });

      console.log('📡 FPT.AI Direct Response status:', response.status);

      if (!response.ok) {
        console.error('❌ FPT.AI TTS failed with status:', response.status);
        const errorText = await response.text();
        console.error('❌ Error response:', errorText);
        debugInfo = `❌ FPT.AI lỗi, chuyển sang giọng trình duyệt`;
        speakWithBrowser(text, onEnd);
        return;
      }

      const data = await response.json();
      console.log('📦 FPT.AI Direct Response data:', data);

      if (data.error === 0 && data.async) {
        const audioUrl = data.async;
        console.log('✅ FPT.AI audio URL:', audioUrl);
        await playAudioFromUrl(audioUrl, onEnd);
      } else {
        console.error('❌ FPT.AI TTS returned error:', data);
        debugInfo = `❌ FPT.AI error: ${data.message || 'Unknown error'}`;
        speakWithBrowser(text, onEnd);
      }

    } catch (error) {
      console.error('❌ Error calling FPT.AI TTS:', error);
      console.error('❌ Error details:', error.message, error.stack);
      debugInfo = `❌ Lỗi kết nối FPT.AI: ${error.message}`;
      speakWithBrowser(text, onEnd);
    }
  }

  async function playAudioFromUrl(audioUrl, onEnd = null) {
    try {
      // Show loading indicator
      debugInfo = `⏳ Đang tải audio từ FPT.AI...`;

      // Wait for audio to be ready with retry logic
      const isReady = await waitForAudioReady(audioUrl, 8000); // Wait up to 8 seconds

      if (!isReady) {
        console.warn('⚠️ Audio not ready after 8 seconds, trying to play anyway...');
      }

      // Play audio from URL
      const audio = new Audio(audioUrl);

      audio.onloadeddata = () => {
        console.log('✅ Audio loaded successfully');
        debugInfo = `🔊 Đang phát giọng đọc...`;
      };

      audio.onended = () => {
        console.log('✅ Audio playback ended');
        debugInfo = `✅ Hoàn thành`;
        state = 'initial'; // Reset to initial state when done
        if (onEnd) onEnd();
      };

      audio.onerror = (error) => {
        console.error('❌ Audio playback error:', error);
        debugInfo = `❌ Lỗi phát audio`;
        state = 'initial'; // Reset to initial state on error
        throw new Error('Audio playback failed');
      };

      // Try to play
      await audio.play();
      console.log('🔊 Audio playing...');

    } catch (err) {
      console.error('❌ Failed to play audio:', err);
      debugInfo = `❌ Không thể phát audio: ${err.message}`;
      throw err; // Re-throw to trigger fallback
    }
  }

  async function waitForAudioReady(url, maxWait = 5000) {
    const startTime = Date.now();
    const checkInterval = 500; // Check every 500ms

    while (Date.now() - startTime < maxWait) {
      try {
        const response = await fetch(url, { method: 'HEAD' });
        if (response.ok) {
          console.log('✅ Audio file is ready');
          return true;
        }
      } catch (e) {
        // Ignore errors, keep trying
      }

      // Wait before next check
      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    console.log('⚠️ Audio file not ready after', maxWait, 'ms, trying anyway...');
    return false;
  }

  function speakWithBrowser(text, onEnd = null) {
    // Only run in browser
    if (!browser) return;

    if (!synthesis) {
      console.error('❌ Browser TTS không khả dụng');
      if (onEnd) onEnd();
      return;
    }

    // MUST have Vietnamese voice - no fallback to English
    if (availableVietnameseVoices.length === 0) {
      console.error('❌ Không có giọng tiếng Việt trong trình duyệt');
      debugInfo = '❌ Không có giọng tiếng Việt';
      if (onEnd) onEnd();
      return;
    }

    stopSpeaking();

    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = 'vi-VN'; // Always Vietnamese

    // ONLY use Vietnamese voices - NO English fallback
    if (selectedBrowserVoice && selectedBrowserVoice.lang.startsWith('vi')) {
      currentUtterance.voice = selectedBrowserVoice;
      console.log('🔊 Sử dụng giọng đã chọn:', selectedBrowserVoice.name);
    } else {
      // Force use first Vietnamese voice
      currentUtterance.voice = availableVietnameseVoices[0];
      selectedBrowserVoice = availableVietnameseVoices[0];
      console.log('🔊 Sử dụng giọng tiếng Việt:', availableVietnameseVoices[0].name);
    }

    currentUtterance.rate = 0.9; // Slightly slower for better clarity
    currentUtterance.pitch = 1.0;
    currentUtterance.volume = 1.0;

    currentUtterance.onend = () => {
      console.log('✅ Browser TTS hoàn thành');
      debugInfo = '✅ Hoàn thành';
      state = 'initial'; // Reset to initial state when done speaking
      if (onEnd) onEnd();
    };

    currentUtterance.onerror = (event) => {
      console.error('❌ Lỗi Browser TTS:', event);
      debugInfo = `❌ Lỗi phát giọng: ${event.error}`;
      state = 'initial'; // Reset to initial state on error
      if (onEnd) onEnd();
    };

    state = 'speaking'; // Set state to speaking
    debugInfo = '🔊 Đang phát giọng đọc (trình duyệt)...';
    synthesis.speak(currentUtterance);
  }

  function stopSpeaking() {
    // Only run in browser
    if (!browser) return;

    // Stop browser TTS
    if (synthesis && synthesis.speaking) {
      synthesis.cancel();
    }

    // Stop any audio playback (FPT.AI)
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });

    // Reset state
    if (state === 'speaking') {
      state = 'initial';
      debugInfo = '⏹️ Đã dừng giọng đọc';
      console.log('⏹️ Stopped speaking');
    }
  }

  async function checkMicrophonePermission() {
    // Only run in browser
    if (!browser) return false;

    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Stop the stream immediately after getting permission
      stream.getTracks().forEach(track => track.stop());
      console.log('✅ Microphone permission granted');
      return true;
    } catch (error) {
      console.error('❌ Microphone permission denied:', error);
      errorMessage = 'Vui lòng cho phép truy cập microphone để sử dụng tính năng này.';
      debugInfo = '❌ Không có quyền truy cập microphone';
      state = 'error';
      return false;
    }
  }

  async function startListening() {
    // Only run in browser
    if (!browser) return;

    if (!recognition) {
      errorMessage = 'Trình duyệt không hỗ trợ nhận diện giọng nói.';
      state = 'error';
      return;
    }

    // Check microphone permission first
    const hasPermission = await checkMicrophonePermission();
    if (!hasPermission) {
      return;
    }

    // Stop any ongoing speech first
    stopSpeaking();

    state = 'listening';
    isRecording = true;
    transcript = '';
    errorMessage = '';
    debugInfo = '🎤 Đang lắng nghe... Hãy nói câu hỏi của bạn';

    try {
      // Always use Vietnamese
      recognition.lang = 'vi-VN';
      console.log('🎤 Bắt đầu ghi âm tiếng Việt...');
      recognition.start();
    } catch (error) {
      console.error('❌ Lỗi bắt đầu ghi âm:', error);

      // Handle "already started" error
      if (error.message && error.message.includes('already started')) {
        console.log('⚠️ Recognition already running, stopping and restarting...');
        recognition.stop();
        setTimeout(() => {
          try {
            recognition.start();
          } catch (retryError) {
            console.error('❌ Retry failed:', retryError);
            errorMessage = 'Không thể bắt đầu ghi âm. Vui lòng thử lại.';
            state = 'error';
            isRecording = false;
            debugInfo = '❌ Lỗi ghi âm';
          }
        }, 100);
      } else {
        errorMessage = `Không thể bắt đầu ghi âm: ${error.message}`;
        state = 'error';
        isRecording = false;
        debugInfo = `❌ Lỗi: ${error.message}`;
      }
    }
  }

  function stopListening() {
    // Only run in browser
    if (!browser) return;

    if (recognition && isRecording) {
      recognition.stop();
      isRecording = false;
    }
  }

  async function handleUserQuestion(question) {
    state = 'processing';

    try {
      // Choose endpoint based on agent type
      const endpoint = isGeneralAgent ? `${API_AI}/ask-general` : `${API_AI}/ask`;

      // For general agent, send question as-is. For museum agent, add context
      const message = isGeneralAgent ? question : `${question} (Về ${itemName})`;

      console.log('Sending to AI:', {
        message,
        endpoint,
        mode: isGeneralAgent ? 'general' : 'museum'
      });

      const res = await fetch(endpoint, {
        method: 'POST',
        // Don't send credentials to AI API (different port, no auth needed)
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      console.log('AI Response status:', res.status, res.statusText);

      if (!res.ok) {
        const errorText = await res.text();
        console.error('AI API error response:', errorText);
        throw new Error(`Không thể kết nối với AI (${res.status})`);
      }

      const data = await res.json();
      console.log('AI Response data:', data);

      // Handle different response formats
      let responseText = '';
      if (data.response) {
        responseText = data.response;
      } else if (data.message) {
        responseText = data.message;
      } else if (data.answer) {
        responseText = data.answer;
      } else if (data.text) {
        responseText = data.text;
      } else if (data.result) {
        responseText = data.result;
      } else if (typeof data === 'string') {
        responseText = data;
      } else {
        console.warn('Unexpected AI response format:', data);
        responseText = 'Xin lỗi, tôi không có thông tin về điều này.';
      }

      aiResponse = responseText;

      if (!aiResponse || aiResponse.trim() === '') {
        console.error('Empty AI response');
        throw new Error('AI trả về phản hồi rỗng');
      }

      console.log('Speaking AI response:', aiResponse);

      state = 'speaking';
      speak(aiResponse, () => {
        // After AI finishes speaking, return to initial state
        state = 'initial';
      });

    } catch (error) {
      console.error('Error querying AI:', error);
      errorMessage = `Không thể truy vấn AI: ${error.message}`;
      state = 'error';
    }
  }

  function resetState() {
    state = 'initial';
    transcript = '';
    aiResponse = '';
    errorMessage = '';
    isRecording = false;
    stopSpeaking();
    if (recognition && isRecording) {
      recognition.abort();
    }
  }

  function handleYes() {
    // Play greeting first, then start listening
    playInitialPrompt();
  }

  function handleNo() {
    // Don't allow closing while speaking or listening
    if (state === 'speaking' || state === 'listening') {
      debugInfo = '⚠️ Vui lòng đợi hoàn thành';
      return;
    }

    speak('Cảm ơn bạn!', () => {
      setTimeout(handleClose, 500);
    });
  }

  function handleClose() {
    // Don't allow closing while speaking or listening
    if (state === 'speaking' || state === 'listening') {
      debugInfo = '⚠️ Vui lòng đợi AI nói xong hoặc dừng ghi âm';
      return;
    }

    stopSpeaking();
    resetState();
    onClose();
  }

  function toggleTextInput() {
    showTextInput = !showTextInput;
  }

  function handleTextSubmit() {
    if (textInput.trim()) {
      transcript = textInput;
      handleUserQuestion(textInput);
      textInput = '';
      showTextInput = false;
    }
  }
</script>

<Modal {show} onClose={handleClose}>
  <div class="voice-interaction-modal">
    <h2 class="text-2xl font-bold text-gray-900 mb-4 text-center">
      🎤 Trợ lý giọng nói
    </h2>

    <div class="mb-4 text-center">
      <p class="text-lg text-gray-700 mb-2">
        <strong>{itemName}</strong>
      </p>
    </div>

    <!-- Voice Settings -->
    <div class="mb-4 border-b border-gray-200 pb-4">
      <button
        class="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2 mx-auto"
        on:click={() => showVoiceSettings = !showVoiceSettings}
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
        {showVoiceSettings ? 'Ẩn' : 'Cài đặt'} giọng nói
      </button>

      {#if showVoiceSettings}
        <div class="mt-4 space-y-3 bg-gray-50 p-4 rounded-lg">
          <!-- Vietnamese Voice Selection (FPT.AI) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              🎤 Chọn giọng đọc tiếng Việt
            </label>
            <select
              bind:value={selectedFptVoice}
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {#each fptVoices as voice}
                <option value={voice.code}>
                  {voice.name}
                </option>
              {/each}
            </select>
            <p class="text-xs text-gray-500 mt-1">
              ✨ Giọng đọc tự nhiên từ FPT.AI
            </p>
          </div>

          <!-- Browser Vietnamese Voice Fallback -->
          {#if availableVietnameseVoices.length > 0}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                🔊 Giọng dự phòng (Trình duyệt)
              </label>
              <select
                bind:value={selectedBrowserVoice}
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {#each availableVietnameseVoices as voice}
                  <option value={voice}>
                    {voice.name}
                  </option>
                {/each}
              </select>
              <p class="text-xs text-gray-500 mt-1">
                Sử dụng khi FPT.AI không khả dụng
              </p>
            </div>
          {/if}

          <!-- Test Voice Button -->
          <button
            class="w-full px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition text-sm font-medium"
            on:click={() => speak('Xin chào! Đây là giọng đọc tiếng Việt từ FPT.AI.')}
          >
            🔊 Nghe thử giọng đọc
          </button>
        </div>
      {/if}
    </div>

    {#if state === 'initial'}
      <div class="text-center space-y-4 animate-fadeIn">
        <p class="text-gray-600 mb-4 text-lg animate-slideInUp">
          💬 Bạn muốn hỏi gì về <span class="font-semibold text-indigo-600">{itemName}</span>?
        </p>
        <p class="text-sm text-gray-500 mb-4 animate-slideInUp" style="animation-delay: 0.1s;">
          Bạn có thể hỏi về lịch sử, đặc điểm, hoặc bất kỳ điều gì bạn tò mò!
        </p>
        <div class="flex gap-4 justify-center">
          <button
            on:click={handleYes}
            class="px-6 py-3 bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 hover:shadow-lg transform hover:scale-105 transition-all duration-300 shadow-smooth animate-slideInUp"
            style="animation-delay: 0.2s;"
          >
            🎤 Nói
          </button>
          <button
            on:click={toggleTextInput}
            class="px-6 py-3 bg-green-600 text-white rounded-full font-semibold hover:bg-green-700 hover:shadow-lg transform hover:scale-105 transition-all duration-300 animate-slideInUp"
            style="animation-delay: 0.25s;"
          >
            ⌨️ Gõ
          </button>
          <button
            on:click={handleNo}
            disabled={state === 'speaking' || state === 'listening'}
            class="px-6 py-3 bg-gray-200 text-gray-700 rounded-full font-semibold hover:bg-gray-300 hover:shadow-md transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none animate-slideInUp"
            style="animation-delay: 0.3s;"
          >
            Không
          </button>
        </div>

        {#if showTextInput}
          <div class="mt-6 space-y-3 animate-scaleIn">
            <input
              type="text"
              bind:value={textInput}
              placeholder="Nhập câu hỏi của bạn..."
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none transition-all duration-300"
              on:keypress={(e) => e.key === 'Enter' && handleTextSubmit()}
            />
            <button
              on:click={handleTextSubmit}
              disabled={!textInput.trim()}
              class="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 hover:shadow-lg transform hover:scale-105 transition-all duration-300 disabled:bg-gray-300 disabled:cursor-not-allowed disabled:transform-none"
            >
              Gửi câu hỏi
            </button>
          </div>
        {/if}
      </div>
    {/if}

    {#if state === 'listening'}
      <div class="text-center space-y-4 animate-fadeIn">
        <div class="relative inline-block">
          <div class="w-24 h-24 bg-red-500 rounded-full flex items-center justify-center animate-smoothPulse shadow-lg">
            <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="absolute inset-0 w-24 h-24 bg-red-500 rounded-full animate-ping opacity-20"></div>
          <div class="absolute inset-0 w-24 h-24 bg-red-400 rounded-full animate-ping opacity-10" style="animation-delay: 0.5s;"></div>
        </div>
        <p class="text-lg font-semibold text-gray-900 animate-slideInUp">🎤 Đang lắng nghe...</p>
        <p class="text-sm text-gray-600 animate-slideInUp" style="animation-delay: 0.1s;">Hãy nói câu hỏi của bạn</p>
        <p class="text-xs text-yellow-600 font-medium animate-slideInUp" style="animation-delay: 0.2s;">⚠️ Không thể đóng khi đang ghi âm</p>
        <button
          on:click={stopListening}
          class="mt-4 px-6 py-3 bg-red-600 text-white rounded-full font-semibold hover:bg-red-700 hover:shadow-lg transform hover:scale-105 transition-all duration-300 animate-slideInUp"
          style="animation-delay: 0.3s;"
        >
          ⏹️ Dừng ghi âm
        </button>
      </div>
    {/if}

    {#if state === 'processing'}
      <div class="text-center space-y-4 animate-fadeIn">
        <div class="w-16 h-16 mx-auto border-4 border-indigo-600 border-t-transparent rounded-full animate-smoothSpin shadow-lg"></div>
        <p class="text-lg font-semibold text-gray-900 animate-slideInUp">Đang xử lý...</p>
        {#if transcript}
          <div class="mt-4 p-4 bg-gray-50 rounded-lg animate-scaleIn shadow-smooth">
            <p class="text-sm text-gray-600 mb-1">Câu hỏi của bạn:</p>
            <p class="text-gray-900 font-medium">{transcript}</p>
          </div>
        {/if}
      </div>
    {/if}

    {#if state === 'speaking'}
      <div class="text-center space-y-4 animate-fadeIn">
        <div class="w-24 h-24 mx-auto bg-green-500 rounded-full flex items-center justify-center animate-smoothPulse shadow-lg">
          <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
          </svg>
        </div>
        <p class="text-lg font-semibold text-gray-900 animate-slideInUp">🔊 Đang phát giọng đọc...</p>
        <p class="text-sm text-gray-500 animate-slideInUp" style="animation-delay: 0.1s;">Vui lòng đợi AI nói xong</p>
        {#if aiResponse}
          <div class="mt-4 p-4 bg-green-50 rounded-lg text-left animate-scaleIn shadow-smooth">
            <p class="text-sm text-gray-600 mb-2">Trả lời:</p>
            <p class="text-gray-900 leading-relaxed">{aiResponse}</p>
          </div>
        {/if}
        <!-- Stop button -->
        <button
          on:click={stopSpeaking}
          class="mt-4 px-6 py-3 bg-red-600 text-white rounded-full font-semibold hover:bg-red-700 hover:shadow-lg transform hover:scale-105 transition-all duration-300 animate-slideInUp"
          style="animation-delay: 0.2s;"
        >
          ⏹️ Dừng giọng đọc
        </button>
      </div>
    {/if}

    {#if state === 'error'}
      <div class="text-center space-y-4">
        <div class="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="text-lg font-semibold text-red-600">Lỗi</p>
        <p class="text-gray-700">{errorMessage}</p>
        <div class="flex gap-3 justify-center">
          <button
            on:click={() => state = 'initial'}
            class="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 transition"
          >
            Thử lại
          </button>
          <button
            on:click={toggleTextInput}
            class="mt-4 px-6 py-2 bg-green-600 text-white rounded-full font-semibold hover:bg-green-700 transition"
          >
            Gõ câu hỏi
          </button>
        </div>
        {#if showTextInput}
          <div class="mt-6 space-y-3">
            <input
              type="text"
              bind:value={textInput}
              placeholder="Nhập câu hỏi của bạn..."
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none"
              on:keypress={(e) => e.key === 'Enter' && handleTextSubmit()}
            />
            <button
              on:click={handleTextSubmit}
              disabled={!textInput.trim()}
              class="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Gửi câu hỏi
            </button>
          </div>
        {/if}
      </div>
    {/if}

    <!-- Debug Info -->
    <div class="mt-6 pt-4 border-t border-gray-200">
      <details class="text-xs text-gray-500">
        <summary class="cursor-pointer hover:text-gray-700 font-medium">🔍 Debug Info</summary>
        <div class="mt-2 space-y-1 text-left bg-gray-50 p-3 rounded">
          <p><strong>State:</strong> {state}</p>
          <p><strong>Mode:</strong> {isGeneralAgent ? '🌐 General AI (Tất cả câu hỏi)' : '🏛️ Museum AI (Bảo tàng)'}</p>
          <p><strong>API Endpoint:</strong> {isGeneralAgent ? `${API_AI}/ask-general` : `${API_AI}/ask`} (Port 8000)</p>
          {#if transcript}
            <p><strong>Transcript:</strong> {transcript}</p>
          {/if}
          {#if aiResponse}
            <p><strong>AI Response:</strong> {aiResponse.substring(0, 100)}...</p>
          {/if}
          {#if errorMessage}
            <p class="text-red-600"><strong>Error:</strong> {errorMessage}</p>
          {/if}
          <p class="text-xs text-gray-400 mt-2">Kiểm tra Console (F12) để xem log chi tiết</p>
        </div>
      </details>
    </div>
  </div>
</Modal>

<style>
  .voice-interaction-modal {
    min-height: 300px;
    display: flex;
    flex-direction: column;
  }

  .shadow-soft {
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
  }
  
  .shadow-fluffy {
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.08), 0 8px 10px -6px rgb(0 0 0 / 0.08);
  }
</style>

