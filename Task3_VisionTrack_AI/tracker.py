import logging
try:
    import pkg_resources
except ImportError:
    pass
from deep_sort_realtime.deepsort_tracker import DeepSort
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepSORTTracker")


class DeepSORTTracker:
    def __init__(self, max_age=config.DEEPSORT_MAX_AGE, n_init=config.DEEPSORT_N_INIT, max_cosine_distance=config.DEEPSORT_MAX_COSINE_DISTANCE):
        """
        Initialize Deep SORT Tracker using deep-sort-realtime.
        """
        self.max_age = max_age
        self.n_init = n_init
        self.max_cosine_distance = max_cosine_distance
        self.tracker = self._init_tracker()

    def _init_tracker(self):
        logger.info(f"Initializing Deep SORT Tracker (max_age={self.max_age}, n_init={self.n_init})")
        return DeepSort(
            max_age=self.max_age,
            n_init=self.n_init,
            max_cosine_distance=self.max_cosine_distance,
            override_track_class=None,
            embedder="mobilenet",
            half=False,
            bgr=True
        )

    def update(self, detections, frame):
        """
        Update Deep SORT tracks with new YOLO detections.

        Parameters:
            detections (list of dict): Detections from YOLODetector.
            frame (numpy.ndarray): Current video frame (BGR).

        Returns:
            list of dict: Confirmed active tracks containing track_id, bbox, class_name, confidence.
        """
        if frame is None:
            return []

        # Convert YOLO detections to Deep SORT format: ([left, top, w, h], confidence, class_name)
        raw_detections = []
        for det in detections:
            bbox = det["bbox"]  # [x1, y1, x2, y2]
            x1, y1, x2, y2 = bbox
            w = max(0, x2 - x1)
            h = max(0, y2 - y1)
            conf = det["confidence"]
            cls_name = det["class_name"]
            raw_detections.append(([x1, y1, w, h], conf, cls_name))

        # Update Deep SORT tracks
        tracks = self.tracker.update_tracks(raw_detections, frame=frame)

        active_tracks = []
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            track_id = track.track_id
            try:
                # Convert string track_id to integer if possible for clean formatting
                track_id_val = int(track_id)
            except (ValueError, TypeError):
                track_id_val = track_id

            # Extract bounding box in [x1, y1, x2, y2] format
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = float(ltrb[0]), float(ltrb[1]), float(ltrb[2]), float(ltrb[3])

            class_name = track.get_det_class()
            if not class_name or class_name == "None":
                class_name = "object"

            confidence = track.get_det_conf()
            if confidence is None:
                confidence = 0.90  # Default display conf if track maintained across occlusion

            active_tracks.append({
                "track_id": track_id_val,
                "bbox": [x1, y1, x2, y2],
                "class_name": class_name,
                "confidence": round(float(confidence), 2)
            })

        return active_tracks

    def reset(self):
        """Reset tracking state for a new stream session."""
        logger.info("Resetting Deep SORT Tracker state.")
        self.tracker = self._init_tracker()
