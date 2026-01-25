// Zmienne globalne do przechowywania pytań
let questions = [];
let questionIdCounter = 0;

// Inicjalizacja aplikacji
document.addEventListener('DOMContentLoaded', function() {
    loadQuestionsFromSession();
    setupEventListeners();
});

/**
 * Załaduj pytania z sesji (wygenerowane z PDF)
 */
function loadQuestionsFromSession() {
    console.log('📥 loadQuestionsFromSession() start');
    
    // 1. NAJPIERW - spróbuj załadować z window.initialQuestions (wstrzyknięte z Django template)
    if (typeof window.initialQuestions !== 'undefined' && Array.isArray(window.initialQuestions) && window.initialQuestions.length > 0) {
        console.log('✓ Ładuję pytania z Django sesji:', window.initialQuestions.length);
        questions = window.initialQuestions.map((q, idx) => ({
            id: `temp_${idx}`,
            question: q.question || q.text || '',
            options: Array.isArray(q.options) ? q.options : [],
            correct: q.correct !== undefined ? q.correct : 0
        }));
        console.log('✓ Pytania zmapowane:', questions);
        renderQuestions();
        return; // Sukces, wyjdź
    }
    
    console.log('⚠️ window.initialQuestions nie dostępne');
    
    // 2. POTEM - spróbuj pobrać z API (dla istniejących quizów)
    console.log('Pytania nie w sesji, próbuję pobrać z API...');
    if (typeof USER_ID === 'undefined' || USER_ID === null) {
        console.warn('USER_ID nie dostępny, pomijam API');
        loadQuestionsFromWindow();
        return;
    }
    
    fetch(`${API_BASE_URL}/questions/?user_id=${USER_ID}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                console.log('✓ Ładuję pytania z API:', data.length);
                // Załaduj pytania z API
                questions = data.map(q => ({
                    id: q.id,
                    question: q.content,
                    options: q.answers.map(a => a.content),
                    answerIds: q.answers.map(a => a.id),
                    correct: q.answers.findIndex(a => a.is_correct),
                    answers: q.answers
                }));
                renderQuestions();
            } else {
                // 3. NA KOŃCU - fallback na sessionStorage
                console.log('API zwróciło pustą listę, próbuję sessionStorage...');
                loadQuestionsFromWindow();
            }
        })
        .catch(error => {
            console.log('Błąd API, fallback na sessionStorage:', error);
            // Fallback - załaduj ze zmiennych globalnych lub session
            loadQuestionsFromWindow();
        });
}

/**
 * Załaduj pytania bezpośrednio z session storage (generowane z PDF)
 */
function loadQuestionsFromWindow() {
    // Sprawdź czy są pytania w window object (wstrzyknięte z contextu Django)
    if (window.initialQuestions && Array.isArray(window.initialQuestions)) {
        questions = window.initialQuestions.map((q, idx) => ({
            id: `new_${idx}`,
            question: q.question || q.text || '',
            options: q.options || [],
            correct: q.correct !== undefined ? q.correct : 0
        }));
        renderQuestions();
    } else {
        // Próbuj session storage
        const stored = sessionStorage.getItem('temp_questions');
        if (stored) {
            try {
                const parsed = JSON.parse(stored);
                questions = parsed.map((q, idx) => ({
                    id: `temp_${idx}`,
                    question: q.question || q.text || '',
                    options: q.options || [],
                    correct: q.correct !== undefined ? q.correct : 0
                }));
                renderQuestions();
            } catch (e) {
                console.error('Błąd parsowania pytań:', e);
            }
        }
    }
}

/**
 * Ustawienie listenery na przyciski i formularze
 */
function setupEventListeners() {
    const addBtn = document.getElementById('add-question-btn');
    const saveBtn = document.getElementById('save-quiz-btn');
    
    if (addBtn) {
        addBtn.addEventListener('click', addNewQuestion);
    }
    
    if (saveBtn) {
        saveBtn.addEventListener('click', saveQuiz);
    }

    // Obsługa ENTER w polach tekstowych do usuwania focus
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.classList.contains('edit-opt')) {
            e.preventDefault();
        }
    });
}

/**
 * Renderuj pytania na stronie
 */
function renderQuestions() {
    const container = document.getElementById('questions-container');
    console.log('🎨 renderQuestions() - container:', container ? '✓ znaleziony' : '✗ NIE ZNALEZIONY');
    console.log('🎨 Liczba pytań do renderowania:', questions.length);
    
    if (!container) {
        console.error('❌ Container #questions-container nie znaleziony!');
        return;
    }
    
    container.innerHTML = '';
    
    if (questions.length === 0) {
        console.warn('⚠️ Brak pytań do renderowania');
        return;
    }
    
    questions.forEach((q, idx) => {
        console.log(`🎨 Renderuję pytanie ${idx + 1}:`, q.question);
        const questionCard = createQuestionCard(q, idx);
        container.appendChild(questionCard);
    });
    
    console.log('✓ Wszystkie pytania renderowane');
    reindexQuestions();
}

/**
 * Stwórz kartę pytania (HTML element)
 */
function createQuestionCard(question, index) {
    console.log(`  📋 createQuestionCard() - idx:${index}, id:${question.id}`);
    
    const div = document.createElement('div');
    div.className = 'panel question-card';
    div.setAttribute('data-question-id', question.id);
    
    const options = question.options || [];
    console.log(`  - Pytanie: ${question.question.substring(0, 50)}...`);
    console.log(`  - Opcje: ${options.length}, Poprawna: ${question.correct}`);
    
    const optionsHTML = options.map((opt, optIdx) => `
        <div class="opt-row">
            <input type="radio" name="q_${question.id}_correct" 
                   value="${optIdx}" 
                   ${question.correct === optIdx ? 'checked' : ''} 
                   required>
            <input type="text" class="edit-opt" 
                   value="${escapeHtml(opt)}" 
                   data-question-id="${question.id}"
                   data-option-index="${optIdx}"
                   required>
        </div>
    `).join('');
    
    div.innerHTML = `
        <div class="q-header">
            <h3>Pytanie <span class="q-index">${index + 1}</span></h3>
            <button type="button" class="btn-delete" onclick="removeQuestion(event)">Usuń</button>
        </div>
        
        <textarea class="edit-q" 
                  data-question-id="${question.id}"
                  required>${escapeHtml(question.question)}</textarea>
        
        <div class="options-grid">
            ${optionsHTML}
        </div>
    `;
    
    // Dodaj event listenery do pól
    const textarea = div.querySelector('.edit-q');
    if (textarea) {
        textarea.addEventListener('change', updateQuestionText);
    }
    
    const optInputs = div.querySelectorAll('.edit-opt');
    optInputs.forEach(input => {
        input.addEventListener('change', updateOptionText);
    });
    
    const radioButtons = div.querySelectorAll(`input[name="q_${question.id}_correct"]`);
    radioButtons.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const qId = e.target.getAttribute('name').replace('_correct', '').replace('q_', '');
            const qIdx = questions.findIndex(q => q.id.toString() === qId);
            if (qIdx !== -1) {
                questions[qIdx].correct = parseInt(e.target.value);
            }
        });
    });
    
    return div;
}

/**
 * Escape HTML do bezpiecznego wyświetlania
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Update tekstu pytania
 */
function updateQuestionText(event) {
    const textarea = event.target;
    const questionId = textarea.getAttribute('data-question-id');
    const questionIdx = questions.findIndex(q => q.id.toString() === questionId);
    
    if (questionIdx !== -1) {
        questions[questionIdx].question = textarea.value;
    }
}

/**
 * Update tekstu odpowiedzi
 */
function updateOptionText(event) {
    const input = event.target;
    const questionId = input.getAttribute('data-question-id');
    const optionIndex = parseInt(input.getAttribute('data-option-index'));
    const questionIdx = questions.findIndex(q => q.id.toString() === questionId);
    
    if (questionIdx !== -1 && questions[questionIdx].options) {
        questions[questionIdx].options[optionIndex] = input.value;
    }
}

/**
 * Dodaj nowe pytanie ręcznie
 */
function addNewQuestion(event) {
    event.preventDefault();
    
    const newQuestion = {
        id: `new_${Date.now()}`,
        question: '',
        options: ['', '', '', ''],
        correct: 0
    };
    
    questions.push(newQuestion);
    renderQuestions();
    
    // Scroll do nowego pytania
    const lastCard = document.querySelector('.question-card:last-of-type');
    if (lastCard) {
        lastCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        const textarea = lastCard.querySelector('.edit-q');
        if (textarea) textarea.focus();
    }
}

/**
 * Usuń pytanie
 */
function removeQuestion(event) {
    event.preventDefault();
    
    if (!confirm("Czy na pewno chcesz usunąć to pytanie? Te zmiany będą nieodwracalne.")) {
        return;
    }
    
    const card = event.target.closest('.question-card');
    if (!card) return;
    
    const questionId = card.getAttribute('data-question-id');
    questions = questions.filter(q => q.id.toString() !== questionId);
    
    renderQuestions();
}

/**
 * Przenumeruj pytania
 */
function reindexQuestions() {
    const indices = document.querySelectorAll('.q-index');
    indices.forEach((span, index) => {
        span.innerText = index + 1;
    });
}

/**
 * Zapisz quiz do API
 */
async function saveQuiz(event) {
    event.preventDefault();
    
    const quizName = document.getElementById('quiz_name').value.trim();
    
    if (!quizName) {
        showError('Proszę podać nazwę quizu');
        return;
    }
    
    if (questions.length === 0) {
        showError('Brak pytań do zapisania');
        return;
    }
    
    // Validacja wszystkich pytań
    for (let q of questions) {
        if (!q.question.trim()) {
            showError('Wszystkie pytania muszą mieć treść');
            return;
        }
        if (!q.options.every(opt => opt.trim())) {
            showError('Wszystkie opcje odpowiedzi muszą być wypełnione');
            return;
        }
    }
    
    showLoading(true);
    
    try {
        // 1. Stwórz quiz
        const quizData = {
            content: quizName,
            slug: quizName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
            owner_id: USER_ID,
            questions: []
        };
        
        // 2. Przygotuj pytania z odpowiedziami
        quizData.questions = questions.map((q, idx) => ({
            content: q.question,
            position: idx + 1,
            answers: q.options.map((opt, optIdx) => ({
                content: opt,
                is_correct: optIdx === q.correct
            }))
        }));
        
        // 3. Wyślij do API
        const response = await fetch(`${API_BASE_URL}/quizzes/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify(quizData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Błąd zapisu quizu');
        }
        
        const result = await response.json();
        
        showLoading(false);
        showSuccess(`Quiz "${quizName}" został pomyślnie zapisany!`);
        
        sessionStorage.removeItem('temp_questions');
        
        setTimeout(() => {
            window.location.href = '../my-quizzes';
        }, 1500);
        
    } catch (error) {
        console.error('Błąd zapisu:', error);
        showLoading(false);
        showError(`Błąd: ${error.message}`);
    }
}

/**
 * Pokaż wiadomość o błędzie
 */
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    if (errorDiv && errorText) {
        errorText.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

/**
 * Pokaż wiadomość o sukcesie
 */
function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
        successDiv.querySelector('p').textContent = message;
        successDiv.style.display = 'block';
    }
}

/**
 * Pokaż/ukryj indicator loadingu
 */
function showLoading(show) {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
}