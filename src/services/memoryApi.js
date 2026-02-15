/**
 * Local fallback memory map — used when the backend API is unreachable.
 */
const FALLBACK_MEMORIES = {
  chair: {
    title: "Grandpa's Rocking Chair",
    text: "This is where Grandpa used to sit every evening, reading stories aloud to the grandchildren while the sunset poured through the window.",
  },
  book: {
    title: "Mom's Favorite Novel",
    text: "Mom always kept this book on the nightstand. She said it reminded her of the summer she spent in the countryside as a girl.",
  },
  tv: {
    title: "Sunday Movie Nights",
    text: "Every Sunday the whole family would gather around the TV with popcorn. Dad always picked the old black-and-white comedies.",
  },
  laptop: {
    title: "First Video Call with Sarah",
    text: "This is the laptop we used for the very first video call with Sarah when she moved abroad. Everyone crowded around the screen, waving.",
  },
};

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

/**
 * Fetch a memory for a given object label.
 * Tries the backend API first; falls back to local map.
 * Returns { title, text } or null.
 */
export async function fetchMemory(objectLabel) {
  const label = objectLabel.toLowerCase();

  // Try backend API
  try {
    const res = await fetch(`${API_BASE}/memory/${encodeURIComponent(label)}`, {
      signal: AbortSignal.timeout(3000),
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.title && data.text) {
        return { title: data.title, text: data.text };
      }
    }
  } catch {
    // Network error or timeout — fall through to fallback
  }

  // Fallback to local memories
  if (FALLBACK_MEMORIES[label]) {
    return { ...FALLBACK_MEMORIES[label] };
  }

  return null;
}

/**
 * Get the list of object labels that have memories available locally.
 */
export function getAvailableLabels() {
  return Object.keys(FALLBACK_MEMORIES);
}
