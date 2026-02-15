import { forwardRef, useCallback } from "react";
import Webcam from "react-webcam";

const videoConstraints = {
  facingMode: "environment",
  width: { ideal: 1280 },
  height: { ideal: 720 },
};

/**
 * Full-screen camera feed.
 * Forwards ref to the underlying <video> element (via Webcam).
 */
const CameraView = forwardRef(function CameraView({ onReady }, ref) {
  const handleUserMedia = useCallback(() => {
    if (onReady) onReady();
  }, [onReady]);

  return (
    <Webcam
      ref={ref}
      audio={false}
      videoConstraints={videoConstraints}
      onUserMedia={handleUserMedia}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        objectFit: "cover",
      }}
      playsInline
      muted
    />
  );
});

export default CameraView;
