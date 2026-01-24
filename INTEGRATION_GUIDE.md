# Poradnik Integracji - Inne Templates

Jeśli chcesz używać API w innych stronach (my_quizzes, start_quiz, etc), poniżej znajdziesz poradnik.

## 1. Podstawowe Setup

### Dodaj do HTML header'a:
```html
{% load static %}
<script src="{% static 'quiz/js/api-client.js' %}"></script>
<script>
    // Globalne zmienne
    const API = new QuizAPI('/api/quiz', '{{ csrf_token }}');
    const USER_ID = {{ request.session.user_id|default:'null' }};
</script>
```

## 2. Pobranie listy quizów dla użytkownika

### JavaScript:
```javascript
async function loadMyQuizzes() {
    try {
        const response = await API.getQuizzes(USER_ID);
        const quizzes = response.quizzes;
        renderQuizzes(quizzes);
    } catch (error) {
        console.error('Błąd ładowania quizów:', error);
        showError('Nie udało się załadować quizów');
    }
}

function renderQuizzes(quizzes) {
    const container = document.getElementById('quizzes-container');
    container.innerHTML = '';
    
    quizzes.forEach(quiz => {
        const card = document.createElement('div');
        card.className = 'quiz-card';
        card.innerHTML = `
            <h3>${escapeHtml(quiz.content)}</h3>
            <p>Pytań: ${quiz.questions?.length || 0}</p>
            <button onclick="startQuiz(${quiz.id})">Rozpocznij</button>
            <button onclick="editQuiz(${quiz.id})">Edytuj</button>
        `;
        container.appendChild(card);
    });
}

// Inicjalizacja
document.addEventListener('DOMContentLoaded', loadMyQuizzes);
```

## 3. Rozpoczęcie quizu (tworzenie attempt'u)

```javascript
async function startQuiz(quizId) {
    try {
        const attempt = await API.createAttempt({
            quiz_id: quizId,
            user_id: USER_ID
        });
        
        // Przechowaj ID attempt'u
        sessionStorage.setItem('currentAttemptId', attempt.id);
        
        // Przechoń ID quizu
        sessionStorage.setItem('currentQuizId', quizId);
        
        // Załaduj quiz
        const quiz = await API.getQuiz(quizId);
        renderQuizForAttempt(quiz, attempt.id);
    } catch (error) {
        showError('Nie udało się rozpocząć quizu');
    }
}

function renderQuizForAttempt(quiz, attemptId) {
    const container = document.getElementById('quiz-container');
    container.innerHTML = '';
    
    quiz.questions.forEach((question, idx) => {
        const div = document.createElement('div');
        div.className = 'question';
        
        let answersHTML = question.answers.map(answer => `
            <label>
                <input type="checkbox" data-answer-id="${answer.id}" 
                       data-question-id="${question.id}">
                ${escapeHtml(answer.content)}
            </label>
        `).join('');
        
        div.innerHTML = `
            <h4>Pytanie ${idx + 1}: ${escapeHtml(question.content)}</h4>
            <div class="answers">
                ${answersHTML}
            </div>
        `;
        container.appendChild(div);
    });
    
    // Przycisk do wysłania
    const submitBtn = document.createElement('button');
    submitBtn.textContent = 'Wyślij odpowiedzi';
    submitBtn.onclick = () => submitQuiz(attemptId);
    container.appendChild(submitBtn);
}
```

## 4. Wysłanie odpowiedzi i sprawdzenie wyniku

```javascript
async function submitQuiz(attemptId) {
    try {
        // Zbierz odpowiedzi z checkboxów
        const answers = [];
        const questionIds = new Set();
        
        document.querySelectorAll('input[type="checkbox"][data-question-id]').forEach(checkbox => {
            const questionId = parseInt(checkbox.getAttribute('data-question-id'));
            
            if (!questionIds.has(questionId)) {
                questionIds.add(questionId);
                const selectedIds = Array.from(
                    document.querySelectorAll(
                        `input[type="checkbox"][data-question-id="${questionId}"]:checked`
                    )
                ).map(el => parseInt(el.getAttribute('data-answer-id')));
                
                answers.push({
                    question_id: questionId,
                    selected_answer_ids: selectedIds
                });
            }
        });
        
        // Wyślij
        const result = await API.submitAttempt(attemptId, answers);
        
        // Pokaż wynik
        showResults(result);
    } catch (error) {
        showError('Błąd przy wysyłaniu odpowiedzi');
    }
}

function showResults(result) {
    const container = document.getElementById('quiz-container');
    container.innerHTML = `
        <div class="results">
            <h2>Twój wynik</h2>
            <p>Poprawne: ${result.total_correct}</p>
            <p>Błędne: ${result.total_incorrect}</p>
            <p class="score">
                ${Math.round((result.total_correct / (result.total_correct + result.total_incorrect)) * 100)}%
            </p>
            
            <div class="details">
                ${result.results.map((r, idx) => `
                    <div class="result-item ${r.correct ? 'correct' : 'incorrect'}">
                        <h4>Pytanie ${idx + 1}</h4>
                        <p>${r.correct ? '✓ Poprawnie' : '✗ Błędnie'}</p>
                        <p>Twoja odpowiedź: ${r.selected_answer_ids.join(', ') || 'Brak'}</p>
                        <p>Poprawna odpowiedź: ${r.correct_answer_ids.join(', ')}</p>
                    </div>
                `).join('')}
            </div>
            
            <button onclick="location.href='/quiz/my-quizzes/'">Powrót do moich quizów</button>
        </div>
    `;
}
```

