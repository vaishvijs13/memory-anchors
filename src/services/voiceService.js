/**
 * Voice Service for Memory Anchors
 * Supports ElevenLabs TTS (preferred) and Web Speech API (fallback)
 */

// ============================================
// Configuration
// ============================================
const ELEVENLABS_API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY || '';
const ELEVENLABS_VOICE_ID = import.meta.env.VITE_ELEVENLABS_VOICE_ID || 'EXAVITQu4vr4xnSDxMaL';

// Debug mode - set to true to see console logs
const DEBUG = true;
const log = (...args) => DEBUG && console.log('[VoiceService]', ...args);

// Check if speech synthesis is available
const isSpeechSupported = () => 
  typeof window !== 'undefined' && 'speechSynthesis' in window;

// Current state
let currentAudio = null;
let currentUtterance = null;
let speakingState = false;
let voicesLoaded = false;

// ============================================
// Initialize voices (they load async in some browsers)
// ============================================
function initVoices() {
  if (!isSpeechSupported()) return;
  
  const loadVoices = () => {
    const voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
      voicesLoaded = true;
      log('Voices loaded:', voices.length);
    }
  };
  
  // Load immediately if available
  loadVoices();
  
  // Also listen for the voiceschanged event (Chrome needs this)
  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }
}

// Initialize on load
if (typeof window !== 'undefined') {
  initVoices();
  // Also try after a short delay (some browsers need this)
  setTimeout(initVoices, 100);
}

// ============================================
// ElevenLabs TTS (High-quality voice)
// ============================================
async function playWithElevenLabs(text) {
  if (!ELEVENLABS_API_KEY) {
    log('ElevenLabs: No API key configured');
    return false;
  }

  log('ElevenLabs: Attempting to play with voice', ELEVENLABS_VOICE_ID);

  try {
    // Use non-streaming endpoint (more reliable)
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'xi-api-key': ELEVENLABS_API_KEY,
        },
        body: JSON.stringify({
          text,
          model_id: 'eleven_turbo_v2_5',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
          },
        }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      log('ElevenLabs: Request failed with status', response.status, errorText);
      return false;
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    log('ElevenLabs: Audio blob received, playing...');
    
    // Stop any existing audio
    stop();
    
    currentAudio = new Audio(audioUrl);
    currentAudio.onplay = () => { 
      speakingState = true; 
      log('ElevenLabs: Playing');
    };
    currentAudio.onended = () => { 
      speakingState = false; 
      currentAudio = null;
      URL.revokeObjectURL(audioUrl);
      log('ElevenLabs: Finished');
    };
    currentAudio.onerror = (e) => { 
      speakingState = false; 
      currentAudio = null;
      log('ElevenLabs: Audio error', e);
    };

    await currentAudio.play();
    return true;
  } catch (err) {
    log('ElevenLabs: Error', err.message);
    return false;
  }
}

// ============================================
// Web Speech API (Fallback - always available)
// ============================================
function playWithWebSpeech(text, options = {}) {
  if (!isSpeechSupported()) {
    log('WebSpeech: Not supported in this browser');
    return false;
  }

  log('WebSpeech: Playing text:', text.substring(0, 50) + '...');

  // Cancel any ongoing speech first
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = options.rate ?? 0.9;
  utterance.pitch = options.pitch ?? 1;
  utterance.volume = options.volume ?? 1;

  // Get available voices
  const voices = window.speechSynthesis.getVoices();
  log('WebSpeech: Available voices:', voices.length);
  
  if (voices.length > 0) {
    // Try to find a good English voice
    const preferredVoice = 
      voices.find(v => v.name.includes('Samantha')) ||
      voices.find(v => v.name.includes('Google') && v.lang.startsWith('en')) ||
      voices.find(v => v.name.includes('Natural') && v.lang.startsWith('en')) ||
      voices.find(v => v.lang === 'en-US') ||
      voices.find(v => v.lang.startsWith('en'));
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
      log('WebSpeech: Using voice:', preferredVoice.name);
    }
  }

  utterance.onstart = () => { 
    speakingState = true; 
    log('WebSpeech: Started speaking');
  };
  utterance.onend = () => { 
    speakingState = false; 
    currentUtterance = null;
    log('WebSpeech: Finished speaking');
  };
  utterance.onerror = (e) => { 
    speakingState = false; 
    currentUtterance = null;
    log('WebSpeech: Error', e.error);
  };

  currentUtterance = utterance;
  
  // Small delay to ensure voices are loaded (Chrome fix)
  setTimeout(() => {
    window.speechSynthesis.speak(utterance);
  }, 10);
  
  return true;
}

