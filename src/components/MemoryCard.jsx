import { useState, useCallback, useEffect } from "react";

/**
 * Floating memory card overlay with voice controls.
 */
export default function MemoryCard({ memory, label, position, onClose }) {
  const [speaking, setSpeaking] = useState(false);
  const [expanding, setExpanding] = useState(false);
  const [expandedText, setExpandedText] = useState(null);

  // Poll speaking state
  useEffect(() => {
    const interval = setInterval(() => {
      const isSpeaking = window.VoiceService?.isSpeaking?.() || false;
      setSpeaking(isSpeaking);
    }, 150);
    return () => clearInterval(interval);
  }, []);

  // Stop speaking when card closes
  useEffect(() => {
    return () => {
      if (window.VoiceService?.stop) {
        window.VoiceService.stop();
      }
    };
  }, []);

  const handlePlay = useCallback(async () => {
    if (speaking) {
      // Stop
      if (window.VoiceService?.stop) {
        window.VoiceService.stop();
      } else if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      setSpeaking(false);
    } else {
      // Play
      const textToSpeak = expandedText || memory.text;
      console.log('[MemoryCard] Playing:', textToSpeak.substring(0, 50) + '...');
      
      if (window.VoiceService?.playMemory) {
        setSpeaking(true); // Optimistic update
        try {
          const success = await window.VoiceService.playMemory(textToSpeak);
          if (!success) {
            console.warn('[MemoryCard] VoiceService.playMemory returned false');
            setSpeaking(false);
          }
        } catch (err) {
          console.error('[MemoryCard] playMemory error:', err);
          setSpeaking(false);
        }
      } else if ("speechSynthesis" in window) {
        // Direct fallback if VoiceService not available
        console.log('[MemoryCard] Using direct speechSynthesis fallback');
        const utter = new SpeechSynthesisUtterance(textToSpeak);
        utter.rate = 0.9;
        utter.pitch = 1;
        utter.onstart = () => setSpeaking(true);
        utter.onend = () => setSpeaking(false);
        utter.onerror = () => setSpeaking(false);
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
      } else {
        console.warn('[MemoryCard] No speech synthesis available');
      }
    }
  }, [memory.text, expandedText, speaking]);

  const handleExpand = useCallback(async () => {
    if (!window.VoiceService?.expandMemory) {
      console.warn('[MemoryCard] expandMemory not available');
      return;
    }
    
    setExpanding(true);
    try {
      const expanded = await window.VoiceService.expandMemory(memory.text);
      setExpandedText(expanded);
    } catch (err) {
      console.warn("[MemoryCard] Expand failed:", err);
    } finally {
      setExpanding(false);
    }
  }, [memory.text]);

  if (!memory) return null;

  const style = {
    position: "absolute",
    top: position?.top ?? 80,
    left: position?.left ?? 24,
    zIndex: 20,
  };

  const displayText = expandedText || memory.text;

  return (
    <div className="memory-card" style={style}>
      <div className="memory-card__header">
        <svg className="memory-card__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M20 7h-4V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/>
          <circle cx="12" cy="13" r="3"/>
        </svg>
        <span className="memory-card__label">{label}</span>
        <button
          className="memory-card__close"
          onClick={onClose}
          aria-label="Close"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
      
      <h3 className="memory-card__title">{memory.title}</h3>
      <p className="memory-card__text">{displayText}</p>
      
      <div className="memory-card__actions">
        <button 
          className={`memory-card__play ${speaking ? 'speaking' : ''}`} 
          onClick={handlePlay}
        >
          {speaking ? '⏹ Stop' : '▶ Play'}
        </button>
        
        {!expandedText && (
          <button 
            className="memory-card__expand"
            onClick={handleExpand}
            disabled={expanding}
          >
            {expanding ? '...' : '✨ Tell me more'}
          </button>
        )}
      </div>

      {speaking && (
        <div className="memory-card__voice-indicator">
          <div className="memory-card__voice-bars">
            <div className="memory-card__voice-bar" />
            <div className="memory-card__voice-bar" />
            <div className="memory-card__voice-bar" />
            <div className="memory-card__voice-bar" />
            <div className="memory-card__voice-bar" />
          </div>
          <span>Speaking...</span>
        </div>
      )}
    </div>
  );
}
