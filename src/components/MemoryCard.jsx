import { useCallback } from "react";

/**
 * Floating memory card overlay.
 *
 * Props:
 *  - memory: { title, text }
 *  - label: the detected object name
 *  - position: { top, left } (optional, for positioning near bbox)
 *  - onClose: callback to dismiss the card
 */
export default function MemoryCard({ memory, label, position, onClose }) {
  if (!memory) return null;

  const handlePlay = useCallback(() => {
    // Voice service stub
    if (window.VoiceService && typeof window.VoiceService.playMemory === "function") {
      window.VoiceService.playMemory(memory.text);
    } else {
      // Fallback: use browser SpeechSynthesis if available
      if ("speechSynthesis" in window) {
        const utter = new SpeechSynthesisUtterance(memory.text);
        utter.rate = 0.9;
        utter.pitch = 1;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
      }
    }
  }, [memory.text]);

  const style = {
    position: "absolute",
    top: position?.top ?? 80,
    left: position?.left ?? 24,
    zIndex: 20,
  };

  return (
    <div className="memory-card" style={style}>
      <div className="memory-card__header">
        <span className="memory-card__icon">💡</span>
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
      <p className="memory-card__text">{memory.text}</p>
      <button className="memory-card__play" onClick={handlePlay}>
        ▶ Play Memory
      </button>
    </div>
  );
}
