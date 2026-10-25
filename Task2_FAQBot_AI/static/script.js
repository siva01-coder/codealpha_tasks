/**
 * FAQBot AI — Intelligent College FAQ Assistant Frontend Application
 * Interacts with Flask backend NLP REST API (/api/chat, /api/categories, /api/faqs).
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatStream = document.getElementById('chatStream');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const suggestionsChips = document.getElementById('suggestionsChips');
    
    // Category & Explorer Elements
    const categoryPills = document.getElementById('categoryPills');
    const categoryCount = document.getElementById('categoryCount');
    const faqAccordionList = document.getElementById('faqAccordionList');
    const faqSearchInput = document.getElementById('faqSearchInput');

    // Inspector Drawer Elements
    const toggleInspectorBtn = document.getElementById('toggleInspectorBtn');
    const closeInspectorBtn = document.getElementById('closeInspectorBtn');
    const inspectorDrawer = document.getElementById('inspectorDrawer');
    const inspRawInput = document.getElementById('inspRawInput');
    const inspTokens = document.getElementById('inspTokens');
    const inspCleanText = document.getElementById('inspCleanText');
    const inspMethod = document.getElementById('inspMethod');
    const inspScore = document.getElementById('inspScore');
    const inspFaqId = document.getElementById('inspFaqId');

    // App State
    let sessionContext = {
        last_category: null,
        last_faq_id: null
    };
    let allFaqs = [];
    let currentCategory = 'All';

    // --------------------------------------------------------------------------
    // INITIALIZATION
    // --------------------------------------------------------------------------
    initApp();

    async function initApp() {
        setupEventListeners();
        await loadCategories();
        await loadFaqs();
    }

    function setupEventListeners() {
        // Form input handlers
        userInput.addEventListener('input', () => {
            const val = userInput.value.trim();
            sendBtn.disabled = val.length === 0;
        });

        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleSendUserMessage();
        });

        clearChatBtn.addEventListener('click', clearChat);

        // Click on suggested questions
        suggestionsChips.addEventListener('click', (e) => {
            const chip = e.target.closest('.chip');
            if (chip) {
                const questionText = chip.getAttribute('data-question') || chip.innerText.trim();
                userInput.value = questionText;
                sendBtn.disabled = false;
                handleSendUserMessage();
            }
        });

        // Search input filter in FAQ Explorer
        faqSearchInput.addEventListener('input', (e) => {
            filterFaqs(e.target.value.toLowerCase());
        });

        // Inspector drawer toggle
        toggleInspectorBtn.addEventListener('click', () => {
            inspectorDrawer.classList.toggle('open');
            inspectorDrawer.setAttribute('aria-hidden', !inspectorDrawer.classList.contains('open'));
        });

        closeInspectorBtn.addEventListener('click', () => {
            inspectorDrawer.classList.remove('open');
            inspectorDrawer.setAttribute('aria-hidden', 'true');
        });
    }

    // --------------------------------------------------------------------------
    // CHAT ENGINE
    // --------------------------------------------------------------------------
    async function handleSendUserMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Clear input & disable send button
        userInput.value = '';
        sendBtn.disabled = true;

        // Append User message to stream
        appendUserMessage(message);

        // Show typing indicator
        const typingId = appendTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    context: sessionContext
                })
            });

            const data = await response.json();
            removeTypingIndicator(typingId);

            if (data.success) {
                appendBotMessage(data);

                // Update session context
                if (data.category) {
                    sessionContext.last_category = data.category;
                    sessionContext.last_faq_id = data.faq_id;
                }

                // Update NLP Inspector Panel
                updateNLPInspector(data);

                // Update Suggested Questions Chips if provided
                if (data.suggested_questions && data.suggested_questions.length > 0) {
                    renderSuggestedChips(data.suggested_questions);
                }
            } else {
                appendBotErrorMessage(data.error || "An error occurred.");
            }
        } catch (err) {
            console.error("Chat API Error:", err);
            removeTypingIndicator(typingId);
            appendBotErrorMessage("Unable to connect to FAQBot AI server. Please check your connection.");
        }
    }

    function appendUserMessage(text) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper user-message';
        wrapper.innerHTML = `
            <div class="message-content">
                <div class="message-bubble">
                    <p>${escapeHTML(text)}</p>
                </div>
                <div class="message-meta">
                    <span>${timeStr}</span>
                </div>
            </div>
        `;
        chatStream.appendChild(wrapper);
        scrollToBottom();
    }

    function appendBotMessage(data) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper bot-message';

        let metaHtml = '';
        if (data.confidence > 0 && data.category) {
            metaHtml = `
                <div class="message-meta">
                    <span class="meta-tag meta-confidence">Match confidence: ${data.confidence}%</span>
                    <span class="meta-tag">Category: ${escapeHTML(data.category)}</span>
                    <span>${timeStr}</span>
                </div>
            `;
        } else {
            metaHtml = `
                <div class="message-meta">
                    <span class="meta-tag">Notice</span>
                    <span>${timeStr}</span>
                </div>
            `;
        }

        wrapper.innerHTML = `
            <div class="bot-avatar">AI</div>
            <div class="message-content">
                <div class="message-bubble">
                    <p>${escapeHTML(data.answer)}</p>
                </div>
                ${metaHtml}
            </div>
        `;

        chatStream.appendChild(wrapper);
        scrollToBottom();
    }

    function appendBotErrorMessage(errorText) {
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper bot-message';
        wrapper.innerHTML = `
            <div class="bot-avatar">AI</div>
            <div class="message-content">
                <div class="message-bubble" style="border-color: #666666;">
                    <p>${escapeHTML(errorText)}</p>
                </div>
            </div>
        `;
        chatStream.appendChild(wrapper);
        scrollToBottom();
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper bot-message';
        wrapper.id = id;
        wrapper.innerHTML = `
            <div class="bot-avatar">AI</div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="typing-indicator">
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                        <span class="typing-dot"></span>
                    </div>
                </div>
            </div>
        `;
        chatStream.appendChild(wrapper);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function clearChat() {
        chatStream.innerHTML = `
            <div class="message-wrapper bot-message">
                <div class="bot-avatar">AI</div>
                <div class="message-content">
                    <div class="message-bubble">
                        <p>Hello! I'm <strong>FAQBot AI</strong>, your intelligent college assistant. Ask me anything about admissions, academics, fees, scholarships, exams, placements, hostel, library, or campus regulations.</p>
                    </div>
                    <div class="message-meta">
                        <span class="meta-tag">Session Reset</span>
                    </div>
                </div>
            </div>
        `;
        sessionContext = { last_category: null, last_faq_id: null };
        renderSuggestedChips([
            "How can I apply for admission?",
            "What is the attendance requirement?",
            "When are semester exams conducted?",
            "How can I apply for scholarships?",
            "Are internships available?"
        ]);
    }

    function renderSuggestedChips(questions) {
        suggestionsChips.innerHTML = questions.map(q => 
            `<button class="chip" data-question="${escapeHTML(q)}">${escapeHTML(q)}</button>`
        ).join('');
    }

    function scrollToBottom() {
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    // --------------------------------------------------------------------------
    // CATEGORIES & FAQ EXPLORER
    // --------------------------------------------------------------------------
    async function loadCategories() {
        try {
            const res = await fetch('/api/categories');
            const data = await res.json();
            if (data.success) {
                categoryCount.innerText = data.categories.length;
                renderCategoryPills(data.categories);
            }
        } catch (e) {
            console.error("Failed to load categories:", e);
        }
    }

    function renderCategoryPills(categories) {
        let html = `<button class="pill active" data-category="All">All</button>`;
        categories.forEach(cat => {
            html += `<button class="pill" data-category="${escapeHTML(cat.name)}">${escapeHTML(cat.name)} (${cat.count})</button>`;
        });
        categoryPills.innerHTML = html;

        categoryPills.addEventListener('click', (e) => {
            const pill = e.target.closest('.pill');
            if (!pill) return;
            document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            currentCategory = pill.getAttribute('data-category');
            filterFaqs(faqSearchInput.value.toLowerCase());
        });
    }

    async function loadFaqs() {
        try {
            const res = await fetch('/api/faqs');
            const data = await res.json();
            if (data.success) {
                allFaqs = data.faqs;
                renderFaqAccordion(allFaqs);
            }
        } catch (e) {
            console.error("Failed to load FAQs:", e);
        }
    }

    function renderFaqAccordion(faqs) {
        if (faqs.length === 0) {
            faqAccordionList.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:10px;">No FAQs found.</div>`;
            return;
        }

        faqAccordionList.innerHTML = faqs.map(faq => `
            <div class="faq-item" id="faq-item-${faq.id}">
                <button class="faq-question-btn" onclick="toggleFaqAccordion(${faq.id})">
                    <span>${escapeHTML(faq.question)}</span>
                    <span class="faq-cat-tag">${escapeHTML(faq.category)}</span>
                </button>
                <div class="faq-answer-panel">
                    <p>${escapeHTML(faq.answer)}</p>
                    <div class="faq-actions">
                        <button class="faq-ask-btn" onclick="askFaqQuestion('${escapeHTML(faq.question)}')">Ask in Chat →</button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    window.toggleFaqAccordion = function(id) {
        const item = document.getElementById(`faq-item-${id}`);
        if (item) {
            const isOpen = item.classList.contains('open');
            document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('open'));
            if (!isOpen) item.classList.add('open');
        }
    };

    window.askFaqQuestion = function(question) {
        userInput.value = question;
        sendBtn.disabled = false;
        handleSendUserMessage();
    };

    function filterFaqs(searchTerm) {
        const filtered = allFaqs.filter(faq => {
            const matchesCat = (currentCategory === 'All' || faq.category === currentCategory);
            const matchesSearch = !searchTerm || 
                faq.question.toLowerCase().includes(searchTerm) || 
                faq.answer.toLowerCase().includes(searchTerm) ||
                (faq.keywords && faq.keywords.some(k => k.toLowerCase().includes(searchTerm)));
            return matchesCat && matchesSearch;
        });
        renderFaqAccordion(filtered);
    }

    // --------------------------------------------------------------------------
    // NLP INSPECTOR PANEL
    // --------------------------------------------------------------------------
    function updateNLPInspector(data) {
        if (!data.nlp_pipeline) return;

        const p = data.nlp_pipeline;
        inspRawInput.innerText = p.input || '-';

        // Tokens
        if (p.tokens && p.tokens.length > 0) {
            inspTokens.innerHTML = p.tokens.map(t => `<span class="token-tag">${escapeHTML(t)}</span>`).join('');
        } else {
            inspTokens.innerHTML = '<code>None</code>';
        }

        inspCleanText.innerText = p.cleaned_text || '-';
        inspMethod.innerText = data.matching_method || 'TF-IDF + Cosine Similarity';
        inspScore.innerText = `${data.confidence}% (Raw: ${(data.confidence / 100).toFixed(4)})`;
        inspFaqId.innerText = data.faq_id !== null ? `#${data.faq_id}` : 'None (Below Threshold)';
    }

    // Helper utilities
    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
