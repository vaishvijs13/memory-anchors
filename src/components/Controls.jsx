import { SUPPORTED_OBJECTS } from "../services/detection";

/**
 * Bottom controls: mode toggle, demo panel, and upload button.
 */
export default function Controls({
  demoMode,
  onToggleDemo,
  selectedLabel,
  onSelectLabel,
  onTrigger,
  modelReady,
  onUpload,
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
          <span className="controls__toggle-text">DEMO_MODE</span>
        </label>

        <div className="controls__right">
          {!demoMode && (
            <span className={`controls__status ${modelReady ? "ready" : "loading"}`}>
              {modelReady ? "◉ MDL_ACTIVE" : "◌ MDL_LOADING"}
            </span>
          )}
          
          <button className="controls__upload-btn" onClick={onUpload}>
            + ADD_MEMORY
          </button>
        </div>
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
                {obj.toUpperCase()}
              </option>
            ))}
          </select>
          <button className="controls__trigger" onClick={onTrigger}>
            [ TRIGGER ]
          </button>
        </div>
      )}
    </div>
  );
}
