import os
import time
import logging
import io
from flask import Flask, render_template, Response, request, jsonify, send_file
from werkzeug.utils import secure_filename
import config
from video_processor import VideoProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlaskServer")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Initialize global VideoProcessor instance
processor = VideoProcessor()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render main dashboard view."""
    return render_template('index.html', coco_classes=config.COCO_CLASSES)


@app.route('/video_feed')
def video_feed():
    """MJPEG Live Streaming Endpoint."""
    return Response(
        processor.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/api/start', methods=['POST'])
def start_detection():
    """Start detection session for webcam or uploaded video."""
    data = request.get_json() or {}
    source_type = data.get("source_type", "webcam")
    filepath = data.get("filepath", None)

    if source_type not in ["webcam", "upload"]:
        return jsonify({"success": False, "error": "Invalid video source type."}), 400

    if source_type == "upload" and not filepath:
        return jsonify({"success": False, "error": "No uploaded video file specified."}), 400

    success, message = processor.start(source_type=source_type, video_path=filepath)
    if success:
        return jsonify({"success": True, "message": f"Detection started on {source_type}."})
    else:
        return jsonify({"success": False, "error": message}), 400


@app.route('/api/stop', methods=['POST'])
def stop_detection():
    """Stop detection and release video resources."""
    processor.stop()
    return jsonify({"success": True, "message": "Detection stopped cleanly."})


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle video file upload, validate extension, and save to uploads directory."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file."}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        saved_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(config.UPLOADS_DIR, saved_filename)
        
        file.save(filepath)
        logger.info(f"Saved uploaded file to {filepath}")
        return jsonify({
            "success": True,
            "filepath": filepath,
            "filename": saved_filename
        })
    else:
        return jsonify({
            "success": False,
            "error": f"Invalid file format. Allowed extensions: {', '.join(config.ALLOWED_EXTENSIONS)}"
        }), 400


@app.route('/api/status', methods=['GET'])
def get_status():
    """Return live system telemetry, FPS, object counts, events."""
    return jsonify(processor.get_status())


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update confidence threshold, class filters, or tracking trail visibility."""
    data = request.get_json() or {}
    confidence = data.get("confidence", None)
    class_filter = data.get("class_filter", None)
    show_trails = data.get("show_trails", None)

    processor.update_settings(
        confidence=confidence,
        class_filter=class_filter,
        show_trails=show_trails
    )
    return jsonify({"success": True, "message": "Settings updated successfully."})


@app.route('/api/snapshot', methods=['GET'])
def take_snapshot():
    """Download current annotated frame as JPEG image."""
    jpeg_bytes = processor.get_current_frame()
    if jpeg_bytes is None:
        return jsonify({"success": False, "error": "No active video stream to snapshot."}), 400

    return Response(
        jpeg_bytes,
        mimetype='image/jpeg',
        headers={"Content-Disposition": "attachment;filename=visiontrack_snapshot.jpg"}
    )


@app.route('/api/record/start', methods=['POST'])
def start_recording():
    """Start output video recording."""
    success, result = processor.start_recording()
    if success:
        return jsonify({"success": True, "filename": result})
    return jsonify({"success": False, "error": result}), 400


@app.route('/api/record/stop', methods=['POST'])
def stop_recording():
    """Stop output video recording."""
    success, result = processor.stop_recording()
    if success:
        return jsonify({"success": True, "filename": result})
    return jsonify({"success": False, "error": result}), 400


if __name__ == '__main__':
    logger.info("Starting VisionTrack AI Flask Server...")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG, threaded=True)
