/**
 * LinguaAI - Client Side Application Logic
 * Pure Vanilla JavaScript (No external frameworks)
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const sourceLangSelect = document.getElementById('source-lang-select');
    const targetLangSelect = document.getElementById('target-lang-select');
    const swapBtn = document.getElementById('swap-btn');
    const sourceText = document.getElementById('source-text');
    const targetText = document.getElementById('target-text');
    const charCounter = document.getElementById('char-counter');
    const statusBadge = document.getElementById('status-badge');
    const translateBtn = document.getElementById('translate-btn');
    const translateBtnText = document.getElementById('translate-btn-text');
    const translateBtnSpinner = document.getElementById('translate-btn-spinner');
    const clearBtn = document.getElementById('clear-btn');
    const copyBtn = document.getElementById('copy-btn');
    const copyBtnText = document.getElementById('copy-btn-text');
    const listenSourceBtn = document.getElementById('listen-source-btn');
    const listenTargetBtn = document.getElementById('listen-target-btn');
    const detectedLangBanner = document.getElementById('detected-lang-banner');
    const detectedLangName = document.getElementById('detected-lang-name');
    const toastContainer = document.getElementById('toast-container');

    // Internal State
    let lastDetectedLangCode = null;
    let isTranslating = false;

    // Fallback DeepL Supported Languages List
    const DEFAULT_SOURCE_LANGS = [
        { code: "auto", name: "Auto Detect" },
        { code: "AR", name: "Arabic" },
        { code: "BG", name: "Bulgarian" },
        { code: "CS", name: "Czech" },
        { code: "DA", name: "Danish" },
        { code: "DE", name: "German" },
        { code: "EL", name: "Greek" },
        { code: "EN", name: "English" },
        { code: "ES", name: "Spanish" },
        { code: "ET", name: "Estonian" },
        { code: "FI", name: "Finnish" },
        { code: "FR", name: "French" },
        { code: "HU", name: "Hungarian" },
        { code: "ID", name: "Indonesian" },
        { code: "IT", name: "Italian" },
        { code: "JA", name: "Japanese" },
        { code: "KO", name: "Korean" },
        { code: "LT", name: "Lithuanian" },
        { code: "LV", name: "Latvian" },
        { code: "NB", name: "Norwegian (Bokmål)" },
        { code: "NL", name: "Dutch" },
        { code: "PL", name: "Polish" },
        { code: "PT", name: "Portuguese" },
        { code: "RO", name: "Romanian" },
        { code: "RU", name: "Russian" },
        { code: "SK", name: "Slovak" },
        { code: "SL", name: "Slovenian" },
        { code: "SV", name: "Swedish" },
        { code: "TR", name: "Turkish" },
        { code: "UK", name: "Ukrainian" },
        { code: "ZH", name: "Chinese" }
    ];

    const DEFAULT_TARGET_LANGS = [
        { code: "AR", name: "Arabic", tts: "ar-SA" },
        { code: "BG", name: "Bulgarian", tts: "bg-BG" },
        { code: "CS", name: "Czech", tts: "cs-CZ" },
        { code: "DA", name: "Danish", tts: "da-DK" },
        { code: "DE", name: "German", tts: "de-DE" },
        { code: "EL", name: "Greek", tts: "el-GR" },
        { code: "EN-GB", name: "English (British)", tts: "en-GB", source_code: "EN" },
        { code: "EN-US", name: "English (American)", tts: "en-US", source_code: "EN" },
        { code: "ES", name: "Spanish", tts: "es-ES" },
        { code: "ET", name: "Estonian", tts: "et-EE" },
        { code: "FI", name: "Finnish", tts: "fi-FI" },
        { code: "FR", name: "French", tts: "fr-FR" },
        { code: "HU", name: "Hungarian", tts: "hu-HU" },
        { code: "ID", name: "Indonesian", tts: "id-ID" },
        { code: "IT", name: "Italian", tts: "it-IT" },
        { code: "JA", name: "Japanese", tts: "ja-JP" },
        { code: "KO", name: "Korean", tts: "ko-KR" },
        { code: "LT", name: "Lithuanian", tts: "lt-LT" },
        { code: "LV", name: "Latvian", tts: "lv-LV" },
        { code: "NB", name: "Norwegian (Bokmål)", tts: "nb-NO" },
        { code: "NL", name: "Dutch", tts: "nl-NL" },
        { code: "PL", name: "Polish", tts: "pl-PL" },
        { code: "PT-BR", name: "Portuguese (Brazilian)", tts: "pt-BR", source_code: "PT" },
        { code: "PT-PT", name: "Portuguese (European)", tts: "pt-PT", source_code: "PT" },
        { code: "RO", name: "Romanian", tts: "ro-RO" },
        { code: "RU", name: "Russian", tts: "ru-RU" },
        { code: "SK", name: "Slovak", tts: "sk-SK" },
        { code: "SL", name: "Slovenian", tts: "sl-SI" },
        { code: "SV", name: "Swedish", tts: "sv-SE" },
        { code: "TR", name: "Turkish", tts: "tr-TR" },
        { code: "UK", name: "Ukrainian", tts: "uk-UA" },
        { code: "ZH", name: "Chinese (Simplified)", tts: "zh-CN" }
    ];

    // Voice / Language TTS Mapping dictionary
    const TTS_LANG_MAP = {
        "AR": "ar-SA", "BG": "bg-BG", "CS": "cs-CZ", "DA": "da-DK",
        "DE": "de-DE", "EL": "el-GR", "EN": "en-US", "EN-US": "en-US",
        "EN-GB": "en-GB", "ES": "es-ES", "ET": "et-EE", "FI": "fi-FI",
        "FR": "fr-FR", "HU": "hu-HU", "ID": "id-ID", "IT": "it-IT",
        "JA": "ja-JP", "KO": "ko-KR", "LT": "lt-LT", "LV": "lv-LV",
        "NB": "nb-NO", "NL": "nl-NL", "PL": "pl-PL", "PT": "pt-PT",
        "PT-BR": "pt-BR", "PT-PT": "pt-PT", "RO": "ro-RO", "RU": "ru-RU",
        "SK": "sk-SK", "SL": "sl-SI", "SV": "sv-SE", "TR": "tr-TR",
        "UK": "uk-UA", "ZH": "zh-CN"
    };

    // Initialize Language Options
    async function initLanguages() {
        try {
            const res = await fetch('/api/languages');
            if (res.ok) {
                const data = await res.json();
                if (data.success) {
                    populateDropdowns(data.source_languages, data.target_languages);
                    return;
                }
            }
        } catch (e) {
            console.warn('Using default fallback languages list.');
        }
        populateDropdowns(DEFAULT_SOURCE_LANGS, DEFAULT_TARGET_LANGS);
    }

    function populateDropdowns(sources, targets) {
        sourceLangSelect.innerHTML = '';
        targets.forEach(lang => {
            // Only add if not already in sources or add unique
        });
        sources.forEach(lang => {
            const opt = document.createElement('option');
            opt.value = lang.code;
            opt.textContent = lang.name;
            sourceLangSelect.appendChild(opt);
        });

        targetLangSelect.innerHTML = '';
        targets.forEach(lang => {
            const opt = document.createElement('option');
            opt.value = lang.code;
            opt.textContent = lang.name;
            if (lang.code === 'DE') opt.selected = true; // Default German
            targetLangSelect.appendChild(opt);
        });
    }

    // Helper: Find Language Name from Code
    function getLangName(code) {
        if (!code) return '';
        const found = DEFAULT_TARGET_LANGS.find(l => l.code === code || l.source_code === code) ||
                      DEFAULT_SOURCE_LANGS.find(l => l.code === code);
        return found ? found.name : code;
    }

    // Toast Notification System
    function showToast(message, type = 'error') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${escapeHtml(message)}</span>
            <button style="background:none;border:none;color:#aaa;cursor:pointer;margin-left:10px;font-size:1.1rem;" onclick="this.parentElement.remove()">✕</button>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }
        }, 4500);
    }

    function escapeHtml(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    }

    // Character Counter
    sourceText.addEventListener('input', () => {
        const length = sourceText.value.length;
        charCounter.textContent = `${length} / 5000`;
        if (length === 0) {
            statusBadge.textContent = 'Ready';
            statusBadge.classList.remove('active');
        }
    });

    // Translate Core Function
    async function handleTranslate() {
        if (isTranslating) return;

        const text = sourceText.value.trim();
        const source_lang = sourceLangSelect.value;
        const target_lang = targetLangSelect.value;

        if (!text) {
            showToast('Please enter text to translate.');
            sourceText.focus();
            return;
        }

        if (text.length > 5000) {
            showToast('Text exceeds maximum limit of 5000 characters.');
            return;
        }

        if (!target_lang) {
            showToast('Please select a valid target language.');
            return;
        }

        // Set Loading UI State
        isTranslating = true;
        translateBtn.disabled = true;
        translateBtnText.textContent = 'TRANSLATING...';
        translateBtnSpinner.style.display = 'inline-block';
        statusBadge.textContent = 'Translating...';
        statusBadge.classList.add('active');

        try {
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    source_lang: source_lang,
                    target_lang: target_lang
                })
            });

            const data = await response.json();

            if (data.success) {
                targetText.value = data.translation;
                statusBadge.textContent = 'Completed';

                if (source_lang === 'auto' && data.detected_source_language) {
                    lastDetectedLangCode = data.detected_source_language;
                    const langName = getLangName(data.detected_source_language);
                    detectedLangName.textContent = `${langName} (${data.detected_source_language})`;
                    detectedLangBanner.style.display = 'inline-block';
                } else {
                    detectedLangBanner.style.display = 'none';
                }
            } else {
                showToast(data.error || 'Translation failed.');
                statusBadge.textContent = 'Error';
            }
        } catch (error) {
            showToast('Unable to connect to the translation service.');
            statusBadge.textContent = 'Network Error';
        } finally {
            isTranslating = false;
            translateBtn.disabled = false;
            translateBtnText.textContent = 'TRANSLATE';
            translateBtnSpinner.style.display = 'none';
        }
    }

    // Translate Button Click & Keyboard Shortcuts
    translateBtn.addEventListener('click', handleTranslate);

    sourceText.addEventListener('keydown', (e) => {
        // Ctrl+Enter or Cmd+Enter to translate
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            handleTranslate();
        }
    });

    // Language Swap Functionality
    swapBtn.addEventListener('click', () => {
        const currentSource = sourceLangSelect.value;
        const currentTarget = targetLangSelect.value;
        const currentTranslation = targetText.value;

        if (currentSource === 'auto') {
            if (lastDetectedLangCode) {
                // Swap using detected language
                const sourceMapped = lastDetectedLangCode; // e.g. "EN"
                sourceLangSelect.value = sourceMapped;
                
                // Match target option or fallback
                const targetMatch = Array.from(targetLangSelect.options).find(opt => opt.value.startsWith(currentTarget)) ? currentTarget : 'EN-US';
                
                // Move target text to source textarea if present
                if (currentTranslation) {
                    sourceText.value = currentTranslation;
                    targetText.value = '';
                    charCounter.textContent = `${sourceText.value.length} / 5000`;
                    statusBadge.textContent = 'Ready';
                }
                detectedLangBanner.style.display = 'none';
            } else {
                showToast('Auto Detect cannot be directly swapped until a source language is detected or selected.');
                return;
            }
        } else {
            // Find corresponding target value for currentSource
            let newTargetVal = currentSource;
            if (currentSource === 'EN') newTargetVal = 'EN-US';
            if (currentSource === 'PT') newTargetVal = 'PT-PT';

            // Find corresponding source value for currentTarget
            let newSourceVal = currentTarget.split('-')[0]; // EN-US -> EN

            // Update Select Elements
            const sourceOptionExists = Array.from(sourceLangSelect.options).some(opt => opt.value === newSourceVal);
            if (sourceOptionExists) {
                sourceLangSelect.value = newSourceVal;
            }

            const targetOptionExists = Array.from(targetLangSelect.options).some(opt => opt.value === newTargetVal);
            if (targetOptionExists) {
                targetLangSelect.value = newTargetVal;
            }

            // Swap Text Contents if translation exists
            if (currentTranslation) {
                sourceText.value = currentTranslation;
                targetText.value = '';
                charCounter.textContent = `${sourceText.value.length} / 5000`;
                statusBadge.textContent = 'Ready';
            }

            detectedLangBanner.style.display = 'none';
        }
    });

    // Clear Functionality
    clearBtn.addEventListener('click', () => {
        sourceText.value = '';
        targetText.value = '';
        charCounter.textContent = '0 / 5000';
        statusBadge.textContent = 'Ready';
        statusBadge.classList.remove('active');
        detectedLangBanner.style.display = 'none';
        lastDetectedLangCode = null;
        sourceText.focus();
    });

    // Copy Translation to Clipboard
    copyBtn.addEventListener('click', async () => {
        const textToCopy = targetText.value.trim();
        if (!textToCopy) {
            showToast('No translation available to copy.');
            return;
        }

        try {
            await navigator.clipboard.writeText(textToCopy);
            copyBtnText.textContent = 'Copied!';
            statusBadge.textContent = 'Copied!';
            
            setTimeout(() => {
                copyBtnText.textContent = 'Copy';
                statusBadge.textContent = 'Completed';
            }, 2000);
        } catch (err) {
            showToast('Failed to copy text to clipboard.');
        }
    });

    // Speech Synthesis (Text-to-Speech)
    function speakText(text, langCode) {
        if (!('speechSynthesis' in window)) {
            showToast('Text-to-speech is not supported by this browser.');
            return;
        }

        const trimmed = text.trim();
        if (!trimmed) {
            showToast('No text available to listen.');
            return;
        }

        window.speechSynthesis.cancel(); // Cancel any ongoing speech

        const utterance = new SpeechSynthesisUtterance(trimmed);
        
        // Match TTS language code
        const ttsLocale = TTS_LANG_MAP[langCode] || langCode || 'en-US';
        utterance.lang = ttsLocale;
        utterance.rate = 0.95;

        utterance.onerror = () => {
            showToast('Text-to-speech error or voice unavailable for this language.');
        };

        window.speechSynthesis.speak(utterance);
    }

    // Source Listen Button
    listenSourceBtn.addEventListener('click', () => {
        const text = sourceText.value;
        let lang = sourceLangSelect.value;
        if (lang === 'auto') {
            lang = lastDetectedLangCode || 'EN';
        }
        speakText(text, lang);
    });

    // Target Listen Button
    listenTargetBtn.addEventListener('click', () => {
        const text = targetText.value;
        const lang = targetLangSelect.value;
        speakText(text, lang);
    });

    // Initialize application
    initLanguages();
});
