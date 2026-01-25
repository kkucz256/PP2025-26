from typing import List, Optional
from django.db import transaction
from django.utils import timezone
from ninja import NinjaAPI, Router
from .models import Question, Answers, Quiz, Users, QuizSession, QuizAttempt
from .schemas import (
    QuestionIn,
    AnswerIn,
    QuestionOut,
    AnswerOut,
    QuizOut,
    QuizListOut,
    QuizIn,
    QuestionCreateIn,
    ShareIn,
    ShareOut,
    QuizSessionIn,
    QuizSessionOut,
    QuizAttemptIn,
    QuizAttemptOut,
    AnswerSubmission,
    SubmissionResult,
    SubmitIn,
    SubmitOut,
)

from . import services

api = NinjaAPI(title="Przejsciowy Quiz API", version="1.0.0", docs_url="/docs", openapi_url="/openapi.json")
router = Router()


@router.post("/questions/", response={201: QuestionOut, 404: dict})
def create_question(request, payload: QuestionIn):
    """Create a question with optional answers"""
    try:
        quiz = Quiz.objects.get(pk=payload.quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}

    with transaction.atomic():
        q = Question.objects.create(quiz=quiz, content=payload.content, position=payload.position)
        answers_objs = [Answers(question=q, content=a.content, is_correct=a.is_correct) for a in payload.answers]
        if answers_objs:
            Answers.objects.bulk_create(answers_objs)
        # refresh answers
        answers = list(q.answers.all())

    response = QuestionOut(
        id=q.id,
        quiz_id=quiz.id,
        content=q.content,
        position=q.position,
        answers=[AnswerOut(id=a.id, content=a.content, is_correct=bool(a.is_correct)) for a in answers],
    )
    return 201, response


@router.post("/questions/{question_id}/answers/", response={201: AnswerOut, 404: dict})
def create_answer(request, question_id: int, payload: AnswerIn):
    """Add an answer to an existing question"""
    try:
        q = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return 404, {"detail": "Question not found"}

    a = Answers.objects.create(question=q, content=payload.content, is_correct=payload.is_correct)
    return 201, AnswerOut(id=a.id, content=a.content, is_correct=bool(a.is_correct))


@router.get("/questions/{question_id}/", response={200: QuestionOut, 404: dict})
def get_question(request, question_id: int):
    try:
        q = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return 404, {"detail": "Question not found"}

    answers = list(q.answers.all())
    return 200, QuestionOut(
        id=q.id,
        quiz_id=q.quiz_id,
        content=q.content,
        position=q.position,
        answers=[AnswerOut(id=a.id, content=a.content, is_correct=bool(a.is_correct)) for a in answers],
    )


@router.get("/questions/", response=List[QuestionOut])
def list_questions(request, quiz_id: Optional[int] = None):
    """List questions, optionally filtered by quiz_id"""
    qs = Question.objects.all()
    if quiz_id is not None:
        qs = qs.filter(quiz_id=quiz_id)

    result = []
    for q in qs:
        answers = list(q.answers.all())
        result.append(
            QuestionOut(
                id=q.id,
                quiz_id=q.quiz_id,
                content=q.content,
                position=q.position,
                answers=[AnswerOut(id=a.id, content=a.content, is_correct=bool(a.is_correct)) for a in answers],
            )
        )
    return result


@router.get("/quizzes/", response=QuizListOut)
def list_quizzes(request, user_id: Optional[int] = None):
    """List quizzes with embedded questions and answers. Optionally filter by related user_id."""
    qs = Quiz.objects.all()
    if user_id is not None:
        qs = qs.filter(quiz_users__user_id=user_id)

    data = []
    for q in qs:
        questions = []
        for qq in q.questions.all():
            answers = list(qq.answers.all())
            questions.append(
                QuestionOut(
                    id=qq.id,
                    quiz_id=qq.quiz_id,
                    content=qq.content,
                    position=qq.position,
                    answers=[AnswerOut(id=a.id, content=a.content, is_correct=bool(a.is_correct)) for a in answers],
                )
            )
        data.append(QuizOut(id=q.id, content=q.content, slug=q.slug, questions=questions))
    return {"quizzes": data}


