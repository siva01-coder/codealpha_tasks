import cv2
import time
import os
import threading
import logging
from collections import deque, Counter
from datetime import datetime
import config
from detector import YOLODetector
from tracker import DeepSORTTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VideoProcessor")


class VideoProcessor:
    def __init__(self):
        self.lock = threading.Lock()
        self.detector = YOLODetector()
        self.tracker = DeepSORTTracker()

        # Processing state
        self.is_running = False
        self.source_type = "webcam"  # 'webcam' or 'upload'
        self.video_path = None
        self.cap = None

        # Configurable settings
        self.confidence_threshold = config.DEFAULT_CONFIDENCE
        self.class_filter = []
        self.show_trails = True

        # Metrics & Statistics
        self.current_fps = 0.0
        self.latency_ms = 0.0
        self.active_tracks_count = 0
        self.total_tracks_set = set()
        self.class_counts = {}
        self.recent_events = []
        self.error_message = None

        # Tracking trails: track_id -> deque of (cx, cy)
        self.track_trails = {}
        self.logged_track_ids = set()

        # Current processed frame (BGR image & encoded JPEG bytes)
        self.latest_bgr_frame = None
        self.latest_jpeg_frame = None

        # Optional Recording State
        self.is_recording = False
        self.video_writer = None
        self.recording_path = None

    def update_settings(self, confidence=None, class_filter=None, show_trails=None):
        """Thread-safe update of user settings."""
        with self.lock:
            if confidence is not None:
                self.confidence_threshold = max(config.CONFIDENCE_MIN, min(config.CONFIDENCE_MAX, float(confidence)))
            if class_filter is not None:
                self.class_filter = class_filter
            if show_trails is not None:
                self.show_trails = bool(show_trails)
            logger.info(f"Updated settings: conf={self.confidence_threshold}, filter={self.class_filter}, trails={self.show_trails}")

    def start(self, source_type="webcam", video_path=None):
        """Initialize video capture, reset tracker, and start processing stream."""
        with self.lock:
            self.stop_internal()

            self.source_type = source_type
            self.video_path = video_path
            self.error_message = None
            self.total_tracks_set.clear()
            self.track_trails.clear()
            self.logged_track_ids.clear()
            self.recent_events.clear()
            self.tracker.reset()

            if source_type == "webcam":
                # Try default webcam index 0
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    self.error_message = "Unable to access camera. Check camera permissions and ensure another application is not using it."
                    logger.error(self.error_message)
                    return False, self.error_message
            elif source_type == "upload":
                if not video_path or not os.path.exists(video_path):
                    self.error_message = f"Uploaded video file not found: {video_path}"
                    logger.error(self.error_message)
                    return False, self.error_message
                self.cap = cv2.VideoCapture(video_path)
                if not self.cap.isOpened():
                    self.error_message = "Failed to open video file. Invalid or unsupported format."
                    logger.error(self.error_message)
                    return False, self.error_message

            self.is_running = True
            self._add_event(f"Started analysis via {source_type.upper()}")
            logger.info(f"VideoProcessor started successfully ({source_type})")
            return True, "Success"

    def stop(self):
        """Public method to stop processing and release resources."""
        with self.lock:
            return self.stop_internal()

    def stop_internal(self):
        """Internal helper to clean up resources (must be called with or within lock)."""
        self.is_running = False
        if self.video_writer is not None:
            try:
                self.video_writer.release()
            except Exception:
                pass
            self.video_writer = None
            self.is_recording = False

        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        self.latest_bgr_frame = None
        self.latest_jpeg_frame = None
        self._add_event("Stopped analysis and released resources.")
        logger.info("VideoProcessor stopped successfully.")
        return True

    def _add_event(self, text):
        """Add timestamped event log item (keeps latest 20)."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"{timestamp} — {text}"
        self.recent_events.insert(0, entry)
        if len(self.recent_events) > 20:
            self.recent_events.pop()

    def start_recording(self):
        """Start saving processed stream to output MP4 file."""
        with self.lock:
            if not self.is_running or self.latest_bgr_frame is None:
                return False, "Stream must be active to start recording."
            
            h, w = self.latest_bgr_frame.shape[:2]
            filename = f"record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            filepath = os.path.join(config.OUTPUT_DIR, filename)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(filepath, fourcc, 20.0, (w, h))
            
            if not writer.isOpened():
                # Fallback to XVID / AVI if mp4v unavailable
                filename = f"record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
                filepath = os.path.join(config.OUTPUT_DIR, filename)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                writer = cv2.VideoWriter(filepath, fourcc, 20.0, (w, h))
                
            if not writer.isOpened():
                return False, "Could not initialize VideoWriter on server codecs."

            self.video_writer = writer
            self.recording_path = filepath
            self.is_recording = True
            self._add_event(f"Recording started: {os.path.basename(filepath)}")
            return True, os.path.basename(filepath)

    def stop_recording(self):
        """Stop video recording."""
        with self.lock:
            if not self.is_recording or self.video_writer is None:
                return False, "No active recording found."
            
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            rec_file = os.path.basename(self.recording_path) if self.recording_path else "video.mp4"
            self._add_event(f"Recording saved: {rec_file}")
            return True, rec_file

    def get_current_frame(self):
        """Get latest JPEG frame for snapshot download."""
        with self.lock:
            if self.latest_jpeg_frame is not None:
                return self.latest_jpeg_frame.tobytes()
            return None

    def get_status(self):
        """Return status and performance metrics for API polling."""
        with self.lock:
            return {
                "running": self.is_running,
                "source_type": self.source_type,
                "fps": round(self.current_fps, 1),
                "latency_ms": round(self.latency_ms, 1),
                "tracked_objects": self.active_tracks_count,
                "total_tracks": len(self.total_tracks_set),
                "confidence": round(self.confidence_threshold, 2),
                "show_trails": self.show_trails,
                "device": self.detector.get_device(),
                "classes": dict(self.class_counts),
                "recent_events": list(self.recent_events),
                "error": self.error_message,
                "is_recording": self.is_recording
            }

    def process_next_frame(self):
        """Reads frame, runs YOLO + Deep SORT, draws overlay, updates metrics."""
        if not self.is_running or self.cap is None:
            return None

        t0 = time.time()
        ret, frame = self.cap.read()

        if not ret or frame is None:
            if self.source_type == "upload":
                # Loop video when reaching end of uploaded video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.stop_internal()
                    return None
            else:
                self.error_message = "Camera disconnected or frame feed interrupted."
                self.stop_internal()
                return None

        # Resize large frame for fast inference while keeping original aspect ratio
        h_orig, w_orig = frame.shape[:2]
        max_dim = config.INFERENCE_MAX_DIM
        if max(h_orig, w_orig) > max_dim:
            scale = max_dim / float(max(h_orig, w_orig))
            w_new, h_new = int(w_orig * scale), int(h_orig * scale)
            frame_resized = cv2.resize(frame, (w_new, h_new), interpolation=cv2.INTER_AREA)
        else:
            frame_resized = frame.copy()
            scale = 1.0

        # Read settings with lock
        with self.lock:
            conf_thresh = self.confidence_threshold
            c_filter = list(self.class_filter)
            trails_enabled = self.show_trails

        # 1. Run YOLO Object Detection
        detections = self.detector.detect(frame_resized, confidence_threshold=conf_thresh, class_filter=c_filter)

        # Scale detection boxes back if resized
        if scale != 1.0 and scale > 0:
            for det in detections:
                det["bbox"] = [
                    det["bbox"][0] / scale,
                    det["bbox"][1] / scale,
                    det["bbox"][2] / scale,
                    det["bbox"][3] / scale
                ]

        # 2. Run Deep SORT Tracker
        active_tracks = self.tracker.update(detections, frame)

        # 3. Process Overlay & Statistics
        annotated_frame = frame.copy()
        current_active_ids = set()
        current_classes = []

        for trk in active_tracks:
            tid = trk["track_id"]
            bbox = trk["bbox"]  # [x1, y1, x2, y2]
            cls_name = trk["class_name"]
            conf = trk["confidence"]

            current_active_ids.add(tid)
            self.total_tracks_set.add(tid)
            current_classes.append(cls_name)

            # Log event for newly discovered track ID
            if tid not in self.logged_track_ids:
                self.logged_track_ids.add(tid)
                self._add_event(f"{cls_name.capitalize()} ID {tid} detected")

            # Clamp coordinates to frame limits
            x1 = int(max(0, min(w_orig - 1, bbox[0])))
            y1 = int(max(0, min(h_orig - 1, bbox[1])))
            x2 = int(max(0, min(w_orig - 1, bbox[2])))
            y2 = int(max(0, min(h_orig - 1, bbox[3])))

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # Store track center points for motion trail
            if tid not in self.track_trails:
                self.track_trails[tid] = deque(maxlen=25)
            self.track_trails[tid].append((cx, cy))

            # Render tracking trail if enabled
            if trails_enabled and len(self.track_trails[tid]) > 1:
                points = list(self.track_trails[tid])
                for i in range(1, len(points)):
                    thickness = int(max(1, (i / len(points)) * 3))
                    cv2.line(annotated_frame, points[i - 1], points[i], (255, 255, 255), thickness)
                    # Small dot at node
                    cv2.circle(annotated_frame, points[i], 2, (200, 200, 200), -1)

            # Draw sleek monochrome Bounding Box (white borders, subtle inner corners)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
            # Corner accents for sleek modern UI look
            corner_len = min(15, (x2 - x1) // 4, (y2 - y1) // 4)
            if corner_len > 0:
                # Top-Left corner
                cv2.line(annotated_frame, (x1, y1), (x1 + corner_len, y1), (255, 255, 255), 3)
                cv2.line(annotated_frame, (x1, y1), (x1, y1 + corner_len), (255, 255, 255), 3)
                # Bottom-Right corner
                cv2.line(annotated_frame, (x2, y2), (x2 - corner_len, y2), (255, 255, 255), 3)
                cv2.line(annotated_frame, (x2, y2), (x2, y2 - corner_len), (255, 255, 255), 3)

            # Prepare Label Text
            line1 = f"{cls_name.upper()}"
            line2 = f"ID: {tid}  {int(conf * 100)}%"

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            
            (w1, h1), _ = cv2.getTextSize(line1, font, font_scale, thickness)
            (w2, h2), _ = cv2.getTextSize(line2, font, font_scale, thickness)
            
            label_w = max(w1, w2) + 16
            label_h = h1 + h2 + 16

            # Label box placement (clamped above bbox or inside frame)
            lbl_x1 = x1
            lbl_y1 = max(0, y1 - label_h)
            lbl_x2 = min(w_orig, lbl_x1 + label_w)
            lbl_y2 = lbl_y1 + label_h

            # Draw background panel for label (#0D0D0D background)
            cv2.rectangle(annotated_frame, (lbl_x1, lbl_y1), (lbl_x2, lbl_y2), (13, 13, 13), -1)
            cv2.rectangle(annotated_frame, (lbl_x1, lbl_y1), (lbl_x2, lbl_y2), (255, 255, 255), 1)

            # Draw Text
            cv2.putText(annotated_frame, line1, (lbl_x1 + 8, lbl_y1 + h1 + 4), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            cv2.putText(annotated_frame, line2, (lbl_x1 + 8, lbl_y1 + h1 + h2 + 10), font, font_scale, (180, 180, 180), thickness, cv2.LINE_AA)

        # Remove stale track trails for tracks that disappeared
        stale_tids = [tid for tid in self.track_trails if tid not in current_active_ids]
        for tid in stale_tids:
            del self.track_trails[tid]

        # Compute frame latency and FPS
        t1 = time.time()
        elapsed = t1 - t0
        fps = 1.0 / elapsed if elapsed > 0 else 30.0
        
        # Exponential moving average smoothing for FPS
        self.current_fps = (0.8 * self.current_fps + 0.2 * fps) if self.current_fps > 0 else fps
        self.latency_ms = elapsed * 1000.0

        # Update metrics state
        with self.lock:
            self.active_tracks_count = len(current_active_ids)
            self.class_counts = dict(Counter(current_classes))
            self.latest_bgr_frame = annotated_frame.copy()

            # Encode frame to JPEG
            ret_encode, jpeg_buf = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if ret_encode:
                self.latest_jpeg_frame = jpeg_buf

            # Save to video writer if recording
            if self.is_recording and self.video_writer is not None:
                try:
                    self.video_writer.write(annotated_frame)
                except Exception as e:
                    logger.error(f"Error writing frame to recording: {e}")

        return self.latest_jpeg_frame

    def generate_frames(self):
        """MJPEG generator yielding multipart JPEG frames for Flask video stream."""
        while True:
            if not self.is_running:
                # Return placeholder offline image or wait
                time.sleep(0.1)
                with self.lock:
                    if not self.is_running:
                        break
                continue

            frame_buf = self.process_next_frame()
            if frame_buf is None:
                time.sleep(0.03)
                continue

            frame_bytes = frame_buf.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Short sleep to prevent spinning CPU in loop
            time.sleep(0.01)
