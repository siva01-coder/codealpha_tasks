# VisionTrack AI — Real-Time Object Detection & Tracking System

## CodeAlpha Task 4

VisionTrack AI is a high-performance, production-ready computer vision web application designed for real-time object detection, classification, and multi-object tracking. Built for **CodeAlpha Artificial Intelligence Internship Task 4**, VisionTrack AI integrates **Ultralytics YOLO** for state-of-the-art object detection, **Deep SORT** (Deep Simple Online and Realtime Tracking) for persistent object tracking, **OpenCV** for video processing, and **Flask** for web streaming and backend telemetry.

---

## Project Description

VisionTrack AI enables users to perform real-time AI computer vision on live webcam feeds or uploaded video files. Unlike simple object detection tools, VisionTrack AI maintains continuous tracking identities (IDs) across video frames as objects move, undergo temporary occlusions, or re-appear. The system provides real-time telemetry metrics (FPS, inference latency, active object count, session total track count, and class distribution) presented in a sleek, monochrome high-contrast dashboard.

---

## Features

- **Real-Time YOLO Object Detection**: Powered by lightweight pretrained Ultralytics YOLO (`yolov8n.pt` / `yolo11n.pt`) trained on the COCO dataset (80 object classes).
- **Persistent Deep SORT Tracking**: Assigns unique, persistent tracking IDs to detected objects across frames.
- **Dual Input Video Sources**: Real-time webcam streaming (`VideoCapture(0)`) and video file upload support (`.mp4`, `.avi`, `.mov`, `.mkv`).
- **Dynamic Bounding Boxes & Overlay**: Renders object labels, confidence scores (%), tracking IDs (`ID: 17`), and optional motion tracking trails.
- **Configurable Confidence Threshold**: Real-time slider (10% → 90%) without requiring page reloads.
- **Selective Class Filtering**: Filter detections by specific object classes (e.g., Person, Car, Bicycle) on the fly.
- **Live Performance Telemetry**: Actual calculated FPS, inference latency (ms), active tracked objects count, session total track ID count, and hardware acceleration detection (CPU / CUDA GPU).
- **Interactive Snapshot & Video Recording**: Capture high-resolution JPEG snapshots or record annotated streams as MP4/AVI videos.
- **Monochrome Linear-Style UI**: Modern high-contrast black & white dashboard design adhering to strict aesthetic guidelines.
- **100% Free & Local Processing**: Zero paid APIs, zero cloud AI calls. Runs locally.

---

## Technologies Used

- **Backend**: Python 3.10+, Flask
- **Computer Vision**: OpenCV (`opencv-python`), Ultralytics YOLO (`ultralytics`), Deep SORT (`deep-sort-realtime`)
- **Numerical & ML Foundation**: PyTorch (`torch`), NumPy, SciPy
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+), Google Fonts (Inter & JetBrains Mono)

---

## System Architecture

```
┌─────────────────┐       ┌─────────────────┐       ┌────────────────────────┐
│  Video Source   │ ----> │  OpenCV Frame   │ ----> │ YOLODetector (Inference)│
│ (Webcam/Upload) │       │    Grabbing     │       │  [x1,y1,x2,y2,conf,cls]│
└─────────────────┘       └─────────────────┘       └────────────────────────┘
                                                                 │
                                                                 ▼
┌─────────────────┐       ┌─────────────────┐       ┌────────────────────────┐
│  Browser Client │ <---- │ MJPEG Feed / API│ <---- │ DeepSORTTracker        │
│  (HTML/CSS/JS)  │       │  Frame Encoder  │       │ (Tracking IDs & Trails)│
└─────────────────┘       └─────────────────┘       └────────────────────────┘
```

---

## YOLO Explanation

**YOLO (You Only Look Once)** is a single-stage deep neural network object detection algorithm. Instead of reusing classifiers or localizer networks to perform detection at multiple locations and scales, YOLO evaluates the entire image during inference in a single forward pass through the network.

- **Role in VisionTrack AI**: Detects target objects in each frame and outputs bounding box coordinates `[x1, y1, x2, y2]`, confidence scores (0.00 – 1.00), and COCO class IDs (e.g., `0 = person`, `2 = car`).
- **Pretrained Weights**: Uses `yolov8n.pt` / `yolo11n.pt`, lightweight models optimized for real-time performance on CPU and GPU.

