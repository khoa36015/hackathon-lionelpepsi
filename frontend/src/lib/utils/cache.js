// Helper cache LocalStorage theo TTL giờ
import { browser } from '$app/environment';

const CACHE_PREFIX = 'cache:'; // -> cache:anh, cache:vat

export function setCached(option, data) {
  if (!browser) return;
  try {
    const payload = { timestamp: Date.now(), data };
    localStorage.setItem(CACHE_PREFIX + option, JSON.stringify(payload));
  } catch {}
}

export function getCached(option) {
  if (!browser) return null;
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + option);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

/** TTL giờ (ví dụ 2 giờ) */
export function isExpired(timestamp, ttlHours = 2) {
  const ttlMs = ttlHours * 60 * 60 * 1000;
  return Date.now() - timestamp > ttlMs;
}

/** (tuỳ chọn) quét dọn cache hết hạn */
export function sweepExpired(ttlHours = 2) {
  if (!browser) return;
  const keys = ['anh', 'vat'];
  keys.forEach((k) => {
    const item = getCached(k);
    if (item && isExpired(item.timestamp, ttlHours)) {
      try {
        localStorage.removeItem('cache:' + k);
      } catch {}
    }
  });
}
