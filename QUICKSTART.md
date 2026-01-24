# 🚀 Szybki Start - API Integration

Kompletna integracja API dla review_questions została wdrożona!

## ✅ Co zostało zrobione

### 1. **review_questions.html** (Template)
- ✓ Zmieniony z formularz POST na dinamiczny system
- ✓ Pytania renderowane przez JavaScript
- ✓ Notyfikacje o błędach i sukcesach
- ✓ CSRF token i ID użytkownika w zmiennych globalnych

### 2. **review_questions.js** (Logika)
- ✓ Ładowanie pytań z sesji (wygenerowanych z PDF)
- ✓ Renderowanie pytań na HTML
- ✓ Edycja tekstu pytań i odpowiedzi
- ✓ Dodawanie nowych pytań ręcznie
- ✓ Usuwanie pytań
- ✓ Walidacja danych
- ✓ Wysyłanie do API via POST `/api/quiz/quizzes/`
- ✓ Obsługa błędów i komunikaty

### 3. **review_questions.css** (Style)
- ✓ Loading indicator (animacja pulsująca)
- ✓ Success notification (zielony banner)
- ✓ Error notification (czerwony banner)
- ✓ Responsive design

### 4. **views.py** (Backend)
- ✓ Przesyłanie pytań jako JSON do template'u
- ✓ Gotowy endpoint do POST (już istnieje)

### 5. **api-client.js** (Helper)
- ✓ Klasa QuizAPI z wszystkimi metodami
- ✓ Obsługa CSRF tokenów
- ✓ Error handling

### 6. **Dokumentacja**
- ✓ API_INTEGRATION.md - Szczegóły zmian
- ✓ API_DOCS.md - Referencja wszystkich endpointów
- ✓ INTEGRATION_GUIDE.md - Poradnik dla innych stron
- ✓ TEST_CHECKLIST.md - Lista testów do wykonania

## 🔄 Przepływ danych

```
1. Użytkownik przywet PDF
           ↓
2. AI generuje pytania
           ↓
3. Pytania w Django session
           ↓
4. Template renderuje je jako JSON
           ↓
5. JavaScript wyświetla w DOM
           ↓
6. Użytkownik edytuje pytania
           ↓
7. Kliknięcie "Zapisz Quiz"
           ↓
8. Walidacja + POST do /api/quiz/quizzes/
           ↓
9. Sukces → redirect do /quiz/my-quizzes/
```

## 🧪 Jak testować

### Test 1: Podstawowy
```bash
1. Zaloguj się
2. Przejdź do /quiz/my-notes/upload/
3. Wgraj plik PDF
4. Wygeneruj pytania
5. Powinieneś trafić na /quiz/review-questions/
6. Pytania powinny się wyświetlić
```

### Test 2: Edycja
```bash
1. Zmień tekst pytania
2. Zmień odpowiedź
3. Kliknij radio button innej odpowiedzi
4. Wszystko powinno działać bez refresh'a
```

### Test 3: Dodanie pytania
```bash
1. Kliknij "+ Dodaj nowe pytanie ręcznie"
2. Powinno pojawić się nowe pytanie
3. Wpisz tekst i odpowiedzi
4. Kliknij save
```

### Test 4: Usunięcie pytania
```bash
1. Kliknij "Usuń" na dowolnym pytaniu
2. Potwierdź w dialog'u
3. Pytanie powinno zniknąć
4. Pozostałe powinny się przenumerować
```

### Test 5: Zapis
```bash
1. Wypełnij nazwę quizu
2. Wszystkie pytania powinny być wypełnione
3. Kliknij "Zapisz Quiz"
4. Pokaże się "Zapisuję quiz..."
5. Po sukcesie pojawi się zielony banner
6. Powinieneś być redirectowany do /quiz/my-quizzes/
```

### Test 6: Błędy
```bash
1. Spróbuj zapisać bez nazwy
2. Powinien być komunikat o błędzie
3. Spróbuj zapisać z pustym pytaniem
4. Powinien być komunikat o błędzie
```

## 📱 Sprawdzenie w DevTools

Otwórz DevTools (F12) i przejdź do Network:

```
1. Kliknij "Zapisz Quiz"
2. Powinno być żądanie POST do /api/quiz/quizzes/
3. Status powinien być 201 Created
4. Response powinien zawierać ID quizu
```

