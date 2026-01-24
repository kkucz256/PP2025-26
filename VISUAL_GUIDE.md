# 🎨 Visual Guide - API Integration

Wizualne wyjaśnienie jak wszystko działa.

## 🔄 Przepływ Review Questions

```
┌─────────────────────────────────────────────────────────────┐
│                      USER FLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Użytkownik wgrywa PDF                                   │
│     └─→ /quiz/my-notes/upload/                             │
│                                                              │
│  2. Backend generuje pytania (AI)                           │
│     └─→ Pytania w Django session                            │
│                                                              │
│  3. Redirect do review_questions                            │
│     └─→ /quiz/review-questions/                            │
│                                                              │
│  4. JavaScript ładuje pytania z JSON                        │
│     └─→ window.initialQuestions                            │
│                                                              │
│  5. Pytania renderują się w DOM                             │
│     └─→ User widzi edytowalny formularz                    │
│                                                              │
│  6. Użytkownik edytuje pytania                              │
│     ├─→ Zmienia tekst pytań                                │
│     ├─→ Zmienia odpowiedzi                                 │
│     ├─→ Dodaje pytania (+)                                 │
│     └─→ Usuwa pytania (×)                                  │
│                                                              │
│  7. Kliknięcie \"Zapisz Quiz\"                               │
│     └─→ Walidacja danych (frontend)                        │
│                                                              │
│  8. POST do API                                             │
│     └─→ /api/quiz/quizzes/                                 │
│                                                              │
│  9. API zapisuje do bazy (transaction)                      │
│     ├─→ Tworzy Quiz                                        │
│     ├─→ Tworzy Questions                                   │
│     └─→ Tworzy Answers                                     │
│                                                              │
│  10. Response 201 Created                                   │
│      └─→ Success message                                   │
│                                                              │
│  11. Auto-redirect                                          │
│      └─→ /quiz/my-quizzes/                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🗂️ Struktura Danych

### Session (Django)
```
request.session = {
    'user_id': 1,
    'username': 'john',
    'temp_questions': [
        {
            'question': 'Co to jest DNA?',
            'options': ['...', '...', '...', '...'],
            'correct': 0
        },
        ...
    ]
}
```

### Window Global (JavaScript)
```javascript
API_BASE_URL = '/api/quiz'
CSRF_TOKEN = 'x1y2z3...'
USER_ID = 1
initialQuestions = [ /* pytania z sesji */ ]

questions = [
    {
        id: 'temp_0',
        question: 'Co to jest DNA?',
        options: ['...', '...', '...', '...'],
        correct: 0,
        answerIds: null  // tylko po pobraniu z API
    },
    ...
]
```

### API Request (POST /quizzes/)
```json
{
  "content": "Biologia - DNA",
  "slug": "biologia-dna",
  "owner_id": 1,
  "questions": [
    {
      "content": "Co to jest DNA?",
      "position": 1,
      "answers": [
        { "content": "...", "is_correct": true },
        { "content": "...", "is_correct": false }
      ]
    }
  ]
}
```

### API Response (201 Created)
```json
{
  "id": 123,
  "content": "Biologia - DNA",
  "slug": "biologia-dna",
  "questions": [
    {
      "id": 456,
      "quiz_id": 123,
      "content": "Co to jest DNA?",
      "position": 1,
      "answers": [
        { "id": 789, "content": "...", "is_correct": true }
      ]
    }
  ]
}
```

## 🎯 Komponent Diagram

```
┌──────────────────────────────────────────────────────────┐
│                  review_questions.html                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Header                                                 │
│  ├─ Title: "Edycja wygenerowanych pytań"               │
│  └─ Cancel button (anuluj)                             │
│                                                          │
│  Form                                                   │
│  ├─ Quiz name input                                     │
│  ├─ Questions container (dynamiczny)                    │
│  │  ├─ Question Card 1                                  │
│  │  │  ├─ Textarea: pytanie                             │
│  │  │  ├─ Options grid                                  │
│  │  │  │  ├─ Radio + Input: Option 1                    │
│  │  │  │  ├─ Radio + Input: Option 2                    │
│  │  │  │  ├─ Radio + Input: Option 3                    │
│  │  │  │  └─ Radio + Input: Option 4                    │
│  │  │  └─ Delete button                                 │
│  │  │                                                   │
│  │  └─ Question Card 2                                  │
│  │     (similar structure)                              │
│  │                                                      │
│  ├─ Add button                                          │
│  └─ Save button                                         │
│                                                          │
│  Notifications                                          │
│  ├─ Loading indicator (pulsing)                         │
│  ├─ Error message (red banner)                          │
│  └─ Success message (green banner)                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 🔗 Komunikacja Frontend-Backend

