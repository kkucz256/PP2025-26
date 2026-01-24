# 🔧 Debugowanie - Pytania się nie wyświetlają

## Kroki debugowania

### 1. Otwórz Developer Tools
```
Mac: Cmd + Option + I
PC: F12
```

### 2. Przejdź do Console tab
```
DevTools → Console (lub F12 → Console)
```

### 3. Odśwież stronę (Cmd/Ctrl + R)
```
Będą logi starting z "🔍 DEBUG"
```

### 4. Wklej WSZYSTKIE logi z konsoli tutaj:
```
Potrzebuję aby zobaczyć:
- 🔍 DEBUG - initialQuestions z Django
- 📥 loadQuestionsFromSession() start
- ✓ Ładuję pytania z Django sesji
- 🎨 renderQuestions()
- 📋 createQuestionCard()
```

## Co sprawdzać

| Log | Oznacza |
|-----|---------|
| `✓ Ładuję pytania z Django sesji: 14` | Pytania załadowane ✅ |
| `🎨 renderQuestions() - container: ✓ znaleziony` | Container znaleziony ✅ |
| `🎨 Renderuję pytanie 1:` | Renderowanie started ✅ |
| `📋 createQuestionCard() - idx:0, id:temp_0` | Karta tworzona ✅ |
| `⚠️ Pytania puste lub undefined!` | PROBLEM - brak danych ❌ |
| `❌ Container #questions-container nie znaleziony!` | PROBLEM - brak kontenera ❌ |

## DevTools Network Check

Jeśli logs są OK ale pytania nie widać:

1. Otwórz DevTools → **Elements** (lub **Inspector**)
2. Szukaj `<div id="questions-container">`
3. Rozpakuj element (kliknij arrow)
4. Czy są wewnątrz `<div class="question-card">`?

Jeśli tak → **Problem CSS**  
Jeśli nie → **Problem JavaScript**

## Jeśli Problem CSS

Sprawdź czy `.question-card` ma:
```css
- display: block; (nie none!)
- visibility: visible;
- height: auto; (nie 0!)
```

## Jeśli Problem JavaScript

Wklej to w konsoli i powiedz co zwróci:
```javascript
console.log('questions array:', questions);
console.log('container:', document.getElementById('questions-container'));
console.log('initialQuestions:', window.initialQuestions);
```

## Debug Output Template

Gdy odświeżysz stronę, skopiuj i wklej wszystko z konsoli:

```
[WKLEJ WSZYSTKIE LOGI Z KONSOLI]
```

Wtedy będę mógł dokładnie wiedzieć co się dzieje! 🔍
