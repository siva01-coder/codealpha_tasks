import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure required directories exist
for directory in [MODELS_DIR, UPLOADS_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Detection & Tracking Model Settings
DEFAULT_MODEL = "yolov8n.pt"  # Pretrained lightweight COCO model
FALLBACK_MODELS = ["yolo11n.pt", "yolov8n.pt", "yolov5s.pt"]
DEFAULT_CONFIDENCE = 0.40
CONFIDENCE_MIN = 0.10
CONFIDENCE_MAX = 0.90

# Deep SORT Tracking Settings
DEEPSORT_MAX_AGE = 30
DEEPSORT_N_INIT = 3
DEEPSORT_MAX_COSINE_DISTANCE = 0.2

# Video Source & Processing Settings
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB max upload
INFERENCE_MAX_DIM = 640  # Resize frame for real-time inference efficiency

# Flask Server Settings
HOST = "0.0.0.0"
PORT = 5000
DEBUG = False

# COCO 80 Class Names
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]