```
┌─────────────────────────────────────────────────────────┐
│                    REVIEW QUESTIONS                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend (Browser)          Backend (Django)            │
│  ═══════════════════         ═══════════════             │
│                                                          │
│  1. Strona się wczytuje                                  │
│     │                                                    │
│     │─────────── GET /review-questions/ ──→ views.py    │
│     │                       ← HTML + JSON ─  (sesja)    │
│     │                                                    │
│  2. JS parsuje JSON                                      │
│     window.initialQuestions = [...]                      │
│                                                          │
│  3. JS renderuje HTML                                    │
│     document.innerHTML = cards                          │
│                                                          │
│  4. Użytkownik edytuje                                   │
│     textarea.value = nova wartość                       │
│     questions[i].question = nova wartość                │
│                                                          │
│  5. User klika \"Zapisz\"                                 │
│     │                                                    │
│     │─────────── POST /api/quiz/quizzes/ ──→ api.py     │
│     │            Body: { questions: [...] }             │
│     │                                                    │
│     │         (Walidacja)                                │
│     │         (Transakcja)                               │
│     │         (Zapis w BD)                               │
│     │                                                    │
│     │←────────── 201 Created + Quiz ────── ─ Response   │
│     │                                                    │
│  6. Success notification                                 │
│     \"Quiz zapisany!\"                                    │
│                                                          │
│  7. Auto-redirect                                        │
│     window.location = /quiz/my-quizzes/                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 📊 Event Lifecycle

```
┌─────────────────────────────────────────────┐
│        DOMContentLoaded Event                │
└────────────────┬────────────────────────────┘
                 │
                 ├─→ loadQuestionsFromSession()
                 │   └─→ fetch API (fallback)
                 │       └─→ loadQuestionsFromWindow()
                 │           └─→ renderQuestions()
                 │
                 └─→ setupEventListeners()
                     ├─→ addBtn.onclick = addNewQuestion()
                     ├─→ saveBtn.onclick = saveQuiz()
                     └─→ (for each question)
                         ├─→ textarea.onchange = updateQuestionText()
                         ├─→ input.onchange = updateOptionText()
                         └─→ radio.onchange = updateCorrect()

┌────────────────────────────────────────────┐
│      User Clicks \"Save Quiz\"               │
└────────────┬───────────────────────────────┘
             │
             ├─→ Validation
             │   ├─→ Quiz name check
             │   ├─→ Questions count check
             │   ├─→ All text filled check
             │   └─→ All options filled check
             │
             ├─→ (if error) showError(msg)
             │   └─→ return
             │
             └─→ (if valid) saveQuiz()
                 ├─→ showLoading(true)
                 ├─→ POST /api/quiz/quizzes/
                 │   └─→ await response
                 ├─→ showLoading(false)
                 ├─→ showSuccess(msg)
                 └─→ setTimeout(() => redirect())
