/**
 * Voice Service for Memory Anchors
 * Supports ElevenLabs TTS (preferred) and Web Speech API (fallback)
 */

// ============================================
// Configuration
// ============================================
const ELEVENLABS_API_KEY = import.meta.env.VITE_ELEVENLABS_API_KEY;
const ELEVENLABS_VOICE_ID = import.meta.env.VITE_ELEVENLABS_VOICE_ID || 'EXAVITQu4vr4xnSDxMaL'; // Default: Sarah (warm, clear)

// Check if speech synthesis is available
const isSpeechSupported = () => 
  typeof window !== 'undefined' && 'speechSynthesis' in window;

// Current state
let currentAudio = null;
let currentUtterance = null;
let speakingState = false;

// ============================================
// ElevenLabs TTS (High-quality voice)
// ============================================
async function playWithElevenLabs(text) {
  if (!ELEVENLABS_API_KEY) return false;

  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'xi-api-key': ELEVENLABS_API_KEY,
        },
        body: JSON.stringify({
          text,
          model_id: 'eleven_monolingual_v1',
          voice_settings: {
            stability: 0.75,
            similarity_boost: 0.75,
          },
        }),
      }
    );

    if (!response.ok) {
      console.warn('VoiceService: ElevenLabs request failed', response.status);
      return false;
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    
    // Stop any existing audio
    stop();
    
    currentAudio = new Audio(audioUrl);
    currentAudio.onplay = () => { speakingState = true; };
    currentAudio.onended = () => { 
      speakingState = false; 
      currentAudio = null;
      URL.revokeObjectURL(audioUrl);
    };
    currentAudio.onerror = () => { 
      speakingState = false; 
      currentAudio = null;
    };

    await currentAudio.play();
    return true;
  } catch (err) {
    console.warn('VoiceService: ElevenLabs error', err);
    return false;
  }
}

// ============================================
// Web Speech API (Fallback)
// ============================================
function playWithWebSpeech(text, options = {}) {
  if (!isSpeechSupported()) return false;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = options.rate ?? 0.9;
  utterance.pitch = options.pitch ?? 1;
  utterance.volume = options.volume ?? 1;

  // Try to use a natural voice if available
  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(v => 
    v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Samantha'))
  ) || voices.find(v => v.lang.startsWith('en'));
  
  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  utterance.onstart = () => { speakingState = true; };
  utterance.onend = () => { speakingState = false; currentUtterance = null; };
  utterance.onerror = () => { speakingState = false; currentUtterance = null; };

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
  return true;
}

// ============================================
// Public API
// ============================================

/**
 * Play memory text as speech
 * Uses ElevenLabs if API key is set, otherwise falls back to Web Speech
 * @param {string} text - The text to speak
 * @param {object} options - Optional config { rate, pitch, voice, forceWebSpeech }
 * @returns {Promise<boolean>} - true if started, false if not supported
 */
export async function playMemory(text, options = {}) {
  // Stop any current speech
  stop();

  // Try ElevenLabs first (unless forced to use Web Speech)
  if (!options.forceWebSpeech && ELEVENLABS_API_KEY) {
    const success = await playWithElevenLabs(text);
    if (success) return true;
  }

  // Fall back to Web Speech
  return playWithWebSpeech(text, options);
}

/**
 * Stop current speech
 */
export function stop() {
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
 * @returns {boolean}
 */
export function isSpeaking() {
  if (currentAudio && !currentAudio.paused) return true;
  if (isSpeechSupported() && window.speechSynthesis.speaking) return true;
  return speakingState;
}

/**
 * Check if voice is supported (at least Web Speech)
 * @returns {boolean}
 */
export function isSupported() {
  return isSpeechSupported() || !!ELEVENLABS_API_KEY;
}

/**
 * Check if ElevenLabs is configured
 * @returns {boolean}
 */
export function hasElevenLabs() {
  return !!ELEVENLABS_API_KEY;
}

// ============================================
// "Tell Me More" Expansion Feature
// ============================================

const EXPANSION_TEMPLATES = [
  "This memory has been with the family for generations, passed down through stories and quiet moments. It represents more than just an object—it's a piece of who we are.",
  "Every time we see this, it brings back the warmth of those days. The laughter, the conversations, the feeling of being truly connected to the people we love.",
  "There's something magical about how ordinary things become extraordinary through the memories we attach to them. This is one of those treasures.",
  "The family often talks about this when we gather together. It's amazing how one simple thing can hold so much meaning and bring back so many feelings.",
];

/**
 * Expand a memory with additional context
 * Uses local templates by default, optional LLM if configured
 * @param {string} memoryText - Original memory text
 * @param {object} options - { useLLM: boolean }
 * @returns {Promise<string>} - Expanded memory text
 */
export async function expandMemory(memoryText, options = {}) {
  const useLLM = options.useLLM && import.meta.env.VITE_OPENAI_API_KEY;
  
  if (useLLM) {
    try {
      return await expandWithLLM(memoryText);
    } catch (err) {
      console.warn('VoiceService: LLM expansion failed, using fallback', err);
    }
  }
  
  return expandLocally(memoryText);
}

function expandLocally(memoryText) {
  const template = EXPANSION_TEMPLATES[Math.floor(Math.random() * EXPANSION_TEMPLATES.length)];
  return `${memoryText}\n\n${template}`;
}

async function expandWithLLM(memoryText) {
  const apiKey = import.meta.env.VITE_OPENAI_API_KEY;
  if (!apiKey) throw new Error('No API key');

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
  const expansion = data.choices?.[0]?.message?.content?.trim();
  
  return expansion || expandLocally(memoryText);
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
}

export default {
  playMemory,
  stop,
  isSpeaking,
  isSupported,
  hasElevenLabs,
  expandMemory,
};
