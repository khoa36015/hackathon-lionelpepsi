// Global store cho Option đang chọn + dữ liệu đã fetch (để không fetch lại trong phiên)
// An toàn SSR: chỉ đụng localStorage khi browser === true

import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';
import { getCached, setCached, isExpired } from '$lib/utils/cache';
import { Anh, Vat } from '$lib/api';

// Key lưu option
const OPTION_KEY = 'chosen-option';

// option hiện tại: 'anh' | 'vat' | null
export const chosenOption = writable(null);

// dữ liệu đã fetch theo option hiện tại (global, tái sử dụng nhiều nơi)
export const chosenData = writable(null);

// cache trong phiên (in-memory) để tránh fetch lặp lại khi đã có data
const memoryCache = {
  anh: null,
  vat: null
};

function readInitialOption() {
  if (!browser) return null;
  try {
    const raw = localStorage.getItem(OPTION_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

if (browser) {
  const initial = readInitialOption();
  if (initial === 'anh' || initial === 'vat') {
    chosenOption.set(initial);
    // Tải data từ cache nếu có, không thì đợi caller gọi ensureData
    const cached = getCached(initial);
    if (cached && !isExpired(cached.timestamp, 2)) {
      memoryCache[initial] = cached.data;
      chosenData.set(cached.data);
    }
  }
}

export function setChosenOption(option) {
  if (option !== 'anh' && option !== 'vat') option = null;
  chosenOption.set(option);
  if (browser) {
    localStorage.setItem(OPTION_KEY, JSON.stringify(option));
  }
}

/**
 * Đảm bảo có dữ liệu tương ứng với option hiện tại (hoặc option truyền vào).
 * Ưu tiên: memoryCache -> localStorage TTL 2h -> fetch API -> ghi cache (mem + localStorage)
 */
export async function ensureData(optionOverride) {
  const option = optionOverride ?? get(chosenOption);
  if (option !== 'anh' && option !== 'vat') return null;

  // 1) memory cache
  if (memoryCache[option]) {
    chosenData.set(memoryCache[option]);
    return memoryCache[option];
  }

  // 2) localStorage cache TTL 2h
  if (browser) {
    const cached = getCached(option);
    if (cached && !isExpired(cached.timestamp, 2)) {
      memoryCache[option] = cached.data;
      chosenData.set(cached.data);
      return cached.data;
    }
  }

  // 3) fetch
  const data = option === 'anh' ? await Anh() : await Vat();

  // save mem + local
  memoryCache[option] = data;
  chosenData.set(data);
  if (browser) setCached(option, data); // timestamp now

  return data;
}

/** Đổi option + fetch dữ liệu tương ứng, trả về data */
export async function switchOption() {
  const current = get(chosenOption);
  const next = current === 'anh' ? 'vat' : 'anh';
  setChosenOption(next);
  return ensureData(next);
}
