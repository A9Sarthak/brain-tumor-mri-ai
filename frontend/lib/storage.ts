import { HistoryItem } from './types';

const STORAGE_KEY = 'neuroscan_history';
const MAX_HISTORY_ITEMS = 6;

// Auto-purge any legacy bloated history (>50KB) on module load to immediately reclaim browser quota
if (typeof window !== 'undefined') {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw && raw.length > 50000) {
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch {}
}

/**
 * Sanitizes a history item to ensure massive base64 images (>50KB) and
 * heavy multi-layer Grad-CAM overlays are not persisted into the 5MB browser localStorage quota.
 */
function sanitizeHistoryItem(item: HistoryItem): HistoryItem {
  let thumb = item.thumbnail || item.image_preview || '';

  // Base64 image payloads (data:image/...) are 1MB to 3MB each and will quickly blow past
  // the browser's 5MB localStorage quota. Only allow short relative/absolute URLs (e.g. /samples/...)
  // or blob URLs. Never persist raw base64 strings into localStorage.
  if (thumb.startsWith('data:') || thumb.length > 1024) {
    thumb = '';
  }

  return {
    id: item.id,
    prediction: item.prediction,
    confidence: item.confidence,
    timestamp: item.timestamp,
    thumbnail: thumb,
    probabilities: item.probabilities || {},
    gradcam: undefined, // Do not store heavy multi-megabyte gradcam heatmaps in localStorage
    image_preview: thumb,
  };
}

/**
 * Safely saves a history item to localStorage with automated quota handling and fallback.
 */
export function saveHistoryItem(newItem: HistoryItem): void {
  if (typeof window === 'undefined') return;

  try {
    const cleanItem = sanitizeHistoryItem(newItem);
    let list: HistoryItem[] = [];

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        // If legacy stored string was bloated by previous un-sanitized versions (>100KB),
        // purge it immediately to free up quota before writing.
        if (stored.length > 50000) {
          localStorage.removeItem(STORAGE_KEY);
        } else {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed)) {
            list = parsed.map(sanitizeHistoryItem);
          }
        }
      }
    } catch {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch {}
      list = [];
    }

    // Prepend new item and keep up to MAX_HISTORY_ITEMS
    list = [cleanItem, ...list.filter((x) => x && x.id !== cleanItem.id)].slice(0, MAX_HISTORY_ITEMS);

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch {
      // Storage quota exceeded: purge existing key first to ensure space is reclaimed,
      // then attempt saving a ultra-compact metadata-only list.
      try {
        localStorage.removeItem(STORAGE_KEY);
        const metadataOnly = list.slice(0, 3).map((it) => ({
          ...it,
          thumbnail: '',
          image_preview: '',
        }));
        localStorage.setItem(STORAGE_KEY, JSON.stringify(metadataOnly));
      } catch {
        // Extreme fallback: ensure key is removed so app never crashes
        try {
          localStorage.removeItem(STORAGE_KEY);
        } catch {}
      }
    }
  } catch {
    // Suppress any storage-related errors
  }
}

/**
 * Safely retrieves history items from localStorage.
 */
export function getHistory(): HistoryItem[] {
  if (typeof window === 'undefined') return [];
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    
    // Automatically purge legacy un-sanitized bloated storage (>100KB)
    if (stored.length > 50000) {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch {}
      return [];
    }
    
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed.map(sanitizeHistoryItem) : [];
  } catch {
    return [];
  }
}

/**
 * Safely clears history items from localStorage.
 */
export function clearHistory(): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {}
}

