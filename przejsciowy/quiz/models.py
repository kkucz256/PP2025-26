# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Answers(models.Model):
    question = models.ForeignKey('Question', models.DO_NOTHING)
    content = models.TextField()
    is_correct = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'answers'


class Question(models.Model):
    quiz = models.ForeignKey('Quiz', models.DO_NOTHING)
    content = models.TextField()
    position = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'question'


class Quiz(models.Model):
    content = models.CharField(max_length=255)
    slug = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'quiz'


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    correct = models.IntegerField(blank=True, null=True)
    incorrect = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quiz_attempt'


class QuizSession(models.Model):
    quiz = models.ForeignKey(Quiz, models.DO_NOTHING)
    host = models.ForeignKey('Users', models.DO_NOTHING)
    access_code = models.CharField(max_length=20)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quiz_session'


class QuizUser(models.Model):
    pk = models.CompositePrimaryKey('quiz_id', 'user_id')
    quiz = models.ForeignKey(Quiz, models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'quiz_user'


class Users(models.Model):
    username = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    mail = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'users'
