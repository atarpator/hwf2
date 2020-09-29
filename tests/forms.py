from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from tests.models import Answer, Question, Employee, EmployeeAnswer, User, Test


class EmployeeSignUpForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User

	@transaction.atomic
	def save(self):
		user = super().save(commit=False)
		user.is_employee = True
		user.save()
		employee = Employee.objects.create(user=user)
		return user


class ManagerSignUpForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User

	def save(self, commit=True):
		user = super().save(commit=False)
		user.is_manager = True
		if commit:
			user.save()
		return user


class QuestionForm(forms.ModelForm):
	class Meta:
		model = Question
		fields = ('text', )


class TestCreateForm(forms.ModelForm):
	class Meta:
		model = Test
		fields = ('name', 'start_date', 'end_date', )


class BaseAnswerInlineFormSet(forms.BaseInlineFormSet):
	def clean(self):
		super().clean()

		has_one_correct_answer = False
		for form in self.forms:
			if not form.cleaned_data.get('DELETE', False):
				if form.cleaned_data.get('is_correct', False):
					has_one_correct_answer = True
					break
		if not has_one_correct_answer:
			raise ValidationError('Mark at least one answer as correct.', code='no_correct_answer')


class TakeTestForm(forms.ModelForm):
	answer = forms.ModelChoiceField(
		queryset=Answer.objects.none(),
		widget=forms.RadioSelect(),
		required=True,
		empty_label=None)

	class Meta:
		model = EmployeeAnswer
		fields = ('answer', )

	def __init__(self, *args, **kwargs):
		question = kwargs.pop('question')
		super().__init__(*args, **kwargs)
		self.fields['answer'].queryset = question.answers.order_by('text')

		