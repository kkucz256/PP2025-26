# Przykład: Integracja my_quizzes.html

Poniżej pełny przykład jak zintegrować stronę "Moje Quizy" z API.

## Template HTML

```html
{% load static %}
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moje Quizy - Quiz Master</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'quiz/style.css' %}">
    <style>
        .quizzes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin: 2rem 0;
        }
        
        .quiz-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .quiz-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .quiz-card h3 {
            margin-top: 0;
            color: #2563eb;
        }
        
        .quiz-meta {
            font-size: 0.9rem;
            color: #666;
            margin: 1rem 0;
        }
        
        .quiz-actions {
            display: flex;
            gap: 8px;
            margin-top: 1rem;
        }
        
        .btn-small {
            flex: 1;
            padding: 0.5rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        .btn-primary {
            background-color: #2563eb;
            color: white;
        }
        
        .btn-primary:hover {
            background-color: #1d4ed8;
        }
        
        .btn-danger {
            background-color: #dc2626;
            color: white;
        }
        
        .btn-danger:hover {
            background-color: #b91c1c;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
        }
        
        .empty-state p {
            color: #666;
            margin-bottom: 1rem;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        }
        
        .notification.success {
            background-color: #10b981;
        }
        
        .notification.error {
            background-color: #dc2626;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Moje Quizy</h1>
            <a href="{% url 'quiz:upload_pdf_view' %}" class="btn btn-primary">+ Nowy Quiz</a>
        </header>

        <div id="loading" class="loading" style="display: none;">
            <p>Ładowanie quizów...</p>
        </div>

        <div id="quizzes-container" class="quizzes-grid"></div>

        <div id="notification"></div>
    </div>

    <script src="{% static 'quiz/js/api-client.js' %}"></script>
    <script>
        // Konfiguracja
        const API = new QuizAPI('/api/quiz', '{{ csrf_token }}');
        const USER_ID = {{ request.session.user_id|default:'null' }};

        // Ładowanie pytań przy załadowaniu strony
        document.addEventListener('DOMContentLoaded', loadMyQuizzes);

        /**
         * Załaduj wszystkie quizy użytkownika
         */
        async function loadMyQuizzes() {
            if (!USER_ID) {
                showNotification('Nie jesteś zalogowany', 'error');
                return;
            }

            try {
                showLoading(true);
                
                const response = await API.getQuizzes(USER_ID);
                const quizzes = response.quizzes || [];
                
                if (quizzes.length === 0) {
                    renderEmptyState();
                } else {
                    renderQuizzes(quizzes);
                }
            } catch (error) {
                console.error('Błąd ładowania quizów:', error);
                showNotification('Błąd: ' + error.message, 'error');
            } finally {
                showLoading(false);
            }
        }

        /**
         * Renderuj pustą stronę
         */
        function renderEmptyState() {
            const container = document.getElementById('quizzes-container');
            container.innerHTML = `
                <div style="grid-column: 1/-1;">
                    <div class="empty-state">
                        <h2>Brak quizów</h2>
                        <p>Nie masz jeszcze żadnych quizów. Stwórz nowy quiz aby zacząć!</p>
                        <a href="{% url 'quiz:upload_pdf_view' %}" class="btn btn-primary">
                            Stwórz Quiz z PDF
                        </a>
                    </div>
                </div>
            `;
        }

        /**
         * Renderuj listę quizów
         */
        function renderQuizzes(quizzes) {
            const container = document.getElementById('quizzes-container');
            container.innerHTML = '';

            quizzes.forEach(quiz => {
                const card = document.createElement('div');
                card.className = 'quiz-card';
                card.innerHTML = `
                    <h3>${escapeHtml(quiz.content)}</h3>
                    <div class="quiz-meta">
                        <p>📚 Pytań: <strong>${quiz.questions?.length || 0}</strong></p>
                        <p>🔗 ID: <code>${quiz.id}</code></p>
                        <p>📍 Slug: <code>${quiz.slug}</code></p>
                    </div>
                    <div class="quiz-actions">
                        <button class="btn-small btn-primary" onclick="startQuiz(${quiz.id})">
                            Rozpocznij
                        </button>
                        <button class="btn-small btn-danger" onclick="confirmDelete(${quiz.id}, '${escapeHtml(quiz.content)}')">
                            Usuń
                        </button>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        /**
         * Rozpocznij rozgrywkę quizu
         */
        async function startQuiz(quizId) {
            try {
                // Twórz attempt
                const attempt = await API.createAttempt({
                    quiz_id: quizId,
                    user_id: USER_ID
                });

                // Przechowaj attempt ID
                sessionStorage.setItem('currentAttemptId', attempt.id);
                sessionStorage.setItem('currentQuizId', quizId);

                // Przejdź do strony rozgrywki
                window.location.href = `/quiz/start-quiz/?attempt_id=${attempt.id}`;
            } catch (error) {
                console.error('Błąd tworzenia attempt\'u:', error);
                showNotification('Nie udało się rozpocząć quizu', 'error');
            }
        }

        /**
         * Potwierdź usunięcie i usuń quiz
         */
        async function confirmDelete(quizId, quizName) {
            if (!confirm(`Czy na pewno chcesz usunąć quiz "${quizName}"?\n\nTa operacja jest nieodwracalna!`)) {
                return;
            }

            try {
                // Najpierw usuń pytania
                const quiz = await API.getQuiz(quizId);
                
                let deleted = 0;
                for (let question of quiz.questions || []) {
                    try {
                        await API.deleteQuestion(question.id);
                        deleted++;
                    } catch (e) {
                        console.warn(`Nie udało się usunąć pytania ${question.id}:`, e);
                    }
                }

                console.log(`Usunięto ${deleted} pytań`);

                // Usuń quiz
                await API.deleteQuiz(quizId);

                showNotification(`Quiz "${quizName}" został usunięty`, 'success');
                loadMyQuizzes(); // Odśwież listę
            } catch (error) {
                console.error('Błąd usuwania:', error);
                showNotification('Błąd: ' + error.message, 'error');
            }
        }

        /**
         * Pokaż/ukryj loading
         */
        function showLoading(show) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }

        /**
         * Pokaż notyfikację
         */
        function showNotification(message, type = 'success') {
            const container = document.getElementById('notification');
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            
            // Wyczyść stare notyfikacje
            container.innerHTML = '';
            container.appendChild(notification);

            // Auto-ukryj po 5 sekundach
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }

        /**
         * Escape HTML do bezpieczeństwa
         */
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
```

## View (views.py)

```python
def my_quizzes_view(request):
    # Sprawdzenie zalogowania
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    
    # Template już obsługuje pobieranie z API
    return render(request, 'quiz/my_quizzes.html')
```

## Opis działania

1. **Załadowanie strony** - JavaScript automatycznie pobiera quizy użytkownika
2. **Wyświetlenie** - Quizy wyświetlają się w siatce (grid)
3. **Interakcja**:
   - Kliknięcie "Rozpocznij" → tworzy attempt → redirect do `/quiz/start-quiz/`
   - Kliknięcie "Usuń" → potwierdza → usuwa pytania → usuwa quiz → odświeża listę

## Zmienne przechowywane

- `currentAttemptId` - ID attempt'u (do obliczania wyniku)
- `currentQuizId` - ID quizu (do wyświetlania)

## Kluczowe różnice od starego kodu

| Stary | Nowy |
|------|------|
| Przesyłanie pytań do template'u | Pobieranie z API |
| Dynamiczne renderowanie HTML | Renderowanie JavaScript |
| Brak error handling'u | Error handling z notyfikacjami |
| Brak walidacji | Walidacja danych |
| POST form | Fetch API |

## Integracja z innymi stronami

Ten sam schemat możesz zastosować do:
- `start_quiz` - lista quizów do rozgrania
- `statistics` - wyświetlanie statystyk
- `multiplayer` - lista sesji do dołączenia

Wystarczy zmienić endpoint API i strukturę danych 👍
