/* ==========================================================================
   VISIONTRACK AI — FRONTEND CONTROL & TELEMETRY SCRIPT
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const tabWebcam = document.getElementById("tab-webcam");
    const tabUpload = document.getElementById("tab-upload");
    const uploadSection = document.getElementById("upload-section");
    const dropzone = document.getElementById("dropzone");
    const videoFileInput = document.getElementById("video-file-input");
    const uploadFileLabel = document.getElementById("upload-file-label");
    const btnUploadFile = document.getElementById("btn-upload-file");
    
    const btnStart = document.getElementById("btn-start");
    const btnStop = document.getElementById("btn-stop");
    const btnSnapshot = document.getElementById("btn-snapshot");
    const btnRecord = document.getElementById("btn-record");
    const recordIcon = document.getElementById("record-icon");
    const recordText = document.getElementById("record-text");
    
    const chkTrails = document.getElementById("chk-trails");
    const sliderConfidence = document.getElementById("slider-confidence");
    const valConfidence = document.getElementById("val-confidence");
    
    const btnSelectAll = document.getElementById("btn-select-all-classes");
    const btnClearClasses = document.getElementById("btn-clear-classes");
    const classCheckboxes = document.querySelectorAll(".cls-checkbox");
    
    const videoStream = document.getElementById("video-stream");
    const videoPlaceholder = document.getElementById("video-placeholder");
    const streamBadge = document.getElementById("stream-badge");
    const streamBadgeText = document.getElementById("stream-badge-text");
    const systemStatusText = document.getElementById("system-status-text");
    const systemStatusDot = document.querySelector("#system-status-indicator .status-dot");
    
    // Telemetry Elements
    const metricStatus = document.getElementById("metric-status");
    const metricTracker = document.getElementById("metric-tracker");
    const metricDevice = document.getElementById("metric-device");
    const metricFps = document.getElementById("metric-fps");
    const metricObjects = document.getElementById("metric-objects");
    const metricTotalTracks = document.getElementById("metric-total-tracks");
    const metricLatency = document.getElementById("metric-latency");
    const chartContainer = document.getElementById("chart-container");
    const activeClassCount = document.getElementById("active-class-count");
    const eventLog = document.getElementById("event-log");
    
    // Toast Elements
    const notificationToast = document.getElementById("notification-toast");
    const toastMessage = document.getElementById("toast-message");
    const btnCloseToast = document.getElementById("btn-close-toast");

    // State Variables
    let currentSourceType = "webcam"; // 'webcam' or 'upload'
    let uploadedFilePath = null;
    let pollInterval = null;
    let isRecording = false;

    // Initialize UI
    initEvents();

    function initEvents() {
        // Source Tab Switching
        tabWebcam.addEventListener("click", () => switchSourceTab("webcam"));
        tabUpload.addEventListener("click", () => switchSourceTab("upload"));

        // File Selection & Drag Drop
        videoFileInput.addEventListener("change", handleFileSelect);
        btnUploadFile.addEventListener("click", uploadVideo);

        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });
        dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                videoFileInput.files = e.dataTransfer.files;
                handleFileSelect();
            }
        });

        // Start / Stop Detection
        btnStart.addEventListener("click", startDetection);
        btnStop.addEventListener("click", stopDetection);

        // Snapshot & Recording
        btnSnapshot.addEventListener("click", takeSnapshot);
        btnRecord.addEventListener("click", toggleRecording);

        // Settings Sync
        chkTrails.addEventListener("change", toggleTrails);
        sliderConfidence.addEventListener("input", (e) => {
            valConfidence.textContent = `${e.target.value}%`;
        });
        sliderConfidence.addEventListener("change", updateConfidence);

        // Class Filters
        classCheckboxes.forEach(cb => cb.addEventListener("change", filterClasses));
        btnSelectAll.addEventListener("click", () => setAllClassFilters(true));
        btnClearClasses.addEventListener("click", () => setAllClassFilters(false));

        // Toast close
        btnCloseToast.addEventListener("click", hideToast);

        // Initial settings sync to backend
        updateConfidence();
        filterClasses();
    }

    function showToast(msg) {
        toastMessage.textContent = msg;
        notificationToast.classList.add("show");
        setTimeout(hideToast, 6000);
    }

    function hideToast() {
        notificationToast.classList.remove("show");
    }

    function switchSourceTab(type) {
        currentSourceType = type;
        if (type === "webcam") {
            tabWebcam.classList.add("active");
            tabUpload.classList.remove("active");
            uploadSection.style.display = "none";
        } else {
            tabUpload.classList.add("active");
            tabWebcam.classList.remove("active");
            uploadSection.style.display = "flex";
        }
    }

    function handleFileSelect() {
        if (videoFileInput.files.length > 0) {
            const file = videoFileInput.files[0];
            uploadFileLabel.textContent = `Selected: ${file.name}`;
            btnUploadFile.disabled = false;
        }
    }

    async function uploadVideo() {
        if (videoFileInput.files.length === 0) return;

        const file = videoFileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        btnUploadFile.disabled = true;
        btnUploadFile.textContent = "UPLOADING...";

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });

            const data = await res.json();
            if (data.success) {
                uploadedFilePath = data.filepath;
                uploadFileLabel.textContent = `Ready: ${data.filename}`;
                showToast("Video file uploaded and prepared successfully.");
            } else {
                showToast(`Upload failed: ${data.error}`);
            }
        } catch (err) {
            showToast("Failed to upload video file. Server error.");
        } finally {
            btnUploadFile.disabled = false;
            btnUploadFile.textContent = "UPLOAD & PREPARE";
        }
    }

    async function startDetection() {
        if (currentSourceType === "upload" && !uploadedFilePath) {
            showToast("Please upload a video file first before starting detection.");
            return;
        }

        btnStart.disabled = true;
        btnStart.textContent = "INITIALIZING...";

        try {
            const res = await fetch("/api/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    source_type: currentSourceType,
                    filepath: uploadedFilePath
                })
            });

            const data = await res.json();

            if (data.success) {
                // Attach timestamp to break browser cache on stream reconnect
                videoStream.src = `/video_feed?t=${new Date().getTime()}`;
                videoStream.style.display = "block";
                videoPlaceholder.style.display = "none";

                streamBadge.classList.remove("offline");
                streamBadge.classList.add("online");
                streamBadgeText.textContent = "LIVE";

                systemStatusText.textContent = "DETECTION ENGINE RUNNING";
                systemStatusDot.style.backgroundColor = "#ffffff";

                btnStart.disabled = true;
                btnStart.innerHTML = "<span>▶</span> START DETECTION";
                btnStop.disabled = false;
                btnSnapshot.disabled = false;
                btnRecord.disabled = false;

                // Start Telemetry Polling
                if (pollInterval) clearInterval(pollInterval);
                pollInterval = setInterval(updateStatus, 1000);
                updateStatus();
            } else {
                showToast(`Failed to start: ${data.error}`);
                btnStart.disabled = false;
                btnStart.innerHTML = "<span>▶</span> START DETECTION";
            }
        } catch (err) {
            showToast("Error connecting to server to start detection.");
            btnStart.disabled = false;
            btnStart.innerHTML = "<span>▶</span> START DETECTION";
        }
    }

    async function stopDetection() {
        btnStop.disabled = true;

        try {
            await fetch("/api/stop", { method: "POST" });
        } catch (err) {
            console.error("Error stopping stream:", err);
        } finally {
            if (pollInterval) clearInterval(pollInterval);

            videoStream.src = "";
            videoStream.style.display = "none";
            videoPlaceholder.style.display = "flex";

            streamBadge.classList.remove("online");
            streamBadge.classList.add("offline");
            streamBadgeText.textContent = "OFFLINE";

            systemStatusText.textContent = "SYSTEM READY";
            systemStatusDot.style.backgroundColor = "#888888";

            btnStart.disabled = false;
            btnStop.disabled = true;
            btnSnapshot.disabled = true;
            btnRecord.disabled = true;

            metricStatus.textContent = "STOPPED";
            metricFps.textContent = "0.0";
            metricObjects.textContent = "0";

            if (isRecording) {
                isRecording = false;
                recordIcon.textContent = "⏺";
                recordText.textContent = "START RECORDING";
            }
        }
    }

    async function updateStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();

            if (!data.running) {
                if (streamBadge.classList.contains("online")) {
                    stopDetection();
                    if (data.error) showToast(data.error);
                }
                return;
            }

            // Update Telemetry Displays
            metricStatus.textContent = "ACTIVE";
            metricDevice.textContent = data.device || "CPU";
            metricFps.textContent = data.fps.toFixed(1);
            metricObjects.textContent = data.tracked_objects;
            metricTotalTracks.textContent = data.total_tracks;
            metricLatency.textContent = `${data.latency_ms.toFixed(1)} ms`;

            // Update Class Distribution Bar Chart
            updateClassCounts(data.classes);

            // Update Event Log
            updateEventLog(data.recent_events);

        } catch (err) {
            console.error("Error fetching status:", err);
        }
    }

    function updateClassCounts(classesDict) {
        if (!classesDict || Object.keys(classesDict).length === 0) {
            chartContainer.innerHTML = `<div class="empty-chart-msg">No objects currently detected.</div>`;
            activeClassCount.textContent = "0 Classes Active";
            return;
        }

        const entries = Object.entries(classesDict);
        activeClassCount.textContent = `${entries.length} Classes Active`;

        const maxVal = Math.max(...Object.values(classesDict), 1);
        let html = "";

        entries.forEach(([clsName, count]) => {
            const percent = Math.min(100, Math.round((count / maxVal) * 100));
            html += `
                <div class="chart-bar-row">
                    <span class="bar-label">${clsName}</span>
                    <div class="bar-track">
                        <div class="bar-fill" style="width: ${percent}%;"></div>
                    </div>
                    <span class="bar-val">${count}</span>
                </div>
            `;
        });

        chartContainer.innerHTML = html;
    }

    function updateEventLog(eventsList) {
        if (!eventsList || eventsList.length === 0) return;

        let html = "";
        eventsList.forEach(ev => {
            html += `<div class="log-entry">${ev}</div>`;
        });
        eventLog.innerHTML = html;
    }

    function takeSnapshot() {
        window.location.href = "/api/snapshot";
    }

    async function toggleRecording() {
        if (!isRecording) {
            try {
                const res = await fetch("/api/record/start", { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    isRecording = true;
                    recordIcon.textContent = "⏹";
                    recordText.textContent = "STOP RECORDING";
                    showToast(`Recording started: ${data.filename}`);
                } else {
                    showToast(`Recording failed: ${data.error}`);
                }
            } catch (err) {
                showToast("Failed to communicate with recording endpoint.");
            }
        } else {
            try {
                const res = await fetch("/api/record/stop", { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    isRecording = false;
                    recordIcon.textContent = "⏺";
                    recordText.textContent = "START RECORDING";
                    showToast(`Recording saved to output directory: ${data.filename}`);
                } else {
                    showToast(`Failed to stop recording: ${data.error}`);
                }
            } catch (err) {
                showToast("Error stopping recording.");
            }
        }
    }

    async function toggleTrails() {
        sendSettings({ show_trails: chkTrails.checked });
    }

    async function updateConfidence() {
        const val = parseFloat(sliderConfidence.value) / 100.0;
        sendSettings({ confidence: val });
    }

    async function filterClasses() {
        const checkedClasses = [];
        classCheckboxes.forEach(cb => {
            if (cb.checked) checkedClasses.push(cb.value);
        });
        sendSettings({ class_filter: checkedClasses });
    }

    function setAllClassFilters(selectState) {
        classCheckboxes.forEach(cb => cb.checked = selectState);
        filterClasses();
    }

    async function sendSettings(payload) {
        try {
            await fetch("/api/settings", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } catch (err) {
            console.error("Error updating settings:", err);
        }
    }
});