@router.get("/quizzes/{quiz_id}/", response=QuizOut)
def get_quiz(request, quiz_id: int):
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}

    questions = []
    for q in quiz.questions.all():
        answers = list(q.answers.all())
        questions.append(
            QuestionOut(
                id=q.id,
                quiz_id=q.quiz_id,
                content=q.content,
                position=q.position,
                answers=[AnswerOut(id=a.id, content=a.content, is_correct=bool(a.is_correct)) for a in answers],
            )
        )

    return QuizOut(id=quiz.id, content=quiz.content, slug=quiz.slug, questions=questions)


@router.post("/quizzes/", response={201: QuizOut, 400: dict})
def create_quiz(request, payload: QuizIn):
    """Create quiz and optional nested questions/answers"""
    # simple validation: unique slug
    if Quiz.objects.filter(slug=payload.slug).exists():
        return 400, {"detail": "Quiz with this slug already exists"}

    with transaction.atomic():
        quiz = Quiz.objects.create(content=payload.content, slug=payload.slug)
        created_questions = []
        for q_in in payload.questions or []:
            q = Question.objects.create(quiz=quiz, content=q_in.content, position=q_in.position)
            answers_objs = [Answers(question=q, content=a.content, is_correct=a.is_correct) for a in (q_in.answers or [])]
            if answers_objs:
                Answers.objects.bulk_create(answers_objs)
            answers = list(q.answers.all())
            created_questions.append(
                QuestionOut(
                    id=q.id,
                    quiz_id=quiz.id,
                    content=q.content,
                    position=q.position,
                    answers=[AnswerOut(id=a.id, content=a.content, is_correct=bool(a.is_correct)) for a in answers],
                )
            )

        # if owner provided, link user to quiz
        if payload.owner_id is not None:
            try:
                owner = Users.objects.get(pk=payload.owner_id)
                from .models import QuizUser
                QuizUser.objects.create(quiz=quiz, user=owner)
            except Users.DoesNotExist:
                # rollback
                transaction.set_rollback(True)
                return 400, {"detail": "Owner user not found"}

    return 201, QuizOut(id=quiz.id, content=quiz.content, slug=quiz.slug, questions=created_questions)

@router.delete("/quizzes/{quiz_id}/", response={204: None, 400: dict, 404: dict})
def delete_quiz(request, quiz_id: int):
    """Remove quiz from user's library (delete QuizUser relation)"""
    from .models import QuizUser
    
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}

    # Get user_id from request
    user_id = request.session.get('user_id') or request.query_params.get('user_id')
    if not user_id:
        return 400, {"detail": "User ID not provided"}

    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return 404, {"detail": "User not found"}

    # Delete QuizUser relation instead of entire quiz
    deleted, _ = QuizUser.objects.filter(quiz=quiz, user=user).delete()
    
    if deleted == 0:
        return 400, {"detail": "Quiz is not in your library"}
    
    return 204, None


@router.delete("/questions/{question_id}/", response={204: None, 404: dict})
def delete_question(request, question_id: int):
    try:
        q = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return 404, {"detail": "Question not found"}

    q.delete()
    return 204, None

@router.post("/sessions/", response={201: QuizSessionOut, 404: dict})
def create_session(request, payload: QuizSessionIn):
    try:
        quiz = Quiz.objects.get(pk=payload.quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}
    try:
        host = Users.objects.get(pk=payload.host_id)
    except Users.DoesNotExist:
        return 404, {"detail": "Host user not found"}

    session = QuizSession.objects.create(
        quiz=quiz,
        host=host,
        access_code=payload.access_code or f"AC{quiz.id}{int(timezone.now().timestamp())}",
        start_time=payload.start_time,
        end_time=payload.end_time,
        is_active=payload.is_active,
    )
    return 201, QuizSessionOut(
        id=session.id,
        quiz_id=session.quiz_id,
        host_id=session.host_id,
        access_code=session.access_code,
        start_time=session.start_time.isoformat() if session.start_time else None,
        end_time=session.end_time.isoformat() if session.end_time else None,
        is_active=session.is_active,
    )