## 5. Pobranie statystyk

```javascript
async function loadQuizStats(quizId) {
    try {
        const stats = await API.getQuizStats(quizId);
        
        console.log(`
            Quiz ID: ${quizId}
            Prób: ${stats.total_attempts}
            Średni wynik: ${(stats.average_score * 100).toFixed(1)}%
            Trudność: ${stats.difficulty}
        `);
        
        renderStats(stats);
    } catch (error) {
        console.error('Błąd ładowania statystyk:', error);
    }
}

function renderStats(stats) {
    const div = document.getElementById('stats');
    div.innerHTML = `
        <h3>Statystyki</h3>
        <p>Prób: ${stats.total_attempts}</p>
        <p>Średni wynik: ${(stats.average_score * 100).toFixed(1)}%</p>
        <p>Trudność: ${stats.difficulty}</p>
    `;
}
```

## 6. Usunięcie quizu

```javascript
async function deleteQuiz(quizId) {
    if (!confirm('Czy na pewno chcesz usunąć ten quiz?')) {
        return;
    }
    
    try {
        // Najpierw usuń wszystkie pytania
        const quiz = await API.getQuiz(quizId);
        for (let question of quiz.questions) {
            await API.deleteQuestion(question.id);
        }
        
        // Potem usuń quiz
        await API.deleteQuiz(quizId);
        
        showSuccess('Quiz usunięty pomyślnie');
        loadMyQuizzes(); // Odśwież listę
    } catch (error) {
        showError('Nie udało się usunąć quizu: ' + error.message);
    }
}
```

## 7. Udostępnienie quizu

```javascript
async function shareQuizWithUser(quizId, userId) {
    try {
        await API.shareQuiz(quizId, userId);
        showSuccess('Quiz udostępniony pomyślnie');
    } catch (error) {
        if (error.message.includes('already shared')) {
            showError('Ten quiz jest już udostępniony temu użytkownikowi');
        } else {
            showError('Błąd przy udostępnianiu: ' + error.message);
        }
    }
}
```

## 8. Helper Functions

```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const div = document.getElementById('error') || createNotification();
    div.className = 'notification error';
    div.textContent = message;
    div.style.display = 'block';
    setTimeout(() => div.style.display = 'none', 5000);
}

function showSuccess(message) {
    const div = document.getElementById('success') || createNotification();
    div.className = 'notification success';
    div.textContent = message;
    div.style.display = 'block';
    setTimeout(() => div.style.display = 'none', 5000);
}

function createNotification() {
    const div = document.createElement('div');
    div.id = 'notification';
    document.body.appendChild(div);
    return div;
}
```

## 9. CSS do notyfikacji

```css
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem;
    border-radius: 8px;
    z-index: 1000;
    min-width: 300px;
}

.notification.success {
    background-color: #10b981;
    color: white;
}

.notification.error {
    background-color: #ef4444;
    color: white;
}
```

## 10. Pełny przykład: my_quizzes.html

```html
{% load static %}
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Moje Quizy</title>
    <link rel="stylesheet" href="{% static 'quiz/style.css' %}">
</head>
<body>
    <div class="container">
        <h1>Moje Quizy</h1>
        <div id="quizzes-container"></div>
    </div>

    <script src="{% static 'quiz/js/api-client.js' %}"></script>
    <script>
        const API = new QuizAPI('/api/quiz', '{{ csrf_token }}');
        const USER_ID = {{ request.session.user_id }};

        async function loadMyQuizzes() {
            try {
                const response = await API.getQuizzes(USER_ID);
                const quizzes = response.quizzes;
                
                const container = document.getElementById('quizzes-container');
                container.innerHTML = '';
                
                if (quizzes.length === 0) {
                    container.innerHTML = '<p>Brak quizów. <a href="/quiz/my-notes/upload/">Stwórz nowy quiz</a></p>';
                    return;
                }
                
                quizzes.forEach(quiz => {
                    const div = document.createElement('div');
                    div.className = 'quiz-card';
                    div.innerHTML = `
                        <h3>${escapeHtml(quiz.content)}</h3>
                        <p>${quiz.questions?.length || 0} pytań</p>
                        <button onclick="startQuiz(${quiz.id})">Rozpocznij</button>
                        <button onclick="deleteQuiz(${quiz.id})">Usuń</button>
                    `;
                    container.appendChild(div);
                });
            } catch (error) {
                document.getElementById('quizzes-container').innerHTML = 
                    `<p>Błąd: ${error.message}</p>`;
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        document.addEventListener('DOMContentLoaded', loadMyQuizzes);
    </script>
</body>
</html>
```

## Kluczowe punkty

1. **Zawsze używaj `API_CLIENT`** dla operacji API
2. **Obsługuj błędy** - API może zwrócić 404, 400 itp
3. **Przechowaj ID attempt'u** w sessionStorage dla przyszłych operacji
4. **Waliduj dane** przed wysłaniem do API
5. **Pokaż feedback użytkownikowi** - loading, success, error messages
6. **Testuuj w DevTools** - sprawdzaj Network tab czy żądania są prawidłowe
