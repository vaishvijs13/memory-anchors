# Memory Anchors

**Memories attached to the real world.**

A hackathon demo for Alzheimer's support — the home becomes a memory interface. Point your camera at household objects and see personal memories overlaid in real time.

---

## Quick Start

```bash
# Install dependencies
npm install

# Start the dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in Chrome (recommended) and allow camera access.

## How It Works

1. **Camera** — The app opens a full-screen camera feed via `react-webcam`.
2. **Object Detection** — TensorFlow.js COCO-SSD runs on each frame, looking for supported household objects.
3. **Memory Overlay** — When a supported object is stably detected (~0.7 s), a floating Memory Card appears with a personal memory and a Play button for voice narration.
4. **Demo Mode** — If object detection is unreliable (lighting, angles, etc.), flip on **Demo Mode** to manually select an object and trigger the memory overlay.

## Supported Objects

| Label    | Why                                   |
| -------- | ------------------------------------- |
| `chair`  | Very reliably detected by COCO-SSD   |
| `book`   | Common household object               |
| `tv`     | Large, easy to detect                 |
| `laptop` | Fallback if fridge not detected well  |

## Project Structure

```
src/
├── components/
│   ├── CameraView.jsx        # Webcam feed (full-screen)
│   ├── DetectionOverlay.jsx   # Canvas bounding-box drawing
│   ├── MemoryCard.jsx         # Floating memory card UI
│   └── Controls.jsx           # Demo Mode toggle + dropdown
├── services/
│   ├── detection.js           # TF.js COCO-SSD loader & detect()
│   └── memoryApi.js           # API fetch + local fallback memories
├── App.jsx                    # Main app (state, detection loop)
├── App.css                    # All styles
├── index.css                  # Global reset
└── main.jsx                   # Entry point
```

## Backend API (Optional)

The app tries to fetch memories from:

```
GET {VITE_API_BASE}/memory/{object_label}
```

Set `VITE_API_BASE` in a `.env` file (defaults to `http://localhost:8000`).

Expected response:
```json
{ "title": "...", "text": "..." }
```

If the API is unreachable, the app gracefully falls back to built-in local memories.

## Voice Narration

- If `window.VoiceService.playMemory(text)` exists, the Play button calls it.
- Otherwise, the browser's built-in `SpeechSynthesis` API is used as a fallback.

## Tech Stack

- **React + Vite** — Fast dev experience
- **react-webcam** — Camera access
- **TensorFlow.js + COCO-SSD** — Client-side object detection
- **Canvas API** — Bounding box overlays
- **CSS** — Custom high-contrast healthcare-style UI (no UI library)

## Tips for Demo Day

- Use **Chrome** for best TF.js + camera support.
- Good lighting helps detection accuracy significantly.
- If detection is flaky, switch to **Demo Mode** — it's designed exactly for this.
- The model (`lite_mobilenet_v2`) loads in ~2–5 seconds on a decent machine.