@router.get("/sessions/", response=List[QuizSessionOut])
def list_sessions(request, quiz_id: Optional[int] = None, host_id: Optional[int] = None, active: Optional[bool] = None):
    qs = QuizSession.objects.all()
    if quiz_id is not None:
        qs = qs.filter(quiz_id=quiz_id)
    if host_id is not None:
        qs = qs.filter(host_id=host_id)
    if active is not None:
        qs = qs.filter(is_active=active)

    result = []
    for s in qs:
        result.append(QuizSessionOut(
            id=s.id,
            quiz_id=s.quiz_id,
            host_id=s.host_id,
            access_code=s.access_code,
            start_time=s.start_time.isoformat() if s.start_time else None,
            end_time=s.end_time.isoformat() if s.end_time else None,
            is_active=s.is_active,
        ))
    return result


@router.post("/attempts/", response={201: QuizAttemptOut, 404: dict})
def create_attempt(request, payload: QuizAttemptIn):
    try:
        quiz = Quiz.objects.get(pk=payload.quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}
    try:
        user = Users.objects.get(pk=payload.user_id)
    except Users.DoesNotExist:
        return 404, {"detail": "User not found"}

    attempt = QuizAttempt.objects.create(quiz=quiz, user=user, start_date=timezone.now(), correct=0, incorrect=0)
    return 201, QuizAttemptOut(id=attempt.id, quiz_id=attempt.quiz_id, user_id=attempt.user_id, start_date=attempt.start_date.isoformat(), end_date=None, correct=0, incorrect=0)


@router.get("/attempts/", response=List[QuizAttemptOut])
def list_attempts(request, quiz_id: Optional[int] = None, user_id: Optional[int] = None):
    qs = QuizAttempt.objects.all()
    if quiz_id is not None:
        qs = qs.filter(quiz_id=quiz_id)
    if user_id is not None:
        qs = qs.filter(user_id=user_id)

    result = []
    for a in qs:
        result.append(QuizAttemptOut(
            id=a.id,
            quiz_id=a.quiz_id,
            user_id=a.user_id,
            start_date=a.start_date.isoformat() if a.start_date else None,
            end_date=a.end_date.isoformat() if a.end_date else None,
            correct=a.correct,
            incorrect=a.incorrect,
        ))
    return result


@router.post("/attempts/{attempt_id}/submit/", response=SubmitOut)
def submit_attempt(request, attempt_id: int, payload: SubmitIn):
    """Check submitted answers, update attempt stats, and return detailed results"""
    try:
        attempt = QuizAttempt.objects.get(pk=attempt_id)
    except QuizAttempt.DoesNotExist:
        return {"results": [], "total_correct": 0, "total_incorrect": 0}

    total_correct = 0
    total_incorrect = 0
    results = []

    with transaction.atomic():
        for ans in payload.answers:
            try:
                q = Question.objects.get(pk=ans.question_id, quiz_id=attempt.quiz_id)
            except Question.DoesNotExist:
                continue

            correct_ids = set(Answers.objects.filter(question=q, is_correct=True).values_list('id', flat=True))
            selected = set(ans.selected_answer_ids)
            is_correct = selected == correct_ids
            if is_correct:
                total_correct += 1
            else:
                total_incorrect += 1

            results.append(SubmissionResult(
                question_id=q.id,
                correct=is_correct,
                correct_answer_ids=list(correct_ids),
                selected_answer_ids=list(selected),
            ))

        attempt.correct = (attempt.correct or 0) + total_correct
        attempt.incorrect = (attempt.incorrect or 0) + total_incorrect
        attempt.end_date = timezone.now()
        attempt.save()

        # update persistent statistics
        stats_payload = [
            {
                "question_id": r.question_id,
                "correct": r.correct,
                "correct_answer_ids": r.correct_answer_ids,
                "selected_answer_ids": r.selected_answer_ids,
            }
            for r in results
        ]
        services.update_stats_on_submission(attempt, stats_payload)

    return SubmitOut(results=results, total_correct=total_correct, total_incorrect=total_incorrect)


