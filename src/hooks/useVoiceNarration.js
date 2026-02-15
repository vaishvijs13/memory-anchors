import { useState, useCallback, useEffect } from 'react';
import { playMemory, stop, isSpeaking, isSupported, expandMemory } from '../services/voiceService';

/**
 * React hook for voice narration functionality
 * @returns {object} - { play, stop, speaking, supported, expand, expanded, expanding }
 */
export function useVoiceNarration() {
  const [speaking, setSpeaking] = useState(false);
  const [supported] = useState(isSupported);
  const [expanded, setExpanded] = useState(null);
  const [expanding, setExpanding] = useState(false);

  // Poll speaking state (Web Speech API doesn't have reliable events in all browsers)
  useEffect(() => {
    if (!supported) return;
    
    const interval = setInterval(() => {
      setSpeaking(isSpeaking());
    }, 100);
    
    return () => clearInterval(interval);
  }, [supported]);

  const play = useCallback((text, options) => {
    if (!supported) return false;
    const result = playMemory(text, options);
    if (result) setSpeaking(true);
    return result;
  }, [supported]);

  const stopNarration = useCallback(() => {
    stop();
    setSpeaking(false);
  }, []);

  const expand = useCallback(async (memoryText, options = {}) => {
    setExpanding(true);
    try {
      const result = await expandMemory(memoryText, options);
      setExpanded(result);
      return result;
    } finally {
      setExpanding(false);
    }
  }, []);

  const clearExpanded = useCallback(() => {
    setExpanded(null);
  }, []);

  return {
    play,
    stop: stopNarration,
    speaking,
    supported,
    expand,
    expanded,
    expanding,
    clearExpanded,
  };
}

export default useVoiceNarration;
