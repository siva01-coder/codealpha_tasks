# CodeAlpha AI Internship Projects

A collection of Artificial Intelligence projects developed as part of the **CodeAlpha Artificial Intelligence Internship — October 2026 Batch**.

This repository contains projects focused on machine translation, Natural Language Processing (NLP), and computer vision.

## 📌 Projects

### 1. LinguaAI — AI Language Translator

A web-based language translation application designed with a professional black-and-white interface.

**Key Features**
- Text input and source/target language selection
- Automatic source-language detection (if supported by the configured API)
- Translation using the DeepL API
- Copy translated text
- Text-to-speech support
- Responsive user interface
- Flask backend with environment-based API key configuration

**Technologies:** Python, Flask, HTML, CSS, JavaScript, DeepL API

**Project Folder:** `Task1_AI_Translator/`

### 2. FAQBot AI — Intelligent FAQ Chatbot

An NLP-based chatbot designed to answer frequently asked questions using a predefined knowledge base.

**Key Features**
- Natural language question input
- Text preprocessing
- TF-IDF vectorization
- Cosine similarity-based FAQ matching
- Confidence threshold for matching
- Appropriate responses for unknown questions
- Interactive chat interface

**Technologies:** Python, Flask, NLTK, scikit-learn, HTML, CSS, JavaScript

**Project Folder:** `Task2_FAQBot_AI/`

### 3. VisionTrack AI — Object Detection and Tracking

A computer vision application designed to detect and track objects in video streams.

**Planned/implemented features depend on the project code:**
- Object detection using YOLO
- Video processing using OpenCV
- Object tracking using Deep SORT
- Bounding boxes, object labels, and tracking IDs
- Real-time detection statistics

**Technologies:** Python, OpenCV, Ultralytics YOLO, Deep SORT, Flask

**Project Folder:** `Task3_VisionTrack_AI/`

## 🛠️ Repository Structure

```text
codealpha_tasks/
│
├── README.md
│
├── Task1_AI_Translator/
│   ├── app.py
│   ├── templates/
│   ├── static/
│   ├── requirements.txt
│   └── README.md
│
├── Task2_FAQBot_AI/
│   ├── app.py
│   ├── chatbot.py
│   ├── data/
│   └── README.md
│
└── Task3_VisionTrack_AI/
    ├── app.py
    ├── detector.py
    ├── tracker.py
    └── README.md
```

*Note: The actual files and folders may vary according to each project's implementation.*

## ⚙️ Installation

Each project has its own dependencies. Open the required project folder before installing packages.

General setup:

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

Install the project's dependencies:

```bash
pip install -r requirements.txt
```

Follow the individual project's README for configuration and execution instructions.

## 🔐 API Key Security

LinguaAI requires a DeepL API key when configured to use the DeepL translation service.

- Store the key in a local `.env` file.
- Never commit `.env` or API credentials to GitHub.
- Use `.env.example` to document required environment variables without including real secrets.
- Keep virtual environments and generated files out of the repository.

## 🎯 Internship Objectives

These projects demonstrate practical implementation of:

- API integration
- Natural Language Processing
- Text similarity and information retrieval
- Object detection and tracking
- Python backend development
- Web application design
- Software development and Git version control

## 🚀 Future Enhancements

- Expand language and translation support
- Improve FAQ matching quality
- Add more computer vision capabilities
- Improve performance and error handling
- Add further testing and documentation

## 👨‍💻 Author

**Siva M**

GitHub: [@siva01-coder](https://github.com/siva01-coder)

## 📄 Acknowledgement

Developed as part of the CodeAlpha Artificial Intelligence Internship learning experience.

---

**Note:** Features described above should be considered complete only after they have been implemented and tested in the corresponding project.