@router.post("/quizzes/{quiz_id}/share/", response={201: ShareOut, 400: dict, 404: dict})
def share_quiz(request, quiz_id: int, payload: ShareIn):
    """Share a quiz with another user (create QuizUser relation)"""
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}

    try:
        user = Users.objects.get(pk=payload.user_id)
    except Users.DoesNotExist:
        return 404, {"detail": "User not found"}

    from .models import QuizUser
    if QuizUser.objects.filter(quiz=quiz, user=user).exists():
        return 400, {"detail": "Quiz already shared with this user"}

    QuizUser.objects.create(quiz=quiz, user=user)
    return 201, ShareOut(quiz_id=quiz.id, user_id=user.id, detail="shared")


@router.get("/quizzes/{quiz_id}/stats/", response=dict)
def quiz_stats(request, quiz_id: int):
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}

    return services.get_quiz_stats(quiz)


@router.get("/questions/{question_id}/stats/", response=dict)
def question_stats(request, question_id: int):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return 404, {"detail": "Question not found"}

    return services.get_question_stats(question)


@router.get("/quizzes/{quiz_id}/ranking/", response=dict)
def quiz_ranking(request, quiz_id: int):
    """Pobierz ranking użytkowników dla konkretnego quizu"""
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return 404, {"detail": "Quiz not found"}
    
    # Pobierz wszystkie ukończone podejścia dla tego quizu
    completed_attempts = QuizAttempt.objects.filter(
        quiz=quiz, 
        end_date__isnull=False
    ).select_related('user')
    
    total_questions = quiz.questions.count()
    ranking = []
    
    # Zgrupuj podejścia po użytkownikach
    users_stats = {}
    for attempt in completed_attempts:
        username = attempt.user.username
        if username not in users_stats:
            users_stats[username] = {
                'user_id': attempt.user_id,
                'attempts': [],
            }
        
        if attempt.start_date and attempt.end_date:
            duration = (attempt.end_date - attempt.start_date).total_seconds() / 60
        else:
            duration = 0
        
        percentage = 0
        if total_questions > 0:
            percentage = round((attempt.correct / total_questions) * 100, 2)
        
        users_stats[username]['attempts'].append({
            'correct': attempt.correct,
            'incorrect': attempt.incorrect,
            'percentage': percentage,
            'duration': round(duration, 1),
            'date': attempt.end_date.isoformat() if attempt.end_date else None,
        })
    
    # Oblicz statystyki dla każdego użytkownika
    for username, data in users_stats.items():
        attempts = data['attempts']
        
        # Średni wynik
        avg_correct = sum(a['correct'] for a in attempts) / len(attempts)
        avg_percentage = round((avg_correct / total_questions) * 100, 2) if total_questions > 0 else 0
        
        # Średni czas
        durations = [a['duration'] for a in attempts]
        avg_duration = round(sum(durations) / len(durations), 1) if durations else 0
        best_duration = round(min(durations), 1) if durations else 0
        
        ranking.append({
            'username': username,
            'user_id': data['user_id'],
            'attempts_count': len(attempts),
            'avg_percentage': avg_percentage,
            'avg_duration': avg_duration,
            'best_duration': best_duration,
            'best_percentage': max(a['percentage'] for a in attempts),
        })
    
    return {
        'quiz_id': quiz_id,
        'quiz_name': quiz.content,
        'total_questions': total_questions,
        'ranking': ranking,
    }


@router.get("/users/", response=list)
def get_all_users(request):
    """Get list of all users (for sharing quizzes), excluding current user"""
    user_id = request.session.get('user_id') or request.query_params.get('exclude_user_id')
    
    users = Users.objects.all().values('id', 'username')
    
    # Exclude current user
    if user_id:
        users = users.exclude(id=user_id)
    
    return list(users)


api.add_router("/quiz/", router)