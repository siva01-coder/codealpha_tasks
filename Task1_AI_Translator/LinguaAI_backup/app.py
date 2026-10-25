import os
import time
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# DeepL Supported Source Languages
SOURCE_LANGUAGES = [
    {"code": "auto", "name": "Auto Detect"},
    {"code": "AR", "name": "Arabic"},
    {"code": "BG", "name": "Bulgarian"},
    {"code": "CS", "name": "Czech"},
    {"code": "DA", "name": "Danish"},
    {"code": "DE", "name": "German"},
    {"code": "EL", "name": "Greek"},
    {"code": "EN", "name": "English"},
    {"code": "ES", "name": "Spanish"},
    {"code": "ET", "name": "Estonian"},
    {"code": "FI", "name": "Finnish"},
    {"code": "FR", "name": "French"},
    {"code": "HU", "name": "Hungarian"},
    {"code": "ID", "name": "Indonesian"},
    {"code": "IT", "name": "Italian"},
    {"code": "JA", "name": "Japanese"},
    {"code": "KO", "name": "Korean"},
    {"code": "LT", "name": "Lithuanian"},
    {"code": "LV", "name": "Latvian"},
    {"code": "NB", "name": "Norwegian (Bokmål)"},
    {"code": "NL", "name": "Dutch"},
    {"code": "PL", "name": "Polish"},
    {"code": "PT", "name": "Portuguese"},
    {"code": "RO", "name": "Romanian"},
    {"code": "RU", "name": "Russian"},
    {"code": "SK", "name": "Slovak"},
    {"code": "SL", "name": "Slovenian"},
    {"code": "SV", "name": "Swedish"},
    {"code": "TR", "name": "Turkish"},
    {"code": "UK", "name": "Ukrainian"},
    {"code": "ZH", "name": "Chinese"}
]

# DeepL Supported Target Languages
TARGET_LANGUAGES = [
    {"code": "AR", "name": "Arabic", "tts": "ar-SA"},
    {"code": "BG", "name": "Bulgarian", "tts": "bg-BG"},
    {"code": "CS", "name": "Czech", "tts": "cs-CZ"},
    {"code": "DA", "name": "Danish", "tts": "da-DK"},
    {"code": "DE", "name": "German", "tts": "de-DE"},
    {"code": "EL", "name": "Greek", "tts": "el-GR"},
    {"code": "EN-GB", "name": "English (British)", "tts": "en-GB", "source_code": "EN"},
    {"code": "EN-US", "name": "English (American)", "tts": "en-US", "source_code": "EN"},
    {"code": "ES", "name": "Spanish", "tts": "es-ES"},
    {"code": "ET", "name": "Estonian", "tts": "et-EE"},
    {"code": "FI", "name": "Finnish", "tts": "fi-FI"},
    {"code": "FR", "name": "French", "tts": "fr-FR"},
    {"code": "HU", "name": "Hungarian", "tts": "hu-HU"},
    {"code": "ID", "name": "Indonesian", "tts": "id-ID"},
    {"code": "IT", "name": "Italian", "tts": "it-IT"},
    {"code": "JA", "name": "Japanese", "tts": "ja-JP"},
    {"code": "KO", "name": "Korean", "tts": "ko-KR"},
    {"code": "LT", "name": "Lithuanian", "tts": "lt-LT"},
    {"code": "LV", "name": "Latvian", "tts": "lv-LV"},
    {"code": "NB", "name": "Norwegian (Bokmål)", "tts": "nb-NO"},
    {"code": "NL", "name": "Dutch", "tts": "nl-NL"},
    {"code": "PL", "name": "Polish", "tts": "pl-PL"},
    {"code": "PT-BR", "name": "Portuguese (Brazilian)", "tts": "pt-BR", "source_code": "PT"},
    {"code": "PT-PT", "name": "Portuguese (European)", "tts": "pt-PT", "source_code": "PT"},
    {"code": "RO", "name": "Romanian", "tts": "ro-RO"},
    {"code": "RU", "name": "Russian", "tts": "ru-RU"},
    {"code": "SK", "name": "Slovak", "tts": "sk-SK"},
    {"code": "SL", "name": "Slovenian", "tts": "sl-SI"},
    {"code": "SV", "name": "Swedish", "tts": "sv-SE"},
    {"code": "TR", "name": "Turkish", "tts": "tr-TR"},
    {"code": "UK", "name": "Ukrainian", "tts": "uk-UA"},
    {"code": "ZH", "name": "Chinese (Simplified)", "tts": "zh-CN"}
]


