from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, date


class User(AbstractUser):
	is_employee = models.BooleanField(default=False)
	is_manager = models.BooleanField(default=False)


class Test(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
	name = models.CharField(max_length=255)
	start_date = models.DateTimeField('Start date', null=True)
	end_date = models.DateTimeField('End date', null=True)
	
	def __str__(self):
		return self.name

	@property
	def is_now(self):
		return self.start_date < timezone.now() < self.end_date


class Question(models.Model):
	test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
	text = models.TextField('Question')

	def __str__(self):
		return self.text


class Answer(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
	text = models.CharField('Answer', max_length=255)
	is_correct = models.BooleanField('Correct answer', default=False)

	def __str__(self):
		return self.text


class Employee(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	tests = models.ManyToManyField(Test, through='TakenTest')
	score = models.IntegerField(default=0)

	def get_unanswered_questions(self, test):
		answered_questions = self.test_answers \
			.filter(answer__question__test=test) \
			.values_list('answer__question__pk', flat=True)
		questions = test.questions.exclude(pk__in=answered_questions).order_by('text')
		return questions

	def __str__(self):
		return self.user.username


class TakenTest(models.Model):
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='taken_tests')
	test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='taken_tests')
	score = models.IntegerField()
	percentage = models.FloatField()
	date = models.DateTimeField(auto_now_add=True)


class EmployeeAnswer(models.Model):
	employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='test_answers')
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')
