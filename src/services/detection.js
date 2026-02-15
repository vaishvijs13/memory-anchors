import * as tf from "@tensorflow/tfjs";
import * as cocoSsd from "@tensorflow-models/coco-ssd";

let model = null;
let isLoading = false;

/**
 * Supported object labels for the Memory Anchors demo.
 * These are COCO-SSD labels that detect reliably.
 */
export const SUPPORTED_OBJECTS = ["chair", "book", "tv", "laptop"];

/**
 * Load the COCO-SSD model. Returns the model instance.
 * Caches after first load.
 */
export async function loadModel() {
  if (model) return model;
  if (isLoading) {
    // Wait for the in-flight load to finish
    while (isLoading) {
      await new Promise((r) => setTimeout(r, 100));
    }
    return model;
  }

  isLoading = true;
  try {
    await tf.ready();
    model = await cocoSsd.load({ base: "lite_mobilenet_v2" });
    console.log("[detection] COCO-SSD model loaded");
    return model;
  } catch (err) {
    console.error("[detection] Failed to load model:", err);
    throw err;
  } finally {
    isLoading = false;
  }
}

/**
 * Run detection on a video element.
 * Returns array of { label, score, bbox: [x, y, width, height] }
 * filtered to only supported objects above the confidence threshold.
 */
export async function detect(videoElement, minScore = 0.45) {
  if (!model) {
    throw new Error("Model not loaded. Call loadModel() first.");
  }

  const predictions = await model.detect(videoElement);

  return predictions
    .filter(
      (p) =>
        SUPPORTED_OBJECTS.includes(p.class) && p.score >= minScore
    )
    .map((p) => ({
      label: p.class,
      score: p.score,
      bbox: p.bbox, // [x, y, width, height]
    }));
}
