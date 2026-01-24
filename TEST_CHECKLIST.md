# Test Checklist - Review Questions API Integration

## Pre-Test Setup
- [ ] Django server running
- [ ] Database migrated
- [ ] User logged in
- [ ] PDF uploaded and questions generated

## Test 1: Load Page
- [ ] Navigate to `/quiz/review-questions/`
- [ ] Questions should display in the container
- [ ] Quiz name field is visible and empty
- [ ] "Add question" and "Save Quiz" buttons are visible

## Test 2: Display Questions
- [ ] Generated questions appear with correct text
- [ ] Answer options are displayed
- [ ] Correct answer is marked with radio button
- [ ] Questions are numbered correctly (1, 2, 3...)

## Test 3: Edit Questions
- [ ] Click on question text → can edit
- [ ] Click on answer option → can edit
- [ ] Select different radio button → marking changes
- [ ] Changes are reflected immediately

## Test 4: Add Manual Question
- [ ] Click "Add new question" button
- [ ] New question card appears at bottom
- [ ] Empty question text, 4 empty answer fields
- [ ] Can fill in question text
- [ ] Can fill in answer options
- [ ] Can select correct answer radio button

## Test 5: Delete Question
- [ ] Click delete button on question
- [ ] Confirmation dialog appears
- [ ] Click cancel → question remains
- [ ] Click OK → question is deleted
- [ ] Remaining questions are renumbered

## Test 6: Validation
- [ ] Try to save WITHOUT quiz name → error message
- [ ] Try to save WITH name BUT no questions → error message
- [ ] Try to save with empty question text → error message
- [ ] Try to save with empty answer option → error message

## Test 7: Save Quiz
- [ ] Fill in quiz name
- [ ] Fill in all questions properly
- [ ] Click "Save Quiz"
- [ ] Loading indicator appears
- [ ] Request sent to `/api/quiz/quizzes/` (check Network tab)
- [ ] Success message appears
- [ ] Auto-redirect to `/quiz/my-quizzes/` after 1.5s

## Test 8: API Response
- [ ] Check browser Network tab
- [ ] POST request should have correct JSON structure
- [ ] Response status should be 201 (Created)
- [ ] Response should contain quiz ID

## Test 9: Database Check
- [ ] Quiz created in database
- [ ] Questions associated with quiz
- [ ] Answers associated with questions
- [ ] is_correct field set properly

## Test 10: Cancel Navigation
- [ ] Go to `/quiz/review-questions/`
- [ ] Click "Anuluj" (Cancel) button
- [ ] Should redirect to `/quiz/my-notes/upload/`

## Test 11: Error Handling
- [ ] Disable network (DevTools)
- [ ] Try to save quiz
- [ ] Error message should appear
- [ ] No redirect should happen

## Test 12: Browser Support
- [ ] Test in Chrome/Edge
- [ ] Test in Firefox
- [ ] Test on mobile (responsive design)
- [ ] Test on tablet

## Expected API Request Example
```json
POST /api/quiz/quizzes/
{
  "content": "Biology Quiz",
  "slug": "biology-quiz",
  "owner_id": 1,
  "questions": [
    {
      "content": "What is the powerhouse of the cell?",
      "position": 1,
      "answers": [
        {
          "content": "Mitochondria",
          "is_correct": true
        },
        {
          "content": "Nucleus",
          "is_correct": false
        },
        {
          "content": "Ribosome",
          "is_correct": false
        },
        {
          "content": "Chloroplast",
          "is_correct": false
        }
      ]
    }
  ]
}
```

## Expected Success Response
```json
{
  "id": 123,
  "content": "Biology Quiz",
  "slug": "biology-quiz",
  "questions": [
    {
      "id": 456,
      "quiz_id": 123,
      "content": "What is the powerhouse of the cell?",
      "position": 1,
      "answers": [...]
    }
  ]
}
```
