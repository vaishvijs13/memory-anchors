import { SUPPORTED_OBJECTS } from "../services/detection";

/**
 * Demo Mode controls: a toggle and a dropdown to manually trigger detections.
 *
 * Props:
 *  - demoMode: boolean
 *  - onToggleDemo: () => void
 *  - selectedLabel: string
 *  - onSelectLabel: (label) => void
 *  - onTrigger: () => void
 *  - modelReady: boolean
 */
export default function Controls({
  demoMode,
  onToggleDemo,
  selectedLabel,
  onSelectLabel,
  onTrigger,
  modelReady,
}) {
  return (
    <div className="controls">
      <div className="controls__row">
        <label className="controls__toggle-label">
          <input
            type="checkbox"
            checked={demoMode}
            onChange={onToggleDemo}
            className="controls__checkbox"
          />
          <span className="controls__toggle-track">
            <span className="controls__toggle-thumb" />
          </span>
          <span className="controls__toggle-text">Demo Mode</span>
        </label>

        {!demoMode && (
          <span className={`controls__status ${modelReady ? "ready" : "loading"}`}>
            {modelReady ? "● Model Ready" : "◌ Loading model…"}
          </span>
        )}
      </div>

      {demoMode && (
        <div className="controls__demo-panel">
          <select
            className="controls__select"
            value={selectedLabel}
            onChange={(e) => onSelectLabel(e.target.value)}
          >
            {SUPPORTED_OBJECTS.map((obj) => (
              <option key={obj} value={obj}>
                {obj.charAt(0).toUpperCase() + obj.slice(1)}
              </option>
            ))}
          </select>
          <button className="controls__trigger" onClick={onTrigger}>
            Trigger Memory
          </button>
        </div>
      )}
    </div>
  );
}