Payload powinien wyglądać tak:
```json
{
  "content": "Nazwa Quizu",
  "slug": "nazwa-quizu",
  "owner_id": 1,
  "questions": [
    {
      "content": "Pytanie 1?",
      "position": 1,
      "answers": [
        {
          "content": "Odpowiedź A",
          "is_correct": true
        }
      ]
    }
  ]
}
```

## 🐛 Troubleshooting

### Problem: Pytania się nie wyświetlają
**Rozwiązanie:**
1. Sprawdź browser console (F12 → Console)
2. Czy są błędy JavaScript?
3. Czy pytania są w sesji?
4. Czy test na `/quiz/review-questions/` z pytaniami w session?

### Problem: Zapisanie nie działa
**Rozwiązanie:**
1. Sprawdź Network tab - czy żądanie idzie do API?
2. Jaki jest status? 400? 404? 500?
3. Co mówi error message?
4. Czy wszystkie pola są wypełnione?

### Problem: CSRF error
**Rozwiązanie:**
1. Sprawdź czy CSRF token jest w template'u
2. Czy `X-CSRFToken` header jest wysyłany?
3. Odśwież stronę

### Problem: Redirect nie działa
**Rozwiązanie:**
1. Po zapisaniu czekaj 1.5s
2. Sprawdzaj Network tab czy idzie do `/quiz/my-quizzes/`
3. Czy URL istnieje?

## 💡 Użyteczne komendy

### Debug pytań w konsoli
```javascript
console.log(questions); // Pokaż wszystkie pytania w pamięci
console.log(JSON.stringify(questions, null, 2)); // Pretty print
```

### Test API ręcznie (curl)
```bash
curl -X POST http://localhost:8000/api/quiz/quizzes/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_TOKEN" \
  -d '{
    "content": "Test Quiz",
    "slug": "test-quiz",
    "owner_id": 1,
    "questions": []
  }'
```

## 📚 Nazewnictwo ID pytań

- `temp_<index>` - Pytania wygenerowane z PDF (tymczasowe)
- `new_<timestamp>` - Pytania dodane ręcznie (tymczasowe)
- `<number>` - Po zapisaniu w API (rzeczywiste ID z bazy)

## 🔒 Bezpieczeństwo

- ✓ CSRF token wymagany
- ✓ User ID sprawdzany
- ✓ SQL injection protection (Django ORM)
- ✓ XSS protection (escapeHtml funkcja)

## 📝 Kolejne kroki

1. **Integruj inne strony** - Use INTEGRATION_GUIDE.md
2. **Przetestuj całkowicie** - Use TEST_CHECKLIST.md
3. **Dodaj walidację** - Backend validations
4. **Dodaj animations** - CSS transitions
5. **Mobile optimization** - Responsive design

## 🎯 Docelowe endpoints

Po integracji będziesz mieć:

- ✓ `/quiz/review-questions/` - Edycja pytań (API)
- ✓ `/api/quiz/quizzes/` - Tworzenie quizu (API)
- [ ] `/quiz/my-quizzes/` - Lista moich quizów (TODO)
- [ ] `/quiz/start-quiz/` - Rozgrywka quizu (TODO)
- [ ] `/quiz/statistics/` - Statystyki (TODO)

## 🆘 Potrzebujesz pomocy?

1. Sprawdź dokumentację:
   - API_DOCS.md - Referencja API
   - INTEGRATION_GUIDE.md - Poradnik integracji
   - API_INTEGRATION.md - Szczegóły zmian

2. Sprawdź DevTools:
   - Console - błędy JavaScript
   - Network - żądania API
   - Sources - debug kodu

3. Przeanalizuj logs:
   - Django console - błędy serwera
   - Browser Network - response z API

## ✨ Bonus: Szybkie API żądania

W browser console:
```javascript
// Załaduj API client
const api = new QuizAPI('/api/quiz', 'YOUR_CSRF_TOKEN');

// Pobierz quizy
api.getQuizzes(1).then(r => console.log(r));

// Pobierz quiz
api.getQuiz(1).then(r => console.log(r));

// Pobierz statystyki
api.getQuizStats(1).then(r => console.log(r));
```

---

**Status: ✅ Gotowe do testowania!**

Wszystkie pliki są w miejscu. Wystarczy teraz przetestować i możesz integrować inne strony.

Powodzenia! 🎉
