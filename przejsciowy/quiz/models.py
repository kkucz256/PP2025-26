from django.db import models


class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)

    class Meta:
        db_table = 'quiz'

    def __str__(self):
        return self.content


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, models.CASCADE, related_name='questions')
    content = models.TextField()
    position = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'question'
        ordering = ['position']

    def __str__(self):
        return f"Question {self.id} - {self.content[:50]}"


class Answers(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, models.CASCADE, related_name='answers')
    content = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'answers'

    def __str__(self):
        return f"Answer {self.id} for Question {self.question_id}"


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    mail = models.CharField(unique=True, max_length=255)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class QuizAttempt(models.Model):
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, models.CASCADE, related_name='attempts')
    user = models.ForeignKey(Users, models.CASCADE, related_name='attempts')
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    correct = models.IntegerField(blank=True, null=True)
    incorrect = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'quiz_attempt'


class QuizSession(models.Model):
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, models.CASCADE, related_name='sessions')
    host = models.ForeignKey(Users, models.CASCADE, related_name='hosted_sessions')
    access_code = models.CharField(max_length=20)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'quiz_session'


class QuizUser(models.Model):
    id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, models.CASCADE, related_name='quiz_users')
    user = models.ForeignKey(Users, models.CASCADE, related_name='user_quizzes')

    class Meta:
        db_table = 'quiz_user'


class QuizStat(models.Model):
    quiz = models.OneToOneField(Quiz, models.CASCADE, related_name='stat')
    total_attempts = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_incorrect = models.IntegerField(default=0)

    class Meta:
        db_table = 'quiz_stat'


class QuestionStat(models.Model):
    question = models.OneToOneField(Question, models.CASCADE, related_name='stat')
    times_asked = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)

    class Meta:
        db_table = 'question_stat'


class AnswerStat(models.Model):
    answer = models.OneToOneField(Answers, models.CASCADE, related_name='stat')
    times_selected = models.IntegerField(default=0)
    times_selected_correct = models.IntegerField(default=0)

    class Meta:
        db_table = 'answer_stat'

