# Integracja API - Review Questions

## Przegląd zmian

Zaktualizowałem stronę edycji pytań (`review_questions.html`) aby używać REST API zamiast tradycyjnego formularza POST.

## Główne zmiany

### 1. **Template HTML** (`review_questions.html`)
- Usunąłem tradycyjny formularz POST
- Dodałem dynamiczny kontener na pytania (`#questions-container`)
- Pytania są teraz renderowane przez JavaScript
- Dodałem elementy do wyświetlania komunikatów o błędach i sukcesie
- Przesyłam CSRF token i dane użytkownika do JS

### 2. **JavaScript** (`review_questions.js`)
Pełna reintegracja z poniższymi funkcjami:

#### Ładowanie pytań
```javascript
loadQuestionsFromSession()  // Ładuje pytania z sesji (wygenerowane z PDF)
loadQuestionsFromWindow()   // Fallback - ładuje ze sessionStorage
```

#### Manipulacja pytaniami
```javascript
addNewQuestion(event)       // Dodaj nowe pytanie ręcznie
removeQuestion(event)       // Usuń pytanie
updateQuestionText(event)   // Zmień tekst pytania
updateOptionText(event)     // Zmień tekst odpowiedzi
renderQuestions()           // Renderuj wszystkie pytania na HTML
reindexQuestions()          // Przenumeruj pytania
```

#### Zapis do API
```javascript
saveQuiz(event)             // Walidacja i wysłanie do API
```

### 3. **CSS** (`review_questions.css`)
Dodałem nowe style dla:
- Loading indicator (animacja pulsująca)
- Success message (zielony banner w rogu)
- Error message (czerwony banner w rogu)
- Responsywny design dla mobilnych

### 4. **Backend** (`views.py`)
- Zaktualizowałem `review_questions_view()` aby przesyłać pytania jako JSON
- Pytania są dostarczone zarówno w kontekście Django jak i jako JSON do JavaScript

### 5. **JavaScript Upload** (`upload_pdf.js`)
- Dodałem funkcję `storeQuestionsInSession()` do przechowywania pytań
- Przygotowałem obsługę przesłania pytań do sessionStorage

## Przepływ danych

```
1. PDF → Generowanie pytań (backend)
   ↓
2. Pytania w sesji Django
   ↓
3. Template receives questions as JSON
   ↓
4. JavaScript renderuje pytania w DOM
   ↓
5. Użytkownik edytuje pytania
   ↓
6. Kliknięcie "Zapisz Quiz"
   ↓
7. Walidacja (JavaScript)
   ↓
8. POST do /api/quiz/quizzes/ (API)
   ↓
9. Sukces → Redirect do /quiz/my-quizzes/
```

## Struktura API

Endpoint do tworzenia quizu z pytaniami i odpowiedziami:

```
POST /api/quiz/quizzes/
Content-Type: application/json

{
  "content": "Nazwa Quizu",
  "slug": "nazwa-quizu",
  "owner_id": 123,
  "questions": [
    {
      "content": "Tekst pytania",
      "position": 1,
      "answers": [
        {
          "content": "Odpowiedź A",
          "is_correct": true
        },
        {
          "content": "Odpowiedź B",
          "is_correct": false
        }
      ]
    }
  ]
}
```

## Walidacja

### Frontend (JavaScript)
- ✓ Quiz musi mieć nazwę
- ✓ Musi być co najmniej jedno pytanie
- ✓ Każde pytanie musi mieć tekst
- ✓ Każda opcja odpowiedzi musi być wypełniona
- ✓ Musi być wybrana poprawna odpowiedź dla każdego pytania

### Backend (Django Ninja)
- ✓ Quiz slug musi być unikalny
- ✓ Owner (user) musi istnieć
- ✓ Transakcja atomowa - jeśli coś się nie uda, wszystko się cofa

## Komunikaty użytkownika

### Błędy
- "Proszę podać nazwę quizu"
- "Brak pytań do zapisania"
- "Wszystkie pytania muszą mieć treść"
- "Wszystkie opcje odpowiedzi muszą być wypełnione"
- Dowolny błąd z API

### Sukces
- "Quiz "{nazwa}" został pomyślnie zapisany!"
- Automatyczne przekierowanie do "Moje Quizy" po 1.5s

## Variabele globalne

W JavaScript zdefiniowanie:
```javascript
API_BASE_URL    // '/api/quiz'
CSRF_TOKEN      // Token bezpieczeństwa Django
USER_ID         // ID zalogowanego użytkownika
questions       // Tablica przechowująca pytania w pamięci
```

## Wsparcie dla fallback'u

Jeśli API jest niedostępne, aplikacja:
1. Próbuje załadować pytania z `window.initialQuestions`
2. Następnie próbuje `sessionStorage.temp_questions`
3. Pozwala użytkownikowi dodawać pytania ręcznie

## Testy

Aby przetestować:

1. Zaladuj stronę `/quiz/my-notes/upload/`
2. Wgraj PDF i wygeneruj pytania
3. Zostaniesz przekierowany na `/quiz/review-questions/`
4. Pytania powinny się wyświetlić z edycją
5. Kliknij "Zapisz Quiz"
6. Quiz powinien być dostępny w API oraz w "Moje Quizy"

## Notatki techniczne

- Pytania przechowywane są w zmiennej `questions` (nie w DOM)
- Za każdym razem gdy zmienisz pytanie, aktualizuje się tablica w pamięci
- HTML jest generowany dynamicznie z funkcji `createQuestionCard()`
- Event listener'y są dodawane dla każdego pytania indywidualnie
- Wszystkie operacje API używają `fetch()` z CSRF tokenem
