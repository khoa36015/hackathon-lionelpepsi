import { Anh, Vat } from '$lib/api'; // Lead đã có 2 hàm này
import { getCached, setCached } from '$lib/utils/cache';

const inflight = new Map(); // key: 'anh' | 'vat' -> Promise

export async function getOptionData(option /* 'anh' | 'vat' */) {
  const cacheKey = option === 'anh' ? 'cache:Anh' : 'cache:Vat';

  // 1) lấy cache nếu còn hạn
  const cached = getCached(cacheKey);
  if (cached) return cached;

  // 2) chống fetch trùng trong cùng session
  if (inflight.has(option)) return inflight.get(option);

  const p = (async () => {
    const data = option === 'anh' ? await Anh() : await Vat();
    setCached(cacheKey, data); // TTL mặc định 2 giờ
    inflight.delete(option);
    return data;
  })();

  inflight.set(option, p);
  return p;
}
