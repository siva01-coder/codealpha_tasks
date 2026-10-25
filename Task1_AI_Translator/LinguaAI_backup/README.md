# LinguaAI — AI Language Translation Tool

LinguaAI is a production-quality, high-performance web application built for **CodeAlpha Artificial Intelligence Internship Task 1**. It delivers intelligent multilingual translation using the official DeepL Neural Machine Translation (NMT) REST API, featuring a modern monochrome SaaS interface inspired by Apple and Linear design systems.

---

## Project Description

LinguaAI provides fast, accurate neural translations across 30+ global languages with automatic source language detection, built-in Text-to-Speech (TTS), clipboard integration, and robust retry mechanics. Built with Python (Flask) and modern vanilla JavaScript, the application separates client presentation from backend translation operations to ensure total API key security.

---

## Features

- **Real DeepL NMT Engine Integration**: Uses the authentic DeepL REST API for neural translation (supports both Free `:fx` and Pro keys).
- **Auto Language Detection**: Automatically detects source text language using DeepL's detection models.
- **Monochrome SaaS Design System**: High-contrast Apple/Linear-inspired dark UI using strictly black, white, and gray tones.
- **Language Swapping**: Effortlessly swap source and target languages and text contexts.
- **Text-to-Speech (Web Speech API)**: Listen to native pronunciations of source and translated text.
- **One-Click Copy**: Copy translations to clipboard with instant status feedback.
- **Live Character Counter**: Real-time counter capped at 5,000 characters.
- **Keyboard Shortcuts**: Press `Ctrl + Enter` (or `Cmd + Enter`) inside the input panel to trigger instant translation.
- **Exponential Backoff Retry**: Automatic backend retry system (up to 3 attempts) for temporary 429/500/503 service disruptions.
- **Fully Responsive**: Seamless user experience across 4K, desktop, tablet, and mobile displays.

---

## Technologies Used

- **Frontend**: HTML5, CSS3 (Vanilla CSS variables & Grid), Vanilla JavaScript (ES6+).
- **Backend**: Python 3.10+, Flask 3.0+.
- **Translation Provider**: DeepL REST API (`/v2/translate`).
- **HTTP Client & Environment**: `requests`, `python-dotenv`.
- **Speech Synthesis**: Browser Web Speech API (`window.speechSynthesis`).

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Client Browser                       │
│  (HTML5 / Vanilla JS / Web Speech / Modern CSS Grid)  │
└──────────────────────────┬─────────────────────────────┘
                           │ POST /api/translate (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Flask Backend                        │
│  - Environment Key Validation (.env)                  │
│  - DeepL Key Suffix Auto-Routing (:fx vs Pro)          │
│  - Exponential Backoff Retry (Attempts 1-3)           │
│  - Secure Header Auth Injection                        │
└──────────────────────────┬─────────────────────────────┘
                           │ POST https://api.deepl.com/v2/translate
                           ▼
┌────────────────────────────────────────────────────────┐
│                   DeepL REST API                       │
│            Neural Machine Translation Engine           │
└────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
LinguaAI/
├── app.py                  # Flask application server & DeepL API gateway
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
├── .env                    # Local environment config (Contains API key, git-ignored)
├── .gitignore              # Files excluded from version control
├── README.md               # Project documentation
├── templates/
│   └── index.html          # Semantic HTML5 layout
└── static/
    ├── style.css           # Custom monochrome SaaS stylesheet
    └── script.js           # Client-side controller & Web Speech logic
```

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/LinguaAI.git
   cd LinguaAI
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Open `.env` in your code editor:
```env
DEEPL_API_KEY=YOUR_REAL_KEY_HERE
```

---

## DeepL API Setup

1. Register for a DeepL API account at [DeepL API Portal](https://www.deepl.com/pro-api).
2. Retrieve your authentication key from your account dashboard.
3. Paste the key into your `.env` file:
   - For DeepL Free API accounts, the key ends with `:fx` (e.g., `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx`).
   - For DeepL Pro API accounts, the key does not have `:fx`.
4. LinguaAI automatically detects key format and routes requests to the correct endpoint (`api-free.deepl.com` or `api.deepl.com`).

---

## Running the Application

Start the Flask development server:
```bash
python app.py
```

Access the application in your browser at:
```
http://localhost:5000
```

---

## API Endpoint

### `POST /api/translate`

#### Request Payload
```json
{
  "text": "Hello, how are you today?",
  "source_lang": "auto",
  "target_lang": "DE"
}
```

#### Success Response (200 OK)
```json
{
  "success": true,
  "translation": "Hallo, wie geht es Ihnen heute?",
  "detected_source_language": "EN"
}
```

#### Error Response (400 Bad Request / Server Error)
```json
{
  "success": false,
  "error": "Translation service authentication failed. Please check the API configuration."
}
```

---

## Error Handling

LinguaAI handles edge cases gracefully with user-friendly notifications:

| Status / Scenario | Internal Handler | User Experience Message |
| :--- | :--- | :--- |
| **Empty Input** | Frontend & Backend validation | "Please enter text to translate." |
| **Quota Reached** | HTTP 456 from DeepL | "DeepL translation character quota has been reached." |
| **Invalid Auth** | HTTP 401 / 403 from DeepL | "Translation service authentication failed. Please check the API configuration." |
| **Rate Limit** | HTTP 429 + Backoff retry | "Translation limit reached. Please try again later." |
| **Service Outage** | HTTP 500 / 503 + Backoff retry | "Translation service is temporarily unavailable." |
| **Network Error** | Connection Exception | "Unable to connect to the translation service." |

---

## Security

- **Zero Key Exposure**: `DEEPL_API_KEY` is loaded strictly on the backend using `python-dotenv`.
- **Git Protection**: `.env` is listed in `.gitignore` to prevent secret leakage to public code repositories.
- **Sanitized Outputs**: Error messages strip sensitive infrastructure data before delivering responses to the frontend.

---

## UI Layout Overview

```
                 LinguaAI
        Intelligent multilingual translation

        [ Auto Detect ]  ⇄  [ German ]

┌──────────────────────┐  ┌──────────────────────┐
│ YOUR TEXT  0 / 5000  │  │ TRANSLATION    Ready │
│                      │  │                      │
│ Enter text...        │  │ Your translation...  │
│                      │  │                      │
│          Clear Listen│  │          Copy Listen │
└──────────────────────┘  └──────────────────────┘

              [ TRANSLATE ]

           Detected language: English (EN)
```

---

## CodeAlpha Internship Task

This project satisfies all requirements for **CodeAlpha AI Internship Task 1**:
- Full-stack Python + Flask + Vanilla HTML/CSS/JS application.
- Real-world integration of DeepL Neural Machine Translation.
- Complete feature set: Swap, Copy, TTS, Auto Detect, Retry logic, Responsive design.
- Production-grade code structure, security, and documentation.

---

## Future Enhancements

- Document translation (.pdf, .docx, .txt upload).
- Historical translation log (local storage powered).
- Favorite translations bookmarking system.
- Custom glossary and term mapping integration.

---

## License

Developed as part of the CodeAlpha Artificial Intelligence Internship Program.
Neural machine translation powered by DeepL.