def get_deepl_endpoint(api_key: str) -> str:
    """
    Determine whether to use DeepL Free or Pro API endpoint based on the API key suffix.
    Keys for the Free API end with ':fx'.
    """
    if api_key.endswith(":fx"):
        return "https://api-free.deepl.com/v2/translate"
    return "https://api.deepl.com/v2/translate"


def call_deepl_translation_api(text: str, source_lang: str, target_lang: str, api_key: str) -> dict:
    """
    Calls the official DeepL REST API with retry logic and error handling.
    """
    endpoint = get_deepl_endpoint(api_key)
    headers = {
        "Authorization": f"DeepL-Auth-Key {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "text": [text],
        "target_lang": target_lang.upper()
    }

    # Only include source_lang if specified and not 'auto'
    if source_lang and source_lang.strip().lower() != "auto":
        payload["source_lang"] = source_lang.strip().upper()

    max_retries = 3
    delay = 1.0

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=12)

            if response.status_code == 200:
                data = response.json()
                if "translations" in data and len(data["translations"]) > 0:
                    result = data["translations"][0]
                    return {
                        "success": True,
                        "translation": result.get("text", ""),
                        "detected_source_language": result.get("detected_source_language", "")
                    }
                else:
                    return {
                        "success": False,
                        "error": "Unexpected response format from DeepL API."
                    }

            # Retryable server or rate-limit errors
            elif response.status_code in [429, 500, 503]:
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    if response.status_code == 429:
                        return {
                            "success": False,
                            "error": "Translation limit reached. Please try again later."
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Translation service is temporarily unavailable."
                        }

            elif response.status_code in [401, 403]:
                return {
                    "success": False,
                    "error": "Translation service authentication failed. Please check the API configuration."
                }
            elif response.status_code == 456:
                return {
                    "success": False,
                    "error": "DeepL translation character quota has been reached."
                }
            elif response.status_code == 400:
                try:
                    err_json = response.json()
                    msg = err_json.get("message", "Invalid request parameters.")
                except Exception:
                    msg = "Invalid translation request parameters."
                return {
                    "success": False,
                    "error": f"Invalid request: {msg}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Translation service error (HTTP {response.status_code})."
                }

        except requests.exceptions.Timeout:
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            return {
                "success": False,
                "error": "Translation request timed out. Please try again."
            }
        except requests.exceptions.RequestException:
            return {
                "success": False,
                "error": "Unable to connect to the translation service. Check network connection."
            }

    return {
        "success": False,
        "error": "Translation request failed after retries."
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/languages", methods=["GET"])
def get_languages():
    return jsonify({
        "success": True,
        "source_languages": SOURCE_LANGUAGES,
        "target_languages": TARGET_LANGUAGES
    })


@app.route("/api/translate", methods=["POST"])
def translate():
    api_key = os.getenv("DEEPL_API_KEY", "").strip()

    if not api_key or api_key == "YOUR_REAL_KEY_HERE":
        return jsonify({
            "success": False,
            "error": "Translation service authentication failed. Please check the API configuration."
        }), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request. Expected JSON body."
        }), 400

    text = data.get("text", "").strip()
    source_lang = data.get("source_lang", "").strip()
    target_lang = data.get("target_lang", "").strip()

    if not text:
        return jsonify({
            "success": False,
            "error": "Please enter text to translate."
        }), 400

    if len(text) > 5000:
        return jsonify({
            "success": False,
            "error": "Text exceeds maximum character limit of 5000 characters."
        }), 400

    if not target_lang:
        return jsonify({
            "success": False,
            "error": "Please select a valid target language."
        }), 400

    result = call_deepl_translation_api(
        text=text,
        source_lang=source_lang,
        target_lang=target_lang,
        api_key=api_key
    )

    if result.get("success"):
        return jsonify(result), 200
    else:
        return jsonify(result), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
