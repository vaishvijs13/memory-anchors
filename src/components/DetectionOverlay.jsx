import { useEffect, useRef } from "react";

/**
 * Canvas overlay that draws bounding boxes and labels
 * on top of the camera feed.
 *
 * Props:
 *  - detections: [{ label, score, bbox: [x, y, w, h] }]
 *  - videoWidth / videoHeight: natural size of the video feed
 */
export default function DetectionOverlay({
  detections,
  videoWidth,
  videoHeight,
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    canvas.width = videoWidth || canvas.clientWidth;
    canvas.height = videoHeight || canvas.clientHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!detections || detections.length === 0) return;

    detections.forEach(({ label, score, bbox }) => {
      const [x, y, w, h] = bbox;

      // Bounding box
      ctx.strokeStyle = "#00e5ff";
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);

      // Label background
      const text = `${label} ${Math.round(score * 100)}%`;
      ctx.font = "bold 16px Inter, system-ui, sans-serif";
      const tm = ctx.measureText(text);
      const padding = 6;
      const labelH = 24;
      ctx.fillStyle = "rgba(0, 229, 255, 0.85)";
      ctx.fillRect(x, y - labelH - 2, tm.width + padding * 2, labelH);

      // Label text
      ctx.fillStyle = "#000";
      ctx.fillText(text, x + padding, y - 8);
    });
  }, [detections, videoWidth, videoHeight]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
    />
  );
}