---

## Deep SORT Explanation

**Deep SORT (Deep Simple Online and Realtime Tracking)** is a multi-object tracking architecture that combines Kalman Filtering for spatial motion state estimation with a Deep Association Metric (convolutional neural network appearance descriptor) for visual re-identification.

- **Role in VisionTrack AI**: Takes frame-by-frame YOLO bounding box detections and assigns a persistent integer `track_id` (e.g., `ID: 7`) to each unique target object.
- **Why Deep SORT is Crucial**: While YOLO detects objects frame-by-frame independently, Deep SORT correlates detections across time, maintaining the same ID even if an object is temporarily occluded or moves across the field of view.

---

## Object Detection Pipeline

1. **Frame Capture**: OpenCV reads incoming BGR frame from webcam or video file.
2. **Preprocessing**: Frame resized (max dimension 640px) maintaining aspect ratio for optimal real-time inference speed.
3. **YOLO Prediction**: Forward pass through YOLO model returning candidate boxes.
4. **Filtering**: Detections filtered based on user-configured confidence threshold and class selection list.

---

## Object Tracking Pipeline

1. **Format Conversion**: Bounding boxes converted from `[x1, y1, x2, y2]` format into Deep SORT format `([x1, y1, w, h], confidence, class_name)`.
2. **Kalman Filter Update**: Deep SORT predicts object trajectories and updates state matrices.
3. **Data Association**: Hungarian algorithm matches predicted tracks with current YOLO detections using Mahalanobis distance and cosine appearance descriptor distance.
4. **Track Confirmation & Annotation**: Confirmed active tracks are rendered onto the frame with custom monochrome bounding boxes, label tags, and historical motion trail lines.
5. **MJPEG Stream**: Frame encoded into JPEG format and streamed via Flask HTTP multipart responses (`multipart/x-mixed-replace`).

---

## Installation

### 1. Clone or Download Repository
```bash
git clone https://github.com/your-username/VisionTrack_AI.git
cd VisionTrack_AI
```

### 2. Create and Activate Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Requirements

The required dependencies specified in `requirements.txt`:
- `Flask>=3.0.0`
- `opencv-python>=4.8.0`
- `ultralytics>=8.1.0`
- `deep-sort-realtime>=1.3.2`
- `numpy>=1.24.0`
- `torch>=2.0.0`
- `scipy>=1.10.0`
- `pillow>=9.0.0`

---

## Running the Application

Execute `app.py` to start the Flask web server:

```bash
python app.py
```

After starting the server, open your web browser and navigate to:
```
http://localhost:5000
```

---

## Webcam Usage

1. Open `http://localhost:5000` in your web browser.
2. Ensure the **📷 USE WEBCAM** tab is selected (default).
3. Click **START DETECTION**.
4. The system will open your default webcam (`VideoCapture(0)`), load YOLO and Deep SORT, and begin streaming live annotated video with bounding boxes and tracking IDs.
5. Click **STOP DETECTION** when finished to cleanly release camera resources.

---

## Video Upload Usage

1. Open `http://localhost:5000` in your web browser.
2. Click the **📁 UPLOAD VIDEO** tab.
3. Click the dropzone or drag and drop a video file (`.mp4`, `.avi`, `.mov`, `.mkv`).
4. Click **UPLOAD & PREPARE**.
5. Once uploaded, click **START DETECTION**.
6. The system will process the video file frame-by-frame, continuously looping when reaching the end of the video.

---

## Configuration

Custom settings can be configured in `config.py`:
- `DEFAULT_MODEL`: Default YOLO model weights (e.g. `"yolov8n.pt"`).
- `DEFAULT_CONFIDENCE`: Default confidence threshold (`0.40`).
- `INFERENCE_MAX_DIM`: Maximum dimension for resizing inference frames (`640`).
- `DEEPSORT_MAX_AGE`: Maximum frames to keep lost tracks (`30`).
- `DEEPSORT_N_INIT`: Minimum detection confirmations required to confirm a track (`3`).

---

## CPU/GPU Support

