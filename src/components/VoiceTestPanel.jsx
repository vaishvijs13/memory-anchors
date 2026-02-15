import { useState } from 'react';
import { useVoiceNarration } from '../hooks/useVoiceNarration';

/**
 * Test panel for voice narration features
 * Includes textarea, Play/Stop, and "Tell me more" expansion
 */
export default function VoiceTestPanel() {
  const [text, setText] = useState(
    "This is where Grandpa used to sit every evening, reading stories aloud to the grandchildren while the sunset poured through the window."
  );
  const { play, stop, speaking, supported, expand, expanded, expanding, clearExpanded } = useVoiceNarration();

  const handlePlay = () => {
    const textToSpeak = expanded || text;
    play(textToSpeak);
  };

  const handleExpand = async () => {
    await expand(text);
  };

  const handlePlayExpanded = () => {
    if (expanded) play(expanded);
  };

  if (!supported) {
    return (
      <div className="voice-test-panel">
        <div className="voice-test-panel__unsupported">
          <span className="voice-test-panel__icon">🔇</span>
          <p>Voice not supported in this browser</p>
        </div>
      </div>
    );
  }

  return (
    <div className="voice-test-panel">
      <div className="voice-test-panel__header">
        <span className="voice-test-panel__icon">🎙️</span>
        <span className="voice-test-panel__title">Voice Test</span>
      </div>

      <textarea
        className="voice-test-panel__textarea"
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          clearExpanded();
        }}
        placeholder="Enter memory text to narrate..."
        rows={4}
      />

      <div className="voice-test-panel__buttons">
        <button
          className={`voice-test-panel__btn voice-test-panel__btn--play ${speaking ? 'speaking' : ''}`}
          onClick={speaking ? stop : handlePlay}
        >
          {speaking ? '⏹ Stop' : '▶ Play'}
        </button>

        <button
          className="voice-test-panel__btn voice-test-panel__btn--expand"
          onClick={handleExpand}
          disabled={expanding}
        >
          {expanding ? '...' : '✨ Tell me more'}
        </button>
      </div>

      {expanded && (
        <div className="voice-test-panel__expanded">
          <div className="voice-test-panel__expanded-header">
            <span>Expanded Memory</span>
            <button className="voice-test-panel__expanded-close" onClick={clearExpanded}>✕</button>
          </div>
          <p className="voice-test-panel__expanded-text">{expanded}</p>
          <button
            className="voice-test-panel__btn voice-test-panel__btn--play-expanded"
            onClick={handlePlayExpanded}
          >
            ▶ Play Expanded
          </button>
        </div>
      )}

      {speaking && (
        <div className="voice-test-panel__status">
          <span className="voice-test-panel__status-dot" />
          Speaking...
        </div>
      )}
    </div>
  );
}
