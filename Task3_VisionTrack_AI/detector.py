import os
import torch
import logging
from ultralytics import YOLO
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("YOLODetector")


class YOLODetector:
    def __init__(self, model_name=config.DEFAULT_MODEL, models_dir=config.MODELS_DIR):
        """
        Initialize the YOLO object detector.
        Automatically checks GPU/CUDA availability and downloads pretrained weights.
        """
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)

        # Detect CUDA / CPU device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing YOLODetector on device: {self.device.upper()}")

        self.model_name = model_name
        self.model_path = os.path.join(self.models_dir, model_name)

        # Load model with fallback handling
        self.model = self._load_model()
        self.names = self.model.names if hasattr(self.model, "names") else {}

    def _load_model(self):
        """
        Load YOLO model, downloading to models_dir if missing.
        """
        target_path = self.model_path if os.path.exists(self.model_path) else self.model_name
        try:
            logger.info(f"Loading YOLO model from: {target_path}")
            model = YOLO(target_path)

            # Move model to detected device
            model.to(self.device)

            # Save weights to local models/ folder if downloaded to default path
            if not os.path.exists(self.model_path) and hasattr(model, "ckpt_path"):
                try:
                    import shutil
                    if os.path.exists(model.ckpt_path):
                        shutil.copy(model.ckpt_path, self.model_path)
                        logger.info(f"Saved pretrained weights to {self.model_path}")
                except Exception as e:
                    logger.warning(f"Could not copy model to models dir: {e}")

            return model
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}. Trying fallback models...")
            for fallback in config.FALLBACK_MODELS:
                try:
                    fallback_path = os.path.join(self.models_dir, fallback)
                    src = fallback_path if os.path.exists(fallback_path) else fallback
                    logger.info(f"Attempting fallback model: {src}")
                    model = YOLO(src)
                    model.to(self.device)
                    self.model_name = fallback
                    return model
                except Exception as fe:
                    logger.error(f"Fallback {fallback} failed: {fe}")
            raise RuntimeError(f"Could not load any YOLO model. Error: {e}")

    def detect(self, frame, confidence_threshold=config.DEFAULT_CONFIDENCE, class_filter=None):
        """
        Run YOLO object detection on a frame.

        Parameters:
            frame (numpy.ndarray): OpenCV BGR frame.
            confidence_threshold (float): Minimum confidence threshold (0.1 to 0.9).
            class_filter (list of str, optional): List of class names to include.

        Returns:
            list of dict: List of detected objects with bbox, confidence, class_id, class_name.
        """
        if frame is None or frame.size == 0:
            return []

        # Run inference
        results = self.model.predict(
            source=frame,
            conf=confidence_threshold,
            device=self.device,
            verbose=False
        )

        detections = []

        if len(results) > 0:
            result = results[0]
            boxes = result.boxes

            for box in boxes:
                # Extract coordinates
                xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                x1, y1, x2, y2 = float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])

                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self.names.get(cls_id, str(cls_id))

                # Apply class filter if specified
                if class_filter is not None and len(class_filter) > 0:
                    if cls_name.lower() not in [c.lower() for c in class_filter]:
                        continue

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(conf, 4),
                    "class_id": cls_id,
                    "class_name": cls_name
                })

        return detections

    def get_device(self):
        return self.device.upper()
