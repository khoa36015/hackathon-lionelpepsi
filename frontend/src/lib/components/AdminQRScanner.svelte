<script>
  import { fade } from 'svelte/transition';
  import { scanCheckinQR } from '$lib/api';
  import { browser } from '$app/environment';

  export let show = false;
  export let locationName = '';
  export let onClose = () => {};

  let loading = false;
  let error = '';
  let success = '';
  let scanning = false;
  let videoElement = null;
  let stream = null;
  let qrCodeReader = null;
  let manualQRInput = '';

  // Scan result
  let scanResult = null;

  $: if (show && browser) {
    if (show) {
      // Component opened
    } else {
      stopScanning();
    }
  }

  async function startScanning() {
    if (!browser) return;

    error = '';
    loading = true;
    
    // Set scanning to true first so the element gets rendered in DOM
    scanning = true;
    
    // Wait a bit for Svelte to render the element
    await new Promise(resolve => setTimeout(resolve, 100));

    try {
      // Wait for html5-qrcode library to load
      let Html5QrcodeLib = null;
      let attempts = 0;
      const maxAttempts = 15; // Increase wait time

      while (!Html5QrcodeLib && attempts < maxAttempts) {
        if (typeof window !== 'undefined' && window.Html5Qrcode) {
          Html5QrcodeLib = window.Html5Qrcode;
          console.log('✅ Html5Qrcode library found');
          break;
        }
        // Wait 200ms before checking again
        await new Promise(resolve => setTimeout(resolve, 200));
        attempts++;
      }

      if (!Html5QrcodeLib) {
        scanning = false;
        throw new Error('Thư viện quét QR chưa được tải. Vui lòng refresh trang hoặc sử dụng chức năng nhập thủ công.');
      }

      // Use html5-qrcode library (it handles camera internally)
      // Wait for element to be rendered (Svelte needs time to render)
      let qrReaderElement = document.getElementById("qr-reader");
      let elementAttempts = 0;
      while (!qrReaderElement && elementAttempts < 20) {
        await new Promise(resolve => setTimeout(resolve, 50));
        qrReaderElement = document.getElementById("qr-reader");
        elementAttempts++;
      }

      if (!qrReaderElement) {
        scanning = false;
        throw new Error('Không tìm thấy phần tử quét QR. Vui lòng refresh trang và thử lại.');
      }

      qrCodeReader = new Html5QrcodeLib("qr-reader");
      
      // Try to start with back camera first, fallback to any camera
      try {
        await qrCodeReader.start(
          { facingMode: 'environment' },
          {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1.0
          },
          onQRCodeScanned,
          (errorMessage) => {
            // Ignore scanning errors (just log them)
            if (errorMessage && !errorMessage.includes('No QR code') && !errorMessage.includes('NotFoundException')) {
              console.log('QR scanning info:', errorMessage);
            }
          }
        );
        scanning = true;
        error = '';
        console.log('✅ Camera started successfully');
      } catch (camError) {
        // Try with any available camera
        console.log('Back camera failed, trying any camera...', camError);
        try {
          await qrCodeReader.start(
            { facingMode: 'user' },
            {
              fps: 10,
              qrbox: { width: 250, height: 250 },
              aspectRatio: 1.0
            },
            onQRCodeScanned,
            (errorMessage) => {
              if (errorMessage && !errorMessage.includes('No QR code') && !errorMessage.includes('NotFoundException')) {
                console.log('QR scanning info:', errorMessage);
              }
            }
          );
          scanning = true;
          error = '';
          console.log('✅ Camera started with front camera');
        } catch (fallbackError) {
          throw new Error(`Không thể truy cập camera: ${fallbackError.message || 'Lỗi không xác định'}`);
        }
      }
    } catch (err) {
      console.error('Camera error:', err);
      error = err.message || 'Không thể truy cập camera. Vui lòng sử dụng chức năng nhập thủ công bên dưới.';
      scanning = false;
      
      // Clean up if qrCodeReader was created but failed to start
      if (qrCodeReader) {
        try {
          await qrCodeReader.stop();
        } catch (stopErr) {
          console.log('Error stopping reader:', stopErr);
        }
        qrCodeReader = null;
      }
    } finally {
      loading = false;
    }
  }

  async function onQRCodeScanned(decodedText, decodedResult) {
    if (loading) return; // Prevent multiple scans

    loading = true;
    error = '';
    success = '';

    try {
      const result = await scanCheckinQR(decodedText);
      
      if (result.ok) {
        scanResult = result;
        success = result.message;
        stopScanning();
      } else {
        error = result.error || 'Có lỗi xảy ra khi quét QR code';
      }
    } catch (err) {
      console.error('Scan QR error:', err);
      error = 'Không thể kết nối với server';
    } finally {
      loading = false;
    }
  }

  async function handleManualInput() {
    const qrData = manualQRInput.trim();

    if (!qrData) {
      error = 'Vui lòng nhập hoặc dán dữ liệu QR code';
      return;
    }

    if (loading) {
      console.log('Already processing, please wait...');
      return;
    }

    loading = true;
    error = '';
    success = '';

    console.log('Processing manual QR input:', qrData);

    try {
      const result = await scanCheckinQR(qrData);
      console.log('Scan result:', result);
      
      if (result.ok) {
        scanResult = result;
        success = result.message;
        stopScanning();
      } else {
        error = result.error || 'Có lỗi xảy ra khi quét QR code';
        console.error('Scan failed:', result.error);
      }
    } catch (err) {
      console.error('Scan QR error:', err);
      error = `Không thể kết nối với server: ${err.message || 'Lỗi không xác định'}`;
    } finally {
      loading = false;
    }
  }

  function stopScanning() {
    scanning = false;
    
    if (qrCodeReader) {
      qrCodeReader.stop().catch(console.error);
      qrCodeReader = null;
    }

    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }

    if (videoElement) {
      videoElement.srcObject = null;
    }
  }

  function handleClose() {
    stopScanning();
    show = false;
    error = '';
    success = '';
    scanResult = null;
    manualQRInput = '';
    onClose();
  }

  // Handle Enter key in manual input
  function handleKeyPress(event) {
    if (event.key === 'Enter' && !loading) {
      handleManualInput();
    }
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
    >
      <!-- Header -->
      <div class="sticky top-0 bg-[#2a2a2a] border-b border-[#4a4a4a] p-6 flex items-center justify-between z-10">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-[#c4a574] rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-[#1a1a1a]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-bold text-[#c4a574]">Quét QR Code - Admin</h2>
            <p class="text-sm text-gray-400">Địa điểm: {locationName}</p>
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
        {#if !scanResult}
          {#if error}
            <div class="bg-red-500/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4">
              ⚠️ {error}
            </div>
          {/if}

          {#if success}
            <div class="bg-green-500/20 border border-green-500 text-green-400 px-4 py-3 rounded-lg mb-4">
              ✅ {success}
            </div>
          {/if}

          {#if !scanning}
            <div class="space-y-6">
              <div class="text-center py-4">
                <p class="text-gray-300 mb-4">Nhấn nút bên dưới để bắt đầu quét QR code bằng camera</p>
                <button
                  on:click={startScanning}
                  disabled={loading}
                  class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-8 py-3 rounded-lg transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {#if loading}
                    <span class="flex items-center gap-2">
                      <div class="w-5 h-5 border-2 border-[#1a1a1a] border-t-transparent rounded-full animate-spin"></div>
                      Đang khởi động camera...
                    </span>
                  {:else}
                    Bắt Đầu Quét Camera
                  {/if}
                </button>
              </div>
              
              <!-- Manual Input (always visible) -->
              <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
                <p class="text-gray-400 text-sm mb-2 font-semibold">📝 Nhập thủ công QR code:</p>
                <form on:submit|preventDefault={handleManualInput} class="flex gap-2">
                  <input
                    type="text"
                    bind:value={manualQRInput}
                    on:keypress={handleKeyPress}
                    placeholder="Dán dữ liệu QR code ở đây (format: ma_ve|dia_diem|timestamp|user_id)..."
                    class="flex-1 bg-[#2a2a2a] border border-[#4a4a4a] text-white px-4 py-2 rounded-lg focus:outline-none focus:border-[#c4a574] disabled:opacity-50"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading || !manualQRInput.trim()}
                    class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {loading ? 'Đang xử lý...' : 'Xác minh'}
                  </button>
                </form>
                <p class="text-gray-500 text-xs mt-2">💡 Nhấn Enter hoặc click nút "Xác minh" để gửi</p>
              </div>
            </div>
          {:else}
            <div class="space-y-4">
              <!-- Camera View -->
              <div class="w-full bg-black rounded-lg overflow-hidden" style="min-height: 300px; position: relative;">
                <div id="qr-reader" class="w-full h-full"></div>
                {#if !qrCodeReader && videoElement}
                  <!-- Fallback video element when library not available -->
                  <video
                    bind:this={videoElement}
                    autoplay
                    playsinline
                    muted
                    class="w-full h-auto absolute inset-0"
                  ></video>
                {/if}
              </div>

              <!-- Manual Input Fallback -->
              <div class="bg-[#1a1a1a] rounded-lg p-4 border border-[#4a4a4a]">
                <p class="text-gray-400 text-sm mb-2">Hoặc nhập/dán dữ liệu QR code thủ công:</p>
                <form on:submit|preventDefault={handleManualInput} class="flex gap-2">
                  <input
                    type="text"
                    bind:value={manualQRInput}
                    on:keypress={handleKeyPress}
                    placeholder="Dán dữ liệu QR code ở đây (format: ma_ve|dia_diem|timestamp|user_id)..."
                    class="flex-1 bg-[#2a2a2a] border border-[#4a4a4a] text-white px-4 py-2 rounded-lg focus:outline-none focus:border-[#c4a574]"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading || !manualQRInput.trim()}
                    class="bg-[#c4a574] hover:bg-[#d4b584] text-[#1a1a1a] font-bold px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {loading ? 'Đang xử lý...' : 'Xác minh'}
                  </button>
                </form>
                <p class="text-gray-500 text-xs mt-2">💡 Nhấn Enter hoặc click nút "Xác minh" để gửi</p>
              </div>

              {#if loading}
                <div class="text-center py-4">
                  <div class="w-8 h-8 border-4 border-[#c4a574] border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p class="text-gray-400 mt-2">Đang xử lý...</p>
                </div>
              {/if}

              <button
                on:click={stopScanning}
                class="w-full bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 rounded-lg transition-all"
              >
                Dừng Quét
              </button>
            </div>
          {/if}
        {:else}
          <!-- Scan Result -->
          <div class="text-center py-8 space-y-6">
            <div class="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
              <svg class="w-12 h-12 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>

            <div>
              <h3 class="text-2xl font-bold text-white mb-2">Check-in Thành Công!</h3>
              <p class="text-gray-400">{scanResult.message}</p>
            </div>

            <div class="bg-[#1a1a1a] rounded-lg p-6 border border-[#4a4a4a] max-w-md mx-auto text-left space-y-3">
              <div>
                <p class="text-gray-400 text-sm">Người dùng</p>
                <p class="text-[#c4a574] font-semibold">{scanResult.user_id}</p>
              </div>
              <div>
                <p class="text-gray-400 text-sm">Mã vé</p>
                <p class="text-white font-semibold">{scanResult.ma_ve}</p>
              </div>
              <div>
                <p class="text-gray-400 text-sm">Địa điểm</p>
                <p class="text-white font-semibold">{scanResult.dia_diem}</p>
              </div>
              {#if scanResult.checkin_time}
                <div>
                  <p class="text-gray-400 text-sm">Thời gian check-in</p>
                  <p class="text-gray-300">{scanResult.checkin_time}</p>
                </div>
              {/if}
              {#if scanResult.points_earned}
                <div class="bg-green-500/20 border border-green-500/30 rounded p-3">
                  <p class="text-green-400 text-sm mb-1">Điểm thưởng</p>
                  <p class="text-2xl font-bold text-green-400">+{scanResult.points_earned} điểm</p>
                  <p class="text-gray-400 text-xs mt-1">Tổng điểm: {scanResult.total_points}</p>
                </div>
              {/if}
              {#if scanResult.already_visited}
                <div class="bg-yellow-500/20 border border-yellow-500/30 rounded p-2">
                  <p class="text-yellow-400 text-sm">⚠️ Đã check-in trước đó</p>
                </div>
              {/if}
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

<style>
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes scaleIn {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out;
  }

  .animate-scaleIn {
    animation: scaleIn 0.3s ease-out;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>

