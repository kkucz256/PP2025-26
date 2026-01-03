# Instrukcja uruchomienia

### 1. Budowanie obrazów
Przebuduj obrazy, jeśli zmieniły się pliki `Dockerfile` lub `requirements.txt`.

```bash
docker-compose build
```

### 2. Uruchomienie kontenerów
```bash
# start containers in background (rebuild if needed)
docker-compose up -d --build
```

PowerShell helper script (Windows)
```
# start detached (build if necessary):
.\scripts\start-containers.ps1
# start and open a separate window to follow logs:
.\scripts\start-containers.ps1 -FollowLogs
```

### 3. Migracja bazy danych (przy pierwszym uruchomieniu)
Będąc wewnątrz kontenera (`quiz_django`), wykonaj migracje:

```bash
python manage.py migrate
```

### 4.1 Pullowanie modelu (deepseek 7B - około 5GB)
```bash
docker-compose exec ollama ollama pull deepseek-r1:7b
```

### 4.2 Testowanie modelu (wiadomo w prompt tam wpisać swojego prompta)
```bash
curl -v http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:7b",
  "prompt": "Napisz po polsku jakieś 3 testowe pytania do quizu",
  "stream": false
}'
```

### 5. Usunięcie kontenerów
```bash
docker-compose down
```
Aplikacja dostępna pod: `http://localhost:8000`
