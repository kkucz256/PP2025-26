# API Reference - Quiz System

## Base URL
```
/api/quiz
```

## Authentication
- CSRF Token required for POST, PUT, DELETE requests
- Token sent via `X-CSRFToken` header

## Endpoints

### Quizzes

#### List Quizzes
```
GET /api/quiz/quizzes/
GET /api/quiz/quizzes/?user_id=1
```

Response:
```json
{
  "quizzes": [
    {
      "id": 1,
      "content": "Biology Quiz",
      "slug": "biology-quiz",
      "questions": [
        {
          "id": 1,
          "quiz_id": 1,
          "content": "What is photosynthesis?",
          "position": 1,
          "answers": [
            {
              "id": 1,
              "content": "Process of converting light to energy",
              "is_correct": true
            }
          ]
        }
      ]
    }
  ]
}
```

#### Get Single Quiz
```
GET /api/quiz/quizzes/{quiz_id}/
```

#### Create Quiz
```
POST /api/quiz/quizzes/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "content": "Quiz Name",
  "slug": "quiz-name",
  "owner_id": 1,
  "questions": [
    {
      "content": "Question text?",
      "position": 1,
      "answers": [
        {
          "content": "Correct answer",
          "is_correct": true
        },
        {
          "content": "Wrong answer",
          "is_correct": false
        }
      ]
    }
  ]
}
```

Response: 201 Created + Quiz object

#### Delete Quiz
```
DELETE /api/quiz/quizzes/{quiz_id}/
```

Condition: Quiz must have no questions

### Questions

#### List Questions
```
GET /api/quiz/questions/
GET /api/quiz/questions/?quiz_id=1
```

Response:
```json
[
  {
    "id": 1,
    "quiz_id": 1,
    "content": "Question text?",
    "position": 1,
    "answers": [...]
  }
]
```

#### Get Single Question
```
GET /api/quiz/questions/{question_id}/
```

#### Create Question
```
POST /api/quiz/questions/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "quiz_id": 1,
  "content": "New question?",
  "position": 1,
  "answers": [
    {
      "content": "Answer",
      "is_correct": false
    }
  ]
}
```

Response: 201 Created + Question object

#### Delete Question
```
DELETE /api/quiz/questions/{question_id}/
```

#### Add Answer to Question
```
POST /api/quiz/questions/{question_id}/answers/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "content": "Answer text",
  "is_correct": true
}
```

Response: 201 Created + Answer object

### Sessions

#### List Sessions
```
GET /api/quiz/sessions/
GET /api/quiz/sessions/?quiz_id=1&host_id=1&active=true
```

#### Create Session
```
POST /api/quiz/sessions/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "quiz_id": 1,
  "host_id": 1,
  "access_code": "AC123456",
  "start_time": "2024-01-24T10:00:00Z",
  "end_time": "2024-01-24T11:00:00Z",
  "is_active": true
}
```

Response: 201 Created + Session object

### Attempts

#### List Attempts
```
GET /api/quiz/attempts/
GET /api/quiz/attempts/?quiz_id=1&user_id=1
```

Response:
```json
[
  {
    "id": 1,
    "quiz_id": 1,
    "user_id": 1,
    "start_date": "2024-01-24T10:00:00Z",
    "end_date": "2024-01-24T10:15:00Z",
    "correct": 8,
    "incorrect": 2
  }
]
```

#### Create Attempt
```
POST /api/quiz/attempts/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "quiz_id": 1,
  "user_id": 1
}
```

Response: 201 Created + Attempt object with `correct: 0, incorrect: 0`

#### Submit Attempt
```
POST /api/quiz/attempts/{attempt_id}/submit/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "answers": [
    {
      "question_id": 1,
      "selected_answer_ids": [1, 2]
    },
    {
      "question_id": 2,
      "selected_answer_ids": [3]
    }
  ]
}
```

Response:
```json
{
  "results": [
    {
      "question_id": 1,
      "correct": true,
      "correct_answer_ids": [1, 2],
      "selected_answer_ids": [1, 2]
    }
  ],
  "total_correct": 8,
  "total_incorrect": 2
}
```

### Statistics

#### Quiz Statistics
```
GET /api/quiz/quizzes/{quiz_id}/stats/
```

Response:
```json
{
  "quiz_id": 1,
  "total_attempts": 10,
  "average_score": 0.75,
  "difficulty": "medium",
  "questions_stats": [...]
}
```

#### Question Statistics
```
GET /api/quiz/questions/{question_id}/stats/
```

Response:
```json
{
  "question_id": 1,
  "total_attempts": 10,
  "correct_count": 8,
  "difficulty": 0.8
}
```

### Sharing

#### Share Quiz
```
POST /api/quiz/quizzes/{quiz_id}/share/
Content-Type: application/json
X-CSRFToken: {csrf_token}

{
  "user_id": 2
}
```

Response: 201 Created
```json
{
  "quiz_id": 1,
  "user_id": 2,
  "detail": "shared"
}
```

## Status Codes

- **200 OK** - Successful GET/HEAD request
- **201 Created** - Successful POST request
- **204 No Content** - Successful DELETE request
- **400 Bad Request** - Invalid input, validation failed
- **404 Not Found** - Resource not found
- **500 Server Error** - Server error

## Error Responses

```json
{
  "detail": "Human readable error message"
}
```

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Quiz with this slug already exists" | Slug not unique | Use different slug |
| "Quiz not found" | Invalid quiz ID | Check quiz_id |
| "Cannot delete quiz with existing questions" | Quiz has questions | Delete questions first |
| "Owner user not found" | User doesn't exist | Use valid user_id |
| "Quiz already shared with this user" | Already shared | Don't share twice |

## Using API Client

Include the API client in your HTML:
```html
<script src="{% static 'quiz/js/api-client.js' %}"></script>
```

Usage:
```javascript
const api = new QuizAPI('/api/quiz', csrf_token);

// Create quiz
const quiz = await api.createQuiz({
    content: "My Quiz",
    slug: "my-quiz",
    owner_id: 1,
    questions: [...]
});

// Get quiz
const quiz = await api.getQuiz(1);

// Get quizzes for user
const response = await api.getQuizzes(1);
const quizzes = response.quizzes;

// Submit attempt
const result = await api.submitAttempt(attemptId, answers);
console.log(`Correct: ${result.total_correct}, Incorrect: ${result.total_incorrect}`);
```

## Rate Limiting
Currently no rate limiting. May be added in future.

## API Documentation (Interactive)
Visit `/api/quiz/docs` for interactive Swagger UI
