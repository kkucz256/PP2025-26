# Instrukcja uruchomienia

### 1. Budowanie obrazów
Przebuduj obrazy, jeśli zmieniły się pliki `Dockerfile` lub `requirements.txt`.

```bash
docker-compose build
```

### 2. Uruchomienie kontenerów
```bash
docker-compose up -d
```

### 3. Migracja bazy danych (przy pierwszym uruchomieniu)
Będąc wewnątrz kontenera (`quiz_django`), wykonaj migracje:

```bash
python manage.py migrate
```
### 4. Usunięcie kontenerów
```bash
docker-compose down
```
Aplikacja dostępna pod: `http://localhost:8000`
