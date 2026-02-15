import { useState, useEffect } from "react";

/**
 * Technical HUD overlay showing system status.
 */
export default function SystemHUD({ modelReady, cameraReady, detectionCount = 0 }) {
  const [fps, setFps] = useState(0);
  const [time, setTime] = useState("");
  const [memoryCount, setMemoryCount] = useState(null);

  // Update time
  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTime(now.toTimeString().slice(0, 8));
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  // Fetch memory count from backend
  useEffect(() => {
    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
    fetch(`${API_BASE}/memory`)
      .then(r => r.json())
      .then(data => setMemoryCount(Array.isArray(data) ? data.length : null))
      .catch(() => setMemoryCount(null));
  }, []);

  // Simulate FPS counter
  useEffect(() => {
    let frames = 0;
    let lastTime = performance.now();
    
    const countFrame = () => {
      frames++;
      const now = performance.now();
      if (now - lastTime >= 1000) {
        setFps(frames);
        frames = 0;
        lastTime = now;
      }
      requestAnimationFrame(countFrame);
    };
    
    const id = requestAnimationFrame(countFrame);
    return () => cancelAnimationFrame(id);
  }, []);

  return (
    <div className="hud">
      {/* Top-left: System info */}
      <div className="hud__block hud__block--tl">
        <div className="hud__line">
          <span className="hud__key">SYS</span>
          <span className="hud__val hud__val--ok">MEMORY_ANCHORS v1.0</span>
        </div>
        <div className="hud__line">
          <span className="hud__key">UTC</span>
          <span className="hud__val">{time}</span>
        </div>
        <div className="hud__line">
          <span className="hud__key">FPS</span>
          <span className={`hud__val ${fps > 24 ? 'hud__val--ok' : 'hud__val--warn'}`}>{fps}</span>
        </div>
      </div>

      {/* Top-right: Module status */}
      <div className="hud__block hud__block--tr">
        <div className="hud__line">
          <span className="hud__key">CAM</span>
          <span className={`hud__val ${cameraReady ? 'hud__val--ok' : 'hud__val--err'}`}>
            {cameraReady ? "ACTIVE" : "OFFLINE"}
          </span>
        </div>
        <div className="hud__line">
          <span className="hud__key">MDL</span>
          <span className={`hud__val ${modelReady ? 'hud__val--ok' : 'hud__val--warn'}`}>
            {modelReady ? "COCO-SSD" : "LOADING"}
          </span>
        </div>
        <div className="hud__line">
          <span className="hud__key">TTS</span>
          <span className={`hud__val ${window.VoiceService?.hasElevenLabs?.() ? 'hud__val--ok' : 'hud__val--warn'}`}>
            {window.VoiceService?.hasElevenLabs?.() ? "ELEVEN_LABS" : "WEB_SPEECH"}
          </span>
        </div>
      </div>

      {/* Bottom-left: Detection info */}
      <div className="hud__block hud__block--bl">
        <div className="hud__line">
          <span className="hud__key">OBJ</span>
          <span className="hud__val">{detectionCount} DETECTED</span>
        </div>
        <div className="hud__line">
          <span className="hud__key">MEM</span>
          <span className="hud__val">{memoryCount !== null ? `${memoryCount} ANCHORED` : "---"}</span>
        </div>
      </div>

      {/* Corner brackets */}
      <div className="hud__corner hud__corner--tl" />
      <div className="hud__corner hud__corner--tr" />
      <div className="hud__corner hud__corner--bl" />
      <div className="hud__corner hud__corner--br" />

      {/* Scanlines effect */}
      <div className="hud__scanlines" />
    </div>
  );
}
