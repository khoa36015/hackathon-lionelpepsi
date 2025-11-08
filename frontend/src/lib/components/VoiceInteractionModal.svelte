<script>
  import { onMount, onDestroy } from 'svelte';
  import Modal from './Modal.svelte';
  import { API_AI } from '$lib/api';

  export let show = false;
  export let itemName = '';
  export let onClose = () => {};

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

  // Voice selection
  let availableVoices = [];
  let selectedVoice = null;
  let selectedLanguage = 'vi-VN'; // Default to Vietnamese
  let showVoiceSettings = false;

  // FPT.AI TTS voices
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
  let useFptTts = true; // Use FPT.AI by default for Vietnamese

  // Initialize speech recognition and synthesis
  onMount(() => {
    if (typeof window !== 'undefined') {
      // Speech Recognition (Speech-to-Text)
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = selectedLanguage; // Use selected language
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {
          const speechResult = event.results[0][0].transcript;
          transcript = speechResult;
          console.log('Speech recognized:', speechResult, 'Language:', selectedLanguage);
          handleUserQuestion(speechResult);
        };

        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          errorMessage = `Không thể nhận diện giọng nói: ${event.error}. Vui lòng thử lại.`;
          state = 'error';
          isRecording = false;
        };

        recognition.onend = () => {
          isRecording = false;
          if (state === 'listening') {
            state = 'processing';
          }
        };
      } else {
        console.warn('Speech Recognition not supported');
        errorMessage = 'Trình duyệt không hỗ trợ nhận diện giọng nói.';
        state = 'error';
      }

      // Speech Synthesis (Text-to-Speech)
      synthesis = window.speechSynthesis;

      // Load available voices
      loadVoices();
      if (synthesis.onvoiceschanged !== undefined) {
        synthesis.onvoiceschanged = loadVoices;
      }
    }

    // Auto-play initial prompt when modal opens
    if (show) {
      playInitialPrompt();
    }
  });

  onDestroy(() => {
    stopSpeaking();
    if (recognition) {
      recognition.abort();
    }
  });

  // Watch for show prop changes
  $: if (show) {
    playInitialPrompt();
  } else {
    resetState();
  }

  function loadVoices() {
    if (!synthesis) return;

    availableVoices = synthesis.getVoices();
    console.log('Available voices:', availableVoices.length);

    // Try to find a Vietnamese voice
    const vietnameseVoice = availableVoices.find(voice =>
      voice.lang.startsWith('vi') || voice.lang.includes('VN')
    );

    if (vietnameseVoice && !selectedVoice) {
      selectedVoice = vietnameseVoice;
      console.log('Selected Vietnamese voice:', vietnameseVoice.name);
    } else if (!selectedVoice && availableVoices.length > 0) {
      // Fallback to first available voice
      selectedVoice = availableVoices[0];
    }
  }

  function playInitialPrompt() {
    // More natural greeting variations
    const greetings = [
      `Xin chào! Mình là trợ lý AI của bảo tàng. Bạn muốn tìm hiểu gì về ${itemName}?`,
      `Chào bạn! Bạn có câu hỏi nào về ${itemName} không?`,
      `Xin chào! Mình có thể giúp bạn tìm hiểu về ${itemName}. Bạn muốn biết điều gì?`,
      `Chào bạn! Đây là ${itemName}. Bạn muốn mình kể gì về nó?`
    ];
    const promptText = greetings[Math.floor(Math.random() * greetings.length)];
    speak(promptText, () => {
      // After prompt finishes, show options
      state = 'initial';
    });
  }

  async function speak(text, onEnd = null) {
    // Use FPT.AI TTS for Vietnamese
    if (useFptTts && selectedLanguage === 'vi-VN') {
      await speakWithFptAi(text, onEnd);
    } else {
      // Fallback to browser TTS
      speakWithBrowser(text, onEnd);
    }
  }

  async function speakWithFptAi(text, onEnd = null) {
    try {
      console.log('🎤 Using FPT.AI TTS with voice:', selectedFptVoice);
      console.log('📝 Text to speak:', text);
      console.log('📏 Text length:', text.length, 'characters');

      // Show loading indicator
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
        if (onEnd) onEnd();
      };

      audio.onerror = (error) => {
        console.error('❌ Audio playback error:', error);
        debugInfo = `❌ Lỗi phát audio`;
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
    if (!synthesis) return;

    stopSpeaking();

    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = selectedLanguage;

    // Use selected voice if available
    if (selectedVoice) {
      currentUtterance.voice = selectedVoice;
    }

    currentUtterance.rate = 1.0;
    currentUtterance.pitch = 1.0;
    currentUtterance.volume = 1.0;

    currentUtterance.onend = () => {
      if (onEnd) onEnd();
    };

    currentUtterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
    };

    console.log('Speaking with browser TTS, voice:', selectedVoice?.name || 'default', 'Language:', selectedLanguage);
    synthesis.speak(currentUtterance);
  }

  function stopSpeaking() {
    if (synthesis && synthesis.speaking) {
      synthesis.cancel();
    }
  }

  function startListening() {
    if (!recognition) {
      errorMessage = 'Trình duyệt không hỗ trợ nhận diện giọng nói.';
      state = 'error';
      return;
    }

    state = 'listening';
    isRecording = true;
    transcript = '';
    errorMessage = '';

    try {
      // Update recognition language before starting
      recognition.lang = selectedLanguage;
      console.log('Starting recognition with language:', selectedLanguage);
      recognition.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
      errorMessage = 'Không thể bắt đầu ghi âm. Vui lòng thử lại.';
      state = 'error';
      isRecording = false;
    }
  }

  function stopListening() {
    if (recognition && isRecording) {
      recognition.stop();
      isRecording = false;
    }
  }

  async function handleUserQuestion(question) {
    state = 'processing';

    try {
      const message = `${question} (Về ${itemName})`;

      console.log('Sending to AI:', { message, endpoint: `${API_AI}/ask` });

      const res = await fetch(`${API_AI}/ask`, {
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

  function handleClose() {
    stopSpeaking();
    stopListening();
    resetState();
    onClose();
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
    startListening();
  }

  function handleNo() {
    speak('Cảm ơn bạn!', () => {
      setTimeout(handleClose, 500);
    });
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
          <!-- Language Selection -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              🌐 Ngôn ngữ nhận diện
            </label>
            <select
              bind:value={selectedLanguage}
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="vi-VN">🇻🇳 Tiếng Việt (Vietnamese)</option>
              <option value="en-US">🇺🇸 English (US)</option>
              <option value="en-GB">🇬🇧 English (UK)</option>
              <option value="zh-CN">🇨🇳 中文 (Chinese)</option>
              <option value="ja-JP">🇯🇵 日本語 (Japanese)</option>
              <option value="ko-KR">🇰🇷 한국어 (Korean)</option>
              <option value="fr-FR">🇫🇷 Français (French)</option>
              <option value="de-DE">🇩🇪 Deutsch (German)</option>
              <option value="es-ES">🇪🇸 Español (Spanish)</option>
            </select>
          </div>

          <!-- FPT.AI Vietnamese Voice Selection -->
          {#if selectedLanguage === 'vi-VN'}
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                🎤 Giọng đọc tiếng Việt (FPT.AI)
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

            <!-- Test Voice Button -->
            <button
              class="w-full px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition text-sm font-medium"
              on:click={() => speak('Xin chào! Đây là giọng đọc tiếng Việt từ FPT.AI.')}
            >
              🔊 Nghe thử giọng đọc
            </button>
          {:else}
            <!-- Browser Voice Selection for other languages -->
            {#if availableVoices.length > 0}
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  🔊 Giọng đọc (Trình duyệt)
                </label>
                <select
                  bind:value={selectedVoice}
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {#each availableVoices as voice}
                    <option value={voice}>
                      {voice.name} ({voice.lang})
                    </option>
                  {/each}
                </select>
              </div>

              <!-- Test Voice Button -->
              <button
                class="w-full px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition text-sm font-medium"
                on:click={() => speak('Hello! This is a test voice.')}
              >
                🔊 Test voice
              </button>
            {/if}
          {/if}
        </div>
      {/if}
    </div>

    {#if state === 'initial'}
      <div class="text-center space-y-4">
        <p class="text-gray-600 mb-4 text-lg">
          💬 Bạn muốn hỏi gì về <span class="font-semibold text-indigo-600">{itemName}</span>?
        </p>
        <p class="text-sm text-gray-500 mb-4">
          Bạn có thể hỏi về lịch sử, đặc điểm, hoặc bất kỳ điều gì bạn tò mò!
        </p>
        <div class="flex gap-4 justify-center">
          <button
            on:click={handleYes}
            class="px-6 py-3 bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 transition-all duration-200 shadow-soft hover:shadow-fluffy"
          >
            🎤 Nói
          </button>
          <button
            on:click={toggleTextInput}
            class="px-6 py-3 bg-green-600 text-white rounded-full font-semibold hover:bg-green-700 transition-all duration-200"
          >
            ⌨️ Gõ
          </button>
          <button
            on:click={handleNo}
            class="px-6 py-3 bg-gray-200 text-gray-700 rounded-full font-semibold hover:bg-gray-300 transition-all duration-200"
          >
            Không
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

    {#if state === 'listening'}
      <div class="text-center space-y-4">
        <div class="relative inline-block">
          <div class="w-24 h-24 bg-red-500 rounded-full flex items-center justify-center animate-pulse">
            <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="absolute inset-0 w-24 h-24 bg-red-500 rounded-full animate-ping opacity-20"></div>
        </div>
        <p class="text-lg font-semibold text-gray-900">Đang lắng nghe...</p>
        <p class="text-sm text-gray-600">Hãy nói câu hỏi của bạn</p>
        <button
          on:click={stopListening}
          class="mt-4 px-6 py-2 bg-gray-200 text-gray-700 rounded-full font-semibold hover:bg-gray-300 transition"
        >
          Dừng
        </button>
      </div>
    {/if}

    {#if state === 'processing'}
      <div class="text-center space-y-4">
        <div class="w-16 h-16 mx-auto border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        <p class="text-lg font-semibold text-gray-900">Đang xử lý...</p>
        {#if transcript}
          <div class="mt-4 p-4 bg-gray-50 rounded-lg">
            <p class="text-sm text-gray-600 mb-1">Câu hỏi của bạn:</p>
            <p class="text-gray-900 font-medium">{transcript}</p>
          </div>
        {/if}
      </div>
    {/if}

    {#if state === 'speaking'}
      <div class="text-center space-y-4">
        <div class="w-24 h-24 mx-auto bg-green-500 rounded-full flex items-center justify-center animate-pulse">
          <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
          </svg>
        </div>
        <p class="text-lg font-semibold text-gray-900">Đang trả lời...</p>
        {#if aiResponse}
          <div class="mt-4 p-4 bg-green-50 rounded-lg text-left">
            <p class="text-sm text-gray-600 mb-2">Trả lời:</p>
            <p class="text-gray-900 leading-relaxed">{aiResponse}</p>
          </div>
        {/if}
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
          <p><strong>API Endpoint:</strong> {API_AI}/ask (Port 8000)</p>
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