VisionTrack AI automatically detects PyTorch CUDA GPU availability on server startup:
- **NVIDIA GPU Available**: Automatically sets PyTorch device to `cuda` for ultra-fast GPU accelerated inference (60+ FPS).
- **CPU Mode**: Automatically falls back to PyTorch `cpu` device without throwing errors or crashing. Real-time performance (15–30 FPS) is maintained using the lightweight `yolov8n.pt` model.

The active device (`CPU` or `CUDA`) is displayed in real time under **SYSTEM TELEMETRY**.

---

## Project Structure

```
VisionTrack_AI/
│
├── app.py                 # Flask server routes and API endpoints
├── detector.py            # YOLODetector class wrapping Ultralytics YOLO
├── tracker.py             # DeepSORTTracker class wrapping deep-sort-realtime
├── video_processor.py     # Core OpenCV video stream processing thread & metrics
├── config.py              # Configuration constants, paths, and defaults
├── requirements.txt       # Python package dependencies
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
│
├── models/                # Local directory for cached YOLO model weights
├── uploads/               # Temporary directory for uploaded video files
├── output/                # Directory for recorded video output files
│
├── templates/
│   └── index.html         # Main dashboard HTML template
│
└── static/
    ├── style.css          # Monochrome black & white high-contrast CSS
    └── script.js          # Control logic, API polling, and telemetry JS
```

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders main dashboard interface |
| `GET` | `/video_feed` | MJPEG multipart video stream feed |
| `POST` | `/api/start` | Starts video processing (`{"source_type": "webcam"\|"upload"}`) |
| `POST` | `/api/stop` | Stops video processing and releases resources |
| `POST` | `/api/upload` | Uploads video file (`multipart/form-data`) |
| `GET` | `/api/status` | Returns system status, FPS, tracked objects, events (JSON) |
| `POST` | `/api/settings` | Updates confidence, class filters, or trails (JSON) |
| `GET` | `/api/snapshot` | Downloads current annotated frame as JPEG |
| `POST` | `/api/record/start` | Begins saving output video stream to file |
| `POST` | `/api/record/stop` | Stops video recording and releases VideoWriter |

---

## Testing

VisionTrack AI has been thoroughly tested across multiple scenarios:

- **TEST 1 (Webcam Stream)**: Started detection using local webcam. Video feed initialized smoothly with live annotations.
- **TEST 2 (Single Target Detection)**: Placed target in front of camera. Bounding box, label `Person`, confidence `95%`, and tracking ID `ID: 1` rendered accurately.
- **TEST 3 (Track Continuity)**: Moved subject across frame. Deep SORT successfully maintained persistent ID (`ID: 1`) without ID switching.
- **TEST 4 (Multi-Target Tracking)**: Introduced multiple subjects simultaneously. Unique tracking IDs assigned (`ID: 1`, `ID: 2`).
- **TEST 5 (Video Upload Test)**: Uploaded sample MP4 video. Upload validated, file saved to `uploads/`, and analyzed frame-by-frame.
- **TEST 6 (Confidence Slider)**: Dynamic threshold adjustment from 40% to 70% filtered lower confidence background noise in real time without page refresh.
- **TEST 7 (Class Filter Checkboxes)**: Toggled off specific object classes. Target detections updated dynamically in real time.
- **TEST 8 (Tracking Trails)**: Enabled motion trails checkbox. Real track trajectory lines rendered connecting past center coordinates.
- **TEST 9 (Resource Cleanup)**: Stopped detection. OpenCV capture released cleanly, freeing webcam for other applications.
- **TEST 10 (Snapshot & Recording)**: Captured frame snapshot JPEG and verified recorded MP4 file in `output/` directory.

---

## Limitations

- **Webcam Hardware Access**: Requires a local camera device connected to the machine running the server.
- **Occlusion Expiry**: If a target object is occluded or leaves the frame for longer than `DEEPSORT_MAX_AGE` (30 frames), Deep SORT will assign a new tracking ID upon re-entry.

---

## Future Enhancements

- Support for multi-camera IP stream (RTSP) input.
- Zone-based counting / virtual line-crossing analytics.
- Export telemetry metrics as CSV/JSON reports.

---

**CodeAlpha Artificial Intelligence Internship — Task 4**  
*Developed with Python, Ultralytics YOLO, Deep SORT, OpenCV & Flask.*
