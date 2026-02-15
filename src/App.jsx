import { useState, useRef, useCallback, useEffect } from "react";
import CameraView from "./components/CameraView";
import DetectionOverlay from "./components/DetectionOverlay";
import MemoryCard from "./components/MemoryCard";
import Controls from "./components/Controls";
import { loadModel, detect, SUPPORTED_OBJECTS } from "./services/detection";
import { fetchMemory } from "./services/memoryApi";
import "./App.css";

/** How long a label must be stably detected before we surface the memory */
const STABLE_THRESHOLD_MS = 700;
/** Minimum time between detection runs */
const DETECT_INTERVAL_MS = 300;

export default function App() {
  const webcamRef = useRef(null);
  const stableTimerRef = useRef(null);
  const lastStableLabelRef = useRef(null);
  const runningRef = useRef(false);

  const [cameraReady, setCameraReady] = useState(false);
  const [modelReady, setModelReady] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const [selectedLabel, setSelectedLabel] = useState(SUPPORTED_OBJECTS[0]);
  const [detections, setDetections] = useState([]);
  const [activeMemory, setActiveMemory] = useState(null); // { label, memory, position }
  const [videoSize, setVideoSize] = useState({ w: 0, h: 0 });

  // ───────────────── Load model on mount ─────────────────
  useEffect(() => {
    let cancelled = false;
    loadModel()
      .then(() => {
        if (!cancelled) setModelReady(true);
      })
      .catch(() => {
        console.warn("Model failed to load — use Demo Mode as fallback");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // ───────────────── Detection loop ─────────────────
  useEffect(() => {
    if (demoMode || !modelReady || !cameraReady) return;

    let animId;
    runningRef.current = true;

    const loop = async () => {
      if (!runningRef.current) return;

      const video = webcamRef.current?.video;
      if (video && video.readyState >= 2) {
        // Keep videoSize in sync
        if (video.videoWidth && video.videoHeight) {
          setVideoSize({ w: video.videoWidth, h: video.videoHeight });
        }

        try {
          const results = await detect(video);
          setDetections(results);

          // Stability logic: pick the highest-confidence supported detection
          const best = results.length > 0 ? results[0] : null;
          const bestLabel = best?.label ?? null;

          if (bestLabel !== lastStableLabelRef.current) {
            lastStableLabelRef.current = bestLabel;
            clearTimeout(stableTimerRef.current);

            if (bestLabel) {
              stableTimerRef.current = setTimeout(() => {
                triggerMemory(bestLabel, best.bbox);
              }, STABLE_THRESHOLD_MS);
            }
          }
        } catch {
          // detection error — skip frame
        }
      }

      if (runningRef.current) {
        animId = setTimeout(() => {
          requestAnimationFrame(loop);
        }, DETECT_INTERVAL_MS);
      }
    };

    requestAnimationFrame(loop);

    return () => {
      runningRef.current = false;
      clearTimeout(animId);
      clearTimeout(stableTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demoMode, modelReady, cameraReady]);

  // ───────────────── Trigger memory (shared by detection + demo mode) ─────
  const triggerMemory = useCallback(async (label, bbox) => {
    const memory = await fetchMemory(label);
    if (!memory) return;

    // Compute card position relative to viewport (rough)
    let position = { top: 90, left: 24 };
    if (bbox) {
      const [x, y] = bbox;
      // Place card offset from bbox — scaled from video to viewport
      const video = webcamRef.current?.video;
      if (video) {
        const scaleX = window.innerWidth / (video.videoWidth || 1);
        const scaleY = window.innerHeight / (video.videoHeight || 1);
        position = {
          top: Math.min(Math.max(y * scaleY, 20), window.innerHeight - 260),
          left: Math.min(Math.max(x * scaleX + 16, 16), window.innerWidth - 340),
        };
      }
    }

    setActiveMemory({ label, memory, position });
  }, []);

  // ───────────────── Demo mode trigger ─────
  const handleDemoTrigger = useCallback(() => {
    triggerMemory(selectedLabel, null);
  }, [selectedLabel, triggerMemory]);

  const handleToggleDemo = useCallback(() => {
    setDemoMode((prev) => !prev);
    setDetections([]);
    setActiveMemory(null);
    lastStableLabelRef.current = null;
  }, []);

  const handleCloseMemory = useCallback(() => {
    setActiveMemory(null);
    lastStableLabelRef.current = null;
  }, []);

  return (
    <div className="app">
      {/* Camera */}
      <CameraView ref={webcamRef} onReady={() => setCameraReady(true)} />

      {/* Detection overlay */}
      <DetectionOverlay
        detections={detections}
        videoWidth={videoSize.w}
        videoHeight={videoSize.h}
      />

      {/* Memory card */}
      {activeMemory && (
        <MemoryCard
          label={activeMemory.label}
          memory={activeMemory.memory}
          position={activeMemory.position}
          onClose={handleCloseMemory}
        />
      )}

      {/* Top bar */}
      <header className="top-bar">
        <h1 className="top-bar__title">Memory Anchors</h1>
        <p className="top-bar__tagline">Memories attached to the real world.</p>
      </header>

      {/* Controls (bottom) */}
      <Controls
        demoMode={demoMode}
        onToggleDemo={handleToggleDemo}
        selectedLabel={selectedLabel}
        onSelectLabel={setSelectedLabel}
        onTrigger={handleDemoTrigger}
        modelReady={modelReady}
      />
    </div>
  );
}
