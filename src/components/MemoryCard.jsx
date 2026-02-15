import { useState, useCallback, useEffect } from "react";

/**
 * Floating memory card overlay with voice controls.
 *
 * Props:
 *  - memory: { title, text }
 *  - label: the detected object name
 *  - position: { top, left } (optional, for positioning near bbox)
 *  - onClose: callback to dismiss the card
 */
export default function MemoryCard({ memory, label, position, onClose }) {
  const [speaking, setSpeaking] = useState(false);
  const [expanding, setExpanding] = useState(false);
  const [expandedText, setExpandedText] = useState(null);

  // Poll speaking state
  useEffect(() => {
    const interval = setInterval(() => {
      if (window.VoiceService?.isSpeaking) {
        setSpeaking(window.VoiceService.isSpeaking());
      }
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const handlePlay = useCallback(() => {
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
      if (window.VoiceService?.playMemory) {
        window.VoiceService.playMemory(textToSpeak);
        setSpeaking(true);
      } else if ("speechSynthesis" in window) {
        const utter = new SpeechSynthesisUtterance(textToSpeak);
        utter.rate = 0.9;
        utter.pitch = 1;
        utter.onend = () => setSpeaking(false);
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
        setSpeaking(true);
      }
    }
  }, [memory.text, expandedText, speaking]);

  const handleExpand = useCallback(async () => {
    if (!window.VoiceService?.expandMemory) return;
    
    setExpanding(true);
    try {
      const expanded = await window.VoiceService.expandMemory(memory.text);
      setExpandedText(expanded);
    } catch (err) {
      console.warn("Expand failed:", err);
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
        <span className="memory-card__icon">✨</span>
        <span className="memory-card__label">{label}</span>
        <button
          className="memory-card__close"
          onClick={onClose}
          aria-label="Close"
        >
          ✕
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
