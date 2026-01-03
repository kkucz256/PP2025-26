from typing import List, Optional
from ninja import Schema


class AnswerIn(Schema):
    content: str
    is_correct: bool = False


class QuestionIn(Schema):
    quiz_id: int
    content: str
    position: Optional[int] = None
    answers: List[AnswerIn] = []


class AnswerOut(Schema):
    id: int
    content: str
    is_correct: bool


class QuestionOut(Schema):
    id: int
    quiz_id: int
    content: str
    position: Optional[int]
    answers: List[AnswerOut]


class QuizOut(Schema):
    id: int
    content: str
    slug: str
    # optionally include questions
    questions: Optional[List[QuestionOut]] = None


class QuizListOut(Schema):
    quizzes: List[QuizOut]


class QuestionCreateIn(Schema):
    content: str
    position: Optional[int] = None
    answers: List[AnswerIn] = []


class QuizIn(Schema):
    content: str
    slug: str
    owner_id: Optional[int] = None
    questions: Optional[List[QuestionCreateIn]] = []


class ShareIn(Schema):
    user_id: int


class ShareOut(Schema):
    quiz_id: int
    user_id: int
    detail: Optional[str] = None


# Sessions and Attempts
class QuizSessionIn(Schema):
    quiz_id: int
    host_id: int
    access_code: Optional[str] = None
    start_time: Optional[str] = None  # ISO datetime
    end_time: Optional[str] = None
    is_active: Optional[bool] = None


class QuizSessionOut(Schema):
    id: int
    quiz_id: int
    host_id: int
    access_code: str
    start_time: Optional[str]
    end_time: Optional[str]
    is_active: Optional[bool]


class QuizAttemptIn(Schema):
    quiz_id: int
    user_id: int


class QuizAttemptOut(Schema):
    id: int
    quiz_id: int
    user_id: int
    start_date: Optional[str]
    end_date: Optional[str]
    correct: Optional[int]
    incorrect: Optional[int]


# Submission
class AnswerSubmission(Schema):
    question_id: int
    selected_answer_ids: List[int]


class SubmissionResult(Schema):
    question_id: int
    correct: bool
    correct_answer_ids: List[int]
    selected_answer_ids: List[int]


class SubmitIn(Schema):
    answers: List[AnswerSubmission]


class SubmitOut(Schema):
    results: List[SubmissionResult]
    total_correct: int
    total_incorrect: int