// ============================================
// Public API
// ============================================

/**
 * Play memory text as speech
 * Uses ElevenLabs if API key is set and working, otherwise falls back to Web Speech
 */
export async function playMemory(text, options = {}) {
  log('playMemory called with text length:', text.length);
  
  // Stop any current speech
  stop();

  // Try ElevenLabs first (unless forced to use Web Speech)
  if (!options.forceWebSpeech && ELEVENLABS_API_KEY) {
    log('Trying ElevenLabs first...');
    const success = await playWithElevenLabs(text);
    if (success) {
      log('ElevenLabs succeeded');
      return true;
    }
    log('ElevenLabs failed, falling back to Web Speech');
  }

  // Fall back to Web Speech
  return playWithWebSpeech(text, options);
}

/**
 * Stop current speech
 */
export function stop() {
  log('stop() called');
  
  // Stop ElevenLabs audio
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
  
  // Stop Web Speech
  if (isSpeechSupported()) {
    window.speechSynthesis.cancel();
  }
  
  speakingState = false;
  currentUtterance = null;
}

/**
 * Check if currently speaking
 */
export function isSpeaking() {
  if (currentAudio && !currentAudio.paused) return true;
  if (isSpeechSupported() && window.speechSynthesis.speaking) return true;
  return speakingState;
}

/**
 * Check if voice is supported (at least Web Speech)
 */
export function isSupported() {
  return isSpeechSupported();
}

/**
 * Check if ElevenLabs is configured and has a valid key
 */
export function hasElevenLabs() {
  return !!ELEVENLABS_API_KEY && ELEVENLABS_API_KEY.length > 10;
}

// ============================================
// "Tell Me More" Expansion Feature
// ============================================

const EXPANSION_TEMPLATES = [
  "This memory has been with the family for generations, passed down through stories and quiet moments. It represents more than just an object—it's a piece of who we are.",
  "Every time we see this, it brings back the warmth of those days. The laughter, the conversations, the feeling of being truly connected to the people we love.",
  "There's something magical about how ordinary things become extraordinary through the memories we attach to them. This is one of those treasures.",
  "The family often talks about this when we gather together. It's amazing how one simple thing can hold so much meaning and bring back so many feelings.",
  "Sometimes the simplest objects carry the deepest memories. This one takes us back to a time when everything felt safe and the world was full of wonder.",
];

/**
 * Expand a memory with additional context
 */
export async function expandMemory(memoryText, options = {}) {
  const openaiKey = import.meta.env.VITE_OPENAI_API_KEY;
  const useLLM = options.useLLM && openaiKey;
  
  if (useLLM) {
    try {
      return await expandWithLLM(memoryText, openaiKey);
    } catch (err) {
      log('LLM expansion failed, using fallback:', err.message);
    }
  }
  
  return expandLocally(memoryText);
}

function expandLocally(memoryText) {
  const template = EXPANSION_TEMPLATES[Math.floor(Math.random() * EXPANSION_TEMPLATES.length)];
  return `${memoryText}\n\n${template}`;
}

async function expandWithLLM(memoryText, apiKey) {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: 'gpt-3.5-turbo',
      messages: [
        {
          role: 'system',
          content: 'You are a warm, empathetic storyteller helping someone with memory difficulties. Expand the given memory with 2-3 additional sentences that add emotional depth and sensory details. Keep it gentle and positive.',
        },
        {
          role: 'user',
          content: `Expand this memory: "${memoryText}"`,
        },
      ],
      max_tokens: 150,
      temperature: 0.7,
    }),
    signal: AbortSignal.timeout(5000),
  });

  if (!response.ok) throw new Error('API request failed');
  
  const data = await response.json();
  return data.choices?.[0]?.message?.content?.trim() || expandLocally(memoryText);
}

// ============================================
// Global Window Export
// ============================================
if (typeof window !== 'undefined') {
  window.VoiceService = {
    playMemory,
    stop,
    isSpeaking,
    isSupported,
    hasElevenLabs,
    expandMemory,
  };
  
  log('VoiceService registered on window');
  log('ElevenLabs configured:', hasElevenLabs());
  log('Web Speech supported:', isSpeechSupported());
}

export default {
  playMemory,
  stop,
  isSpeaking,
  isSupported,
  hasElevenLabs,
  expandMemory,
};
