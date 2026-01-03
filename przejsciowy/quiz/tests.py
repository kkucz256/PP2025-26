import json
from django.test import TestCase, Client
from .models import Quiz, Question, Answers, Users, QuizAttempt


class QuizAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.quiz = Quiz.objects.create(content='Quiz 1', slug='quiz-1')

    def test_create_question_with_answers(self):
        payload = {
            "quiz_id": self.quiz.id,
            "content": "Pytanie 1",
            "position": 1,
            "answers": [
                {"content": "A", "is_correct": True},
                {"content": "B", "is_correct": False},
            ],
        }
        resp = self.client.post('/api/quiz/questions/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['content'], 'Pytanie 1')
        self.assertEqual(len(data['answers']), 2)

    def test_create_answer_endpoint(self):
        q = Question.objects.create(quiz=self.quiz, content='Q', position=1)
        payload = {"content": "C", "is_correct": False}
        resp = self.client.post(f'/api/quiz/questions/{q.id}/answers/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['content'], 'C')

    def test_list_quizzes_and_quiz_detail(self):
        # list quizzes
        resp = self.client.get('/api/quiz/quizzes/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('quizzes', data)
        self.assertTrue(len(data['quizzes']) >= 1)
        self.assertIsNotNone(data['quizzes'][0].get('questions'))

        quiz_id = data['quizzes'][0]['id']
        # get quiz detail including questions
        resp = self.client.get(f'/api/quiz/quizzes/{quiz_id}/')
        self.assertEqual(resp.status_code, 200)
        detail = resp.json()
        self.assertEqual(detail['id'], quiz_id)

    def test_create_quiz(self):
        payload = {
            "content": "New Quiz",
            "slug": "new-quiz",
            "questions": [
                {
                    "content": "Q1",
                    "position": 1,
                    "answers": [
                        {"content": "A1", "is_correct": True},
                        {"content": "A2", "is_correct": False}
                    ]
                },
                {
                    "content": "Q2",
                    "position": 2,
                    "answers": [
                        {"content": "B1", "is_correct": False}
                    ]
                }
            ]
        }
        resp = self.client.post('/api/quiz/quizzes/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['slug'], 'new-quiz')
        self.assertEqual(len(data['questions']), 2)

    def test_delete_question(self):
        q = Question.objects.create(quiz=self.quiz, content='To be deleted', position=1)
        resp = self.client.delete(f'/api/quiz/questions/{q.id}/')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Question.objects.filter(pk=q.id).exists())

    def test_delete_quiz_blocked_if_has_questions(self):
        quiz = Quiz.objects.create(content='Has Q', slug='has-q')
        Question.objects.create(quiz=quiz, content='Q1')
        resp = self.client.delete(f'/api/quiz/quizzes/{quiz.id}/')
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(Quiz.objects.filter(pk=quiz.id).exists())

    def test_delete_quiz_when_empty(self):
        quiz = Quiz.objects.create(content='Empty', slug='empty-quiz')
        resp = self.client.delete(f'/api/quiz/quizzes/{quiz.id}/')
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Quiz.objects.filter(pk=quiz.id).exists())

    def test_filter_quizzes_by_user(self):
        user = Users.objects.create(username='u1', password='p', role='user', mail='u1@example.com')
        quiz = Quiz.objects.create(content='Q for user', slug='q-user')
        # link user to quiz
        from .models import QuizUser
        QuizUser.objects.create(quiz=quiz, user=user)

        resp = self.client.get(f'/api/quiz/quizzes/?user_id={user.id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(any(q['id'] == quiz.id for q in data['quizzes']))

    def test_create_quiz_with_owner(self):
        owner = Users.objects.create(username='owner', password='x', role='user', mail='owner@example.com')
        payload = {"content": "Owned Quiz", "slug": "owned-quiz", "owner_id": owner.id}
        resp = self.client.post('/api/quiz/quizzes/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['slug'], 'owned-quiz')
        # ensure relation exists
        from .models import QuizUser
        quiz_id = data['id']
        self.assertTrue(QuizUser.objects.filter(quiz_id=quiz_id, user_id=owner.id).exists())

    def test_share_quiz_endpoint(self):
        user = Users.objects.create(username='target', password='p', role='user', mail='t@example.com')
        quiz = Quiz.objects.create(content='Shareable', slug='share-me')
        payload = {"user_id": user.id}
        resp = self.client.post(f'/api/quiz/quizzes/{quiz.id}/share/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['user_id'], user.id)
        # duplicate share is rejected
        resp2 = self.client.post(f'/api/quiz/quizzes/{quiz.id}/share/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp2.status_code, 400)

    def test_session_and_attempt_flow(self):
        user = Users.objects.create(username='host', password='x', role='host', mail='host@example.com')
        quiz = Quiz.objects.create(content='Session Quiz', slug='session-quiz')
        # create session
        payload = {"quiz_id": quiz.id, "host_id": user.id}
        resp = self.client.post('/api/quiz/sessions/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        sess = resp.json()
        self.assertEqual(sess['quiz_id'], quiz.id)

        # create a question and answers
        q = Question.objects.create(quiz=quiz, content='Qsubmit')
        a1 = Answers.objects.create(question=q, content='A1', is_correct=True)
        a2 = Answers.objects.create(question=q, content='A2', is_correct=False)

        # create attempt
        payload = {"quiz_id": quiz.id, "user_id": user.id}
        resp = self.client.post('/api/quiz/attempts/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        attempt = resp.json()
        attempt_id = attempt['id']

        # submit - correct
        submit_payload = {"answers": [{"question_id": q.id, "selected_answer_ids": [a1.id]}]}
        resp = self.client.post(f'/api/quiz/attempts/{attempt_id}/submit/', data=json.dumps(submit_payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_correct'], 1)
        # reload attempt
        att = QuizAttempt.objects.get(pk=attempt_id)
        self.assertEqual(att.correct, 1)
        self.assertEqual(att.incorrect, 0)

        # submit - incorrect
        submit_payload = {"answers": [{"question_id": q.id, "selected_answer_ids": [a2.id]}]}
        resp = self.client.post(f'/api/quiz/attempts/{attempt_id}/submit/', data=json.dumps(submit_payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_incorrect'], 1)
        att.refresh_from_db()
        self.assertEqual(att.incorrect, 1)

    def test_stats_update_and_endpoints(self):
        user = Users.objects.create(username='stats_user', password='p', role='user', mail='s@example.com')
        quiz = Quiz.objects.create(content='Stats Quiz', slug='stats-quiz')
        q = Question.objects.create(quiz=quiz, content='StatQ', position=1)
        a1 = Answers.objects.create(question=q, content='A1', is_correct=True)
        a2 = Answers.objects.create(question=q, content='A2', is_correct=False)

        # create attempt
        payload = {"quiz_id": quiz.id, "user_id": user.id}
        resp = self.client.post('/api/quiz/attempts/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        attempt = resp.json()
        attempt_id = attempt['id']

        # submit correct
        submit_payload = {"answers": [{"question_id": q.id, "selected_answer_ids": [a1.id]}]}
        resp = self.client.post(f'/api/quiz/attempts/{attempt_id}/submit/', data=json.dumps(submit_payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        # check stats models
        from .models import QuizStat, QuestionStat, AnswerStat
        qs = QuizStat.objects.get(quiz=quiz)
        self.assertEqual(qs.total_attempts, 1)
        self.assertEqual(qs.total_correct, 1)
        self.assertEqual(qs.total_incorrect, 0)
        qqs = QuestionStat.objects.get(question=q)
        self.assertEqual(qqs.times_asked, 1)
        self.assertEqual(qqs.times_correct, 1)
        a1s = AnswerStat.objects.get(answer=a1)
        self.assertEqual(a1s.times_selected, 1)
        self.assertEqual(a1s.times_selected_correct, 1)

        # submit incorrect
        submit_payload = {"answers": [{"question_id": q.id, "selected_answer_ids": [a2.id]}]}
        resp = self.client.post(f'/api/quiz/attempts/{attempt_id}/submit/', data=json.dumps(submit_payload), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        qs.refresh_from_db()
        self.assertEqual(qs.total_attempts, 2)
        self.assertEqual(qs.total_correct, 1)
        self.assertEqual(qs.total_incorrect, 1)
        qqs.refresh_from_db()
        self.assertEqual(qqs.times_asked, 2)
        self.assertEqual(qqs.times_correct, 1)
        a2s = AnswerStat.objects.get(answer=a2)
        self.assertEqual(a2s.times_selected, 1)
        self.assertEqual(a2s.times_selected_correct, 0)

        # check GET endpoints
        resp = self.client.get(f'/api/quiz/quizzes/{quiz.id}/stats/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['quiz_id'], quiz.id)
        self.assertEqual(data['total_attempts'], qs.total_attempts)
        resp = self.client.get(f'/api/quiz/questions/{q.id}/stats/')
        self.assertEqual(resp.status_code, 200)
        qdata = resp.json()
        self.assertEqual(qdata['question_id'], q.id)
        self.assertEqual(qdata['times_asked'], qqs.times_asked)
