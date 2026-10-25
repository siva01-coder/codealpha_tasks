# FAQBot AI — Intelligent College FAQ Assistant

[![CodeAlpha Internship Task 2](https://img.shields.io/badge/CodeAlpha-Task%202%20AI-black?style=for-the-badge)](https://www.codealpha.tech)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-white?style=for-the-badge&logo=python&logoColor=black)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-TF--IDF-white?style=for-the-badge&logo=scikit-learn&logoColor=black)](https://scikit-learn.org)

**FAQBot AI** is an intelligent, real NLP-driven college FAQ chatbot built for **CodeAlpha Artificial Intelligence Internship Task 2**. The system enables students to query college information in natural language and receive accurate, instant responses powered by **NLTK Preprocessing**, **TF-IDF Vectorization**, and **Cosine Similarity Matching**, backed by a secondary **Fuzzy Matching Fallback**.

> ⚡ **No Paid APIs / No Hardcoded Rules**: FAQBot AI runs 100% locally without external generative AI dependencies (ChatGPT/OpenAI) or fake `if/else` keyword matching.

---

## 📸 Interface & System Architecture

The application features a modern, high-contrast, **Monochrome Premium SaaS UI** (`#050505` background, `#0D0D0D` surfaces, `#262626` borders, crisp typography) featuring:
- **Interactive Chat Stream**: Real-time natural language query resolution with confidence scores and category tags.
- **Suggested Questions Chips**: Instant query triggers.
- **FAQ Explorer & Category Filter**: Searchable accordion displaying all 45+ knowledge base entries.
- **Live NLP Pipeline Inspector Drawer**: Inspect tokenization, stop-word removal, lemmatization, and TF-IDF similarity vectors in real-time.

---

## 🧠 NLP & AI Pipeline Architecture

```
                               ┌───────────────────────────┐
                               │     Raw User Input        │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  Lowercase Normalization  │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   Punctuation Removal     │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ NLTK Word Tokenization    │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │    Stop-Word Removal      │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   WordNet Lemmatization   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   Clean Text Assembly     │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ TF-IDF Vectorization      │
                               │ (Unigrams + Bigrams)      │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ Cosine Similarity Match   │
                               │ (vs Pre-fitted FAQ Matrix)│
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │ Score >= Threshold (0.25)?   │
                             └───────┬───────────────┬───────┘
                                     │ YES           │ NO
                                     ▼               ▼
                        ┌──────────────────┐  ┌───────────────────────────┐
                        │ Return FAQ Answer│  │ Secondary Fuzzy Fallback  │
                        │ + Match %        │  │ (RapidFuzz / Sequence)    │
                        └──────────────────┘  └──────────────┬────────────┘
                                                             │
                                                     ┌───────┴───────┐
                                                     │ Score >= 0.60?│
                                                     └───┬───────┬───┘
                                                         │ YES   │ NO
                                                         ▼       ▼
                                                    ┌────────┐ ┌───────────────┐
                                                    │ Return │ │ Return Out-of-│
                                                    │ Answer │ │ Domain Message│
                                                    └────────┘ └───────────────┘
```

---

## 🔬 Core Mathematical & NLP Concepts

### 1. TF-IDF (Term Frequency - Inverse Document Frequency)
TF-IDF measures how important a word is to a specific document relative to the entire FAQ corpus:

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

Where:
- $\text{TF}(t, d)$ = Frequency of term $t$ in document $d$.
- $\text{IDF}(t, D) = \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$

> **Optimization**: The `TfidfVectorizer` is trained **ONCE** when the Flask server starts. User queries are transformed against the precomputated vector space in $\mathcal{O}(N)$ time.

### 2. Cosine Similarity
Cosine similarity computes the normalized dot product between the user vector $\vec{U}$ and each FAQ vector $\vec{F_i}$:

$$\text{Cosine Similarity}(\vec{U}, \vec{F_i}) = \frac{\vec{U} \cdot \vec{F_i}}{\|\vec{U}\| \|\vec{F_i}\|} = \frac{\sum U_k F_{i,k}}{\sqrt{\sum U_k^2} \sqrt{\sum F_{i,k}^2}}$$

### 3. Confidence Score & Thresholding
- **Threshold**: Set to `CONFIDENCE_THRESHOLD = 0.25` (25%).
- **Display**: Shown in the UI as **`Match confidence: XX%`** (clarified to the user as similarity metric, not probability).
- **Graceful Fallback**: If $\text{Score} < 0.25$ (and fuzzy score $< 0.60$), the bot returns a helpful out-of-domain response without inventing answers.

---

## 📁 Project Structure

```
FAQBot_AI/
│
├── app.py                 # Flask Server & REST API Routes (/api/chat, /api/faqs, /api/categories)
├── chatbot.py             # Core NLP Engine (NLTK, TF-IDF Vectorizer, Cosine Similarity, Fuzzy Fallback)
├── requirements.txt       # Python dependencies (Flask, scikit-learn, nltk, rapidfuzz)
├── README.md              # Detailed project documentation & evaluation guide
├── .gitignore             # Ignored temporary files & cache
│
├── data/
│   └── faqs.json          # Knowledge base containing 45 generic college FAQs (categories, questions, keywords)
│
├── templates/
│   └── index.html         # HTML5 single-page application UI with ARIA accessibility
│
└── static/
    ├── style.css          # Premium Monochrome Black & White design system CSS
    └── script.js          # Asynchronous JavaScript client for chat API, FAQ accordion, & NLP inspector
```

---

## 🛠️ Installation & Local Setup

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### Step 1: Clone or Navigate to Project
```bash
cd FAQBot_AI
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

> Note: Required NLTK datasets (`punkt`, `stopwords`, `wordnet`) are **automatically downloaded programmatically** upon first launch.

---

## 🚀 Running the Application

Start the Flask development server:

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Test Cases & Verification Results

The application was verified across the mandatory CodeAlpha test matrix:

| Test # | User Query | Expected Behavior | Category | Result |
| :--- | :--- | :--- | :--- | :---: |
| **1** | *"How can I apply for admission?"* | Matches Admission FAQ | Admissions | **PASS** |
| **2** | *"How do I join the college?"* | Synonym expansion via keywords matches Admission | Admissions | **PASS** |
| **3** | *"What happens if my attendance is low?"* | Matches Attendance shortage/condonation FAQ | Attendance | **PASS** |
| **4** | *"When are semester exams conducted?"* | Matches Examination schedule FAQ | Examinations | **PASS** |
| **5** | *"How can I get a scholarship?"* | Matches Scholarship application FAQ | Scholarships | **PASS** |
| **6** | *"Does the college provide internships?"* | Matches Internship assistance FAQ | Internships | **PASS** |
| **7** | *"How can I use the library?"* | Matches Library timing/access FAQ | Library | **PASS** |
| **8** | *"What is the hostel facility?"* | Matches Hostel & accommodation FAQ | Hostel | **PASS** |
| **9** | *"Who is the president of the United States?"* | Out-of-domain response; offers suggested questions | None | **PASS** |
| **10** | *"" (Empty message)* | Form validation error: *"Please enter a question."* | None | **PASS** |
| **11** | *2000+ character message* | Length validation error: *"Keep under 2000 chars"* | None | **PASS** |
| **12** | *"How can I aply for admision?"* (Typos) | Secondary Fuzzy Fallback matches Admission FAQ | Admissions | **PASS** |

---

## 📤 Instructions for CodeAlpha GitHub Submission

1. **Initialize Git Repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - CodeAlpha AI Internship Task 2 FAQBot AI"
   ```

2. **Push to GitHub**:
   Create a new public repository on GitHub named `CodeAlpha_FAQBot_AI` and run:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/CodeAlpha_FAQBot_AI.git
   git branch -M main
   git push -u origin main
   ```

3. **Submission Details**:
   - **Repository Link**: `https://github.com/YOUR_USERNAME/CodeAlpha_FAQBot_AI`
   - **Task Name**: Artificial Intelligence Internship Task 2 - Intelligent FAQ Chatbot
   - **Key Tech Stack**: Python, Flask, NLTK, Scikit-Learn (TF-IDF), Cosine Similarity, RapidFuzz.

---

## ⚡ Future Enhancements
- Integration of Word Embeddings (Word2Vec / GloVe) for dense semantic vector representations.
- Admin portal for dynamic CRUD operations on `faqs.json`.
- Voice query input via Web Speech API.

---

*Developed with precision for CodeAlpha Artificial Intelligence Internship.*
