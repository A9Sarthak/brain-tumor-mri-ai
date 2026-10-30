import { HistoryItem } from './types';

const STORAGE_KEY = 'neuroscan_history';
const MAX_HISTORY_ITEMS = 6;

/**
 * Sanitizes a history item to ensure massive base64 images (>50KB) and
 * heavy multi-layer Grad-CAM overlays are not persisted into the 5MB browser localStorage quota.
 */
function sanitizeHistoryItem(item: HistoryItem): HistoryItem {
  let thumb = item.thumbnail || item.image_preview || '';

  // If thumbnail is a giant raw base64 string (>30KB), strip it from persistent localStorage
  if (thumb.startsWith('data:image/') && thumb.length > 30000) {
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
        list = JSON.parse(stored);
        if (!Array.isArray(list)) list = [];
      }
    } catch {
      list = [];
    }

    // Prepend new item and keep up to MAX_HISTORY_ITEMS
    list = [cleanItem, ...list.filter((x) => x && x.id !== cleanItem.id)].slice(0, MAX_HISTORY_ITEMS);

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch {
      // Storage quota exceeded: prune thumbnails from all items and reduce count
      try {
        const lightweightList = list.slice(0, 3).map((it) => ({
          ...it,
          thumbnail: '',
          image_preview: '',
        }));
        localStorage.setItem(STORAGE_KEY, JSON.stringify(lightweightList));
      } catch {
        // Extreme fallback: reset key to prevent app crashing
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
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed : [];
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