```

## 🔀 State Management

```
┌──────────────────────────────────────────┐
│         questions Array (Memory)          │
├──────────────────────────────────────────┤
│                                          │
│  questions = [                           │
│    {                                      │
│      id: 'temp_0'                        │
│      question: 'Text...'   ← updateQuestionText()
│      options: [...]        ← updateOptionText()
│      correct: 0            ← radio.onchange
│    },                                     │
│    ...                                    │
│  ]                                        │
│                                          │
│  NOT stored in DOM attributes            │
│  NOT stored in localStorage              │
│  Just in memory for performance          │
│                                          │
└──────────────────────────────────────────┘
```

## 🎨 CSS Architecture

```
┌─────────────────────────────────────────┐
│       review_questions.css              │
├─────────────────────────────────────────┤
│                                         │
│  :root (variables)                      │
│  ├─ --primary: #2563eb                  │
│  ├─ --success: #16a34a                  │
│  ├─ --bg: #f8fafc                       │
│  └─ --surface: #ffffff                  │
│                                         │
│  Layout                                 │
│  ├─ .main-container (max-width)         │
│  ├─ header                              │
│  ├─ .quiz-meta                          │
│  └─ .questions-list                     │
│                                         │
│  Components                             │
│  ├─ .question-card                      │
│  ├─ .options-grid                       │
│  ├─ .btn-delete                         │
│  └─ .btn-primary                        │
│                                         │
│  Animations                             │
│  ├─ @keyframes pulse (loading)          │
│  ├─ @keyframes slideIn (notification)   │
│  └─ @keyframes (transitions)            │
│                                         │
│  Notifications                          │
│  ├─ .loading-indicator                  │
│  ├─ .success-message                    │
│  └─ .error-message                      │
│                                         │
└─────────────────────────────────────────┘
```

## 🔐 Security Flow

```
┌──────────────────────────────────────────┐
│         Security Layers                  │
├──────────────────────────────────────────┤
│                                          │
│  1. Template (Django)                    │
│     └─→ {% csrf_token %} injected        │
│                                          │
│  2. JavaScript                           │
│     └─→ CSRF_TOKEN = '{{ csrf_token }}'  │
│                                          │
│  3. Fetch Request                        │
│     └─→ 'X-CSRFToken': CSRF_TOKEN        │
│                                          │
│  4. Django Ninja API                     │
│     └─→ Walidacja CSRF                   │
│         └─→ Walidacja USER_ID            │
│             └─→ Walidacja danych         │
│                                          │
│  5. Database                             │
│     └─→ ORM protection (SQL injection)   │
│         └─→ Transaction (atomicity)      │
│                                          │
└──────────────────────────────────────────┘
```

## 📱 Responsive Design

```
Desktop (1200px+)
┌─────────────────────────────────────┐
│  Header                             │
├─────────────────────────────────────┤
│  Quiz Name: [Text Input .............]  │
├─────────────────────────────────────┤
│  ┌─── Question 1 ──────────────────┐  │
│  │ [Textarea with question text]    │  │
│  │ ☑ Option 1 [Input field]         │  │
│  │ ☐ Option 2 [Input field]         │  │
│  │ ☐ Option 3 [Input field]         │  │
│  │ ☐ Option 4 [Input field]         │  │
│  │ [Delete]                         │  │
│  └─────────────────────────────────┘  │
│                                      │
│  [+ Add Question] [Save Quiz]        │
└─────────────────────────────────────┘

Mobile (< 768px)
┌────────────────────────┐
│ Header                 │
├────────────────────────┤
│ Quiz Name: [Input]     │
├────────────────────────┤
│ Question 1             │
│ [Textarea]             │
│ ☑ Option [Input]       │
│ ☐ Option [Input]       │
│ ☐ Option [Input]       │
│ ☐ Option [Input]       │
│ [Delete]               │
├────────────────────────┤
│ [+ Add] [Save]         │
└────────────────────────┘
```

## 🎁 Bonus: Code Quality

```
┌──────────────────────────────────────────┐
│      Code Quality Metrics                │
├──────────────────────────────────────────┤
│                                          │
│  JavaScript (review_questions.js)        │
│  ├─ Lines: 402                           │
│  ├─ Functions: 15+                       │
│  ├─ Comments: Comprehensive              │
│  ├─ Error handling: ✅                    │
│  └─ Browser support: Modern              │
│                                          │
│  CSS (review_questions.css)              │
│  ├─ CSS Variables: Used                  │
│  ├─ Responsive: Mobile-first             │
│  ├─ Animations: Smooth                   │
│  └─ Accessibility: WCAG basic            │
│                                          │
│  HTML (review_questions.html)            │
│  ├─ Semantic: Good                       │
│  ├─ Forms: Proper structure              │
│  └─ Accessibility: Labels included       │
│                                          │
│  API (api.py)                            │
│  ├─ Error codes: Proper                  │
│  ├─ Validation: Frontend + Backend       │
│  ├─ Transactions: Atomic                 │
│  └─ Security: CSRF protected             │
│                                          │
└──────────────────────────────────────────┘
```

---

**Wizualne wyjaśnienie będą Ci pomocne aby zrozumieć jak system działa! 🎨**
