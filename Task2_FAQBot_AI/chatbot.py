import json
import os
import re
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Try importing NLTK and resources gracefully
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Try importing rapidfuzz or fallback to difflib
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    import difflib
    HAS_RAPIDFUZZ = False

# Programmatically ensure NLTK resources are available
def ensure_nltk_resources():
    resources = [
        ('tokenizers/punkt', 'punkt'),
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet'),
        ('corpora/omw-1.4', 'omw-1.4')
    ]
    for res_path, res_name in resources:
        try:
            nltk.data.find(res_path)
        except LookupError:
            try:
                nltk.download(res_name, quiet=True)
            except Exception as e:
                print(f"Warning: Could not download NLTK resource '{res_name}': {e}")

ensure_nltk_resources()


class FAQChatbot:
    """
    NLP Engine for FAQBot AI.
    Implements Text Preprocessing, TF-IDF Vectorization, Cosine Similarity Matching,
    Fuzzy Matching Fallback, and Session Context handling.
    """
    CONFIDENCE_THRESHOLD = 0.25  # Minimum similarity score required (25%)

    def __init__(self, data_path=None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, 'data', 'faqs.json')
        
        self.data_path = data_path
        self.faqs = []
        self.categories = []
        self.cleaned_faq_corpus = []
        self.vectorizer = None
        self.faq_vectors = None
        self.lemmatizer = WordNetLemmatizer()

        # Load stop words safely
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
                "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
                'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself',
                'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
                'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
                'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a',
                'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
                'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
                'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
                'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
                'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
                'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o',
                're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't"
            }

        self.load_faqs()
        self.build_tfidf()

    def load_faqs(self):
        """Loads FAQ dataset from JSON file."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"FAQ data file not found at {self.data_path}")

        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.faqs = json.load(f)

        # Extract unique categories
        cats = sorted(list(set(faq['category'] for faq in self.faqs)))
        self.categories = cats
        print(f"[FAQChatbot] Successfully loaded {len(self.faqs)} FAQs across {len(self.categories)} categories.")

    def preprocess_text(self, text):
        """
        Full NLP Preprocessing Pipeline:
        Input Text -> Lowercase -> Punctuation Removal -> Tokenization -> Stop-word Removal -> Lemmatization -> Clean Text
        """
        if not text:
            return ""

        # Step 1: Lowercase
        text_lower = text.lower()

        # Step 2: Remove punctuation
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)

        # Step 3: Tokenization
        try:
            tokens = word_tokenize(text_clean)
        except Exception:
            tokens = text_clean.split()

        # Step 4: Stop-word removal & Lemmatization
        cleaned_tokens = []
        for token in tokens:
            token = token.strip()
            if token and token not in self.stop_words and not token.isdigit():
                lemma = self.lemmatizer.lemmatize(token)
                cleaned_tokens.append(lemma)

        return " ".join(cleaned_tokens)

    def get_pipeline_details(self, raw_text):
        """Returns step-by-step NLP execution details for UI visualization."""
        if not raw_text:
            return {}

        text_lower = raw_text.lower()
        text_no_punc = re.sub(r'[^\w\s]', ' ', text_lower)
        try:
            raw_tokens = word_tokenize(text_no_punc)
        except Exception:
            raw_tokens = text_no_punc.split()

        tokens_no_stop = [t for t in raw_tokens if t not in self.stop_words]
        lemmas = [self.lemmatizer.lemmatize(t) for t in tokens_no_stop]
        final_clean = " ".join(lemmas)

        return {
            "input": raw_text,
            "lowercase": text_lower,
            "tokens": raw_tokens,
            "filtered_tokens": tokens_no_stop,
            "lemmas": lemmas,
            "cleaned_text": final_clean
        }

    def build_tfidf(self):
        """
        Precomputes cleaned text for all FAQs (Question + Keywords + Category)
        and fits the TF-IDF Vectorizer ONCE at server startup.
        """
        self.cleaned_faq_corpus = []
        for faq in self.faqs:
            # Combine question + keywords + category for richer semantic matching
            keywords_str = " ".join(faq.get("keywords", []))
            combined_text = f"{faq['question']} {keywords_str} {faq['category']}"
            cleaned = self.preprocess_text(combined_text)
            self.cleaned_faq_corpus.append(cleaned)

        # Initialize TF-IDF Vectorizer with unigrams & bigrams
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.faq_vectors = self.vectorizer.fit_transform(self.cleaned_faq_corpus)
        print(f"[FAQChatbot] TF-IDF Matrix created with shape {self.faq_vectors.shape}.")

    def _fuzzy_match_fallback(self, cleaned_query, raw_query):
        """
        Fuzzy matching secondary fallback layer using RapidFuzz or Difflib.
        Triggered when TF-IDF cosine similarity falls below the confidence threshold.
        """
        best_score = 0.0
        best_idx = -1

        for i, faq in enumerate(self.faqs):
            target_text = f"{faq['question']} {' '.join(faq.get('keywords', []))}"
            if HAS_RAPIDFUZZ:
                score = fuzz.token_set_ratio(raw_query.lower(), target_text.lower()) / 100.0
            else:
                score = difflib.SequenceMatcher(None, cleaned_query, self.cleaned_faq_corpus[i]).ratio()

            if score > best_score:
                best_score = score
                best_idx = i

        return best_idx, best_score

    def get_response(self, user_query, session_context=None):
        """
        Processes a user question and returns the best matching FAQ response.
        
        Args:
            user_query (str): The raw input question from the user.
            session_context (dict, optional): Session history containing last_category or last_faq_id.
            
        Returns:
            dict: Structured response with answer, category, confidence, faq_id, matching method, and NLP steps.
        """
        if not user_query or not user_query.strip():
            return {
                "success": False,
                "error": "Please enter a question.",
                "answer": "Please enter a valid question.",
                "confidence": 0,
                "category": None,
                "faq_id": None
            }

        if len(user_query) > 2000:
            return {
                "success": False,
                "error": "Please keep your question below 2000 characters.",
                "answer": "Your question is too long. Please keep it under 2000 characters.",
                "confidence": 0,
                "category": None,
                "faq_id": None
            }

        # Step 1: Execute NLP Preprocessing Pipeline
        nlp_pipeline = self.get_pipeline_details(user_query)
        cleaned_query = nlp_pipeline["cleaned_text"]

        # If preprocessing left nothing (e.g., only stop words or symbols like "what is the")
        if not cleaned_query:
            cleaned_query = user_query.lower()

        # Step 2: Vectorize User Query using pre-fitted vectorizer
        user_vector = self.vectorizer.transform([cleaned_query])

        # Step 3: Compute Cosine Similarity against all FAQ vectors
        similarities = cosine_similarity(user_vector, self.faq_vectors)[0]

        # Apply Context Boost if follow-up prompt is detected
        last_category = session_context.get("last_category") if session_context else None
        if last_category and ("it" in user_query.lower().split() or "that" in user_query.lower().split() or "this" in user_query.lower().split() or len(user_query.split()) <= 4):
            for i, faq in enumerate(self.faqs):
                if faq["category"] == last_category:
                    similarities[i] += 0.08  # Small context boost for continuous category chat

        best_idx = int(similarities.argmax())
        best_score = float(similarities[best_idx])
        matching_method = "TF-IDF + Cosine Similarity"

        # Step 4: Fallback to Fuzzy Matching if TF-IDF score is below threshold
        if best_score < self.CONFIDENCE_THRESHOLD:
            fuzzy_idx, fuzzy_score = self._fuzzy_match_fallback(cleaned_query, user_query)
            # Require high confidence for fuzzy fallback (>= 0.60)
            if fuzzy_score >= 0.60 and fuzzy_score > best_score:
                best_idx = fuzzy_idx
                best_score = fuzzy_score * 0.85  # Slightly discount fuzzy matching confidence
                matching_method = "Fuzzy Matching Fallback"

        # Step 5: Check against CONFIDENCE_THRESHOLD
        if best_score >= self.CONFIDENCE_THRESHOLD:
            matched_faq = self.faqs[best_idx]
            confidence_percentage = int(min(100, max(0, round(best_score * 100))))

            return {
                "success": True,
                "answer": matched_faq["answer"],
                "category": matched_faq["category"],
                "confidence": confidence_percentage,
                "faq_id": matched_faq["id"],
                "matched_question": matched_faq["question"],
                "keywords": matched_faq.get("keywords", []),
                "matching_method": matching_method,
                "nlp_pipeline": nlp_pipeline,
                "suggested_questions": self.get_suggested_questions(exclude_id=matched_faq["id"], category=matched_faq["category"])
            }

        # Step 6: Unknown / Out-of-Domain Response if below threshold
        low_confidence_pct = int(min(100, max(0, round(best_score * 100))))
        return {
            "success": True,
            "answer": "I'm currently trained to answer college-related FAQs. I couldn't find a reliable answer to that question. Please try asking in a different way or pick from the suggested questions below.",
            "category": None,
            "confidence": low_confidence_pct,
            "faq_id": None,
            "matched_question": None,
            "matching_method": "Below Confidence Threshold (<25%)",
            "nlp_pipeline": nlp_pipeline,
            "suggested_questions": [
                "How can I apply for admission?",
                "What is the attendance requirement?",
                "When are semester exams conducted?",
                "Does the college provide internships?",
                "How can I apply for scholarships?"
            ]
        }

    def get_suggested_questions(self, limit=4, exclude_id=None, category=None):
        """Generates contextual suggested questions for the user UI."""
        suggestions = []
        if category:
            same_cat = [f["question"] for f in self.faqs if f["category"] == category and f["id"] != exclude_id]
            suggestions.extend(same_cat[:2])

        default_qs = [
            "How can I apply for admission?",
            "What is the attendance requirement?",
            "When are semester exams conducted?",
            "How can I apply for scholarships?",
            "Does the college provide internships?",
            "What facilities does the library provide?",
            "Are separate hostel facilities available?"
        ]
        for q in default_qs:
            if len(suggestions) >= limit:
                break
            if q not in suggestions:
                suggestions.append(q)

        return suggestions[:limit]

    def get_categories(self):
        """Returns list of categories with item counts."""
        cat_counts = {}
        for faq in self.faqs:
            c = faq["category"]
            cat_counts[c] = cat_counts.get(c, 0) + 1
        
        return [{"name": cat, "count": count} for cat, count in cat_counts.items()]

    def get_faqs_by_category(self, category_name=None):
        """Filters FAQs by category or returns all."""
        if not category_name or category_name == "All":
            return self.faqs
        return [f for f in self.faqs if f["category"].lower() == category_name.lower()]
