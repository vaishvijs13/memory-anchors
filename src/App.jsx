import { useState, useRef, useCallback, useEffect } from "react";
import CameraView from "./components/CameraView";
import DetectionOverlay from "./components/DetectionOverlay";
import MemoryCard from "./components/MemoryCard";
import MemoryUpload from "./components/MemoryUpload";
import SystemHUD from "./components/SystemHUD";
import Controls from "./components/Controls";
import { loadModel, detect, SUPPORTED_OBJECTS } from "./services/detection";
import { fetchMemory } from "./services/memoryApi";
import "./App.css";

const STABLE_THRESHOLD_MS = 700;
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
  const [activeMemory, setActiveMemory] = useState(null);
  const [videoSize, setVideoSize] = useState({ w: 0, h: 0 });
  const [showUpload, setShowUpload] = useState(false);

  // Load model on mount
  useEffect(() => {
    let cancelled = false;
    loadModel()
      .then(() => {
        if (!cancelled) setModelReady(true);
      })
      .catch(() => {
        console.warn("[SYS] Model failed to load — use Demo Mode");
      });
    return () => { cancelled = true; };
  }, []);

  // Detection loop
  useEffect(() => {
    if (demoMode || !modelReady || !cameraReady) return;

    let animId;
    runningRef.current = true;

    const loop = async () => {
      if (!runningRef.current) return;

      const video = webcamRef.current?.video;
      if (video && video.readyState >= 2) {
        if (video.videoWidth && video.videoHeight) {
          setVideoSize({ w: video.videoWidth, h: video.videoHeight });
        }

        try {
          const results = await detect(video);
          setDetections(results);

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
          // detection error
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
  }, [demoMode, modelReady, cameraReady]);

  const triggerMemory = useCallback(async (label, bbox) => {
    const memory = await fetchMemory(label);
    if (!memory) return;

    let position = { top: 90, left: 24 };
    if (bbox) {
      const [x, y] = bbox;
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
      <CameraView ref={webcamRef} onReady={() => setCameraReady(true)} />

      <DetectionOverlay
        detections={detections}
        videoWidth={videoSize.w}
        videoHeight={videoSize.h}
      />

      <SystemHUD
        modelReady={modelReady}
        cameraReady={cameraReady}
        detectionCount={detections.length}
      />

      {activeMemory && (
        <MemoryCard
          label={activeMemory.label}
          memory={activeMemory.memory}
          position={activeMemory.position}
          onClose={handleCloseMemory}
        />
      )}

      {showUpload && (
        <MemoryUpload
          onClose={() => setShowUpload(false)}
          onSaved={() => setShowUpload(false)}
        />
      )}

      <header className="top-bar">
        <div className="top-bar__brand">
          <svg className="top-bar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          <h1 className="top-bar__title">Memory Anchors</h1>
        </div>
        <p className="top-bar__tagline">Spatial Memory Interface</p>
      </header>

      <Controls
        demoMode={demoMode}
        onToggleDemo={handleToggleDemo}
        selectedLabel={selectedLabel}
        onSelectLabel={setSelectedLabel}
        onTrigger={handleDemoTrigger}
        modelReady={modelReady}
        onUpload={() => setShowUpload(true)}
      />
    </div>
  );
}
