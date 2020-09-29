from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
from django.views import View

from ..decorators import employee_required
from ..forms import EmployeeSignUpForm, TakeTestForm
from ..models import User, Test, Employee, TakenTest, Question

User = get_user_model()

class EmployeeSignUpView(CreateView):
	model = User
	form_class = EmployeeSignUpForm
	template_name = 'registration/signup_form.html'

	def get_context_data(self, **kwargs):
		kwargs['user_type'] = 'employee'
		return super().get_context_data(**kwargs)

	def form_valid(self, form):
		user = form.save()
		login(self.request, user)
		return redirect('employees:test_list')


@method_decorator([login_required, employee_required], name='dispatch')
class TestListView(ListView):
	model = Test
	ordering = ('name', )
	context_object_name = 'tests'
	template_name = 'tests/employees/test_list.html'

	def get_queryset(self):
		employee = self.request.user.employee
		taken_tests = employee.tests.values_list('pk', flat=True)
		queryset = Test.objects.exclude(pk__in=taken_tests) \
			.annotate(questions_count=Count('questions')) \
			.filter(questions_count__gt=0)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context


@method_decorator([login_required, employee_required], name='dispatch')
class TestResultsView(View):
    template_name = 'tests/employees/test_result.html'

    def get(self, request, *args, **kwargs):        
        test = Test.objects.get(id = kwargs['pk'])
        taken_test = TakenTest.objects.filter(employee = request.user.employee, test = test)
        if not taken_test:
            """
            Don't show the result if the user didn't attempted the test
            """
            return render(request, '404.html')
        questions = Question.objects.filter(test =test)
        return render(request, self.template_name, {'questions':questions, 
            'test':test, 'percentage': taken_test[0].percentage})


@method_decorator([login_required, employee_required], name='dispatch')
class TakenTestListView(ListView):
	model = TakenTest
	context_object_name = 'taken_tests'
	template_name = 'tests/employees/taken_test_list.html'

	def get_queryset(self):
		queryset = self.request.user.employee.taken_tests \
			.order_by('test__name')
		return queryset


@login_required
@employee_required
def take_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    employee = request.user.employee

    if employee.tests.filter(pk=pk).exists():
        return render(request, 'employees/taken_test.html')

    total_questions = test.questions.count()
    unanswered_questions = employee.get_unanswered_questions(test)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeTestForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                employee_answer = form.save(commit=False)
                employee_answer.employee = employee
                employee_answer.save()
                if employee.get_unanswered_questions(test).exists():
                    return redirect('employees:take_test', pk)
                else:
                    correct_answers = employee.test_answers.filter(answer__question__test=test, answer__is_correct=True).count()
                    percentage = round((correct_answers / total_questions) * 100.0, 2)
                    TakenTest.objects.create(employee=employee, test=test, score=correct_answers, percentage= percentage)
                    employee.score = TakenTest.objects.filter(employee=employee).aggregate(Sum('score'))['score__sum']
                    employee.save()
                    if percentage < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the test %s was %s.' % (test.name, percentage))
                    else:
                        messages.success(request, 'Congratulations! You completed the test %s with success! You scored %s points.' % (test.name, percentage))
                    return redirect('employees:employee_test_results', pk)
    else:
        form = TakeTestForm(question=question)

    return render(request, 'tests/employees/take_test_form.html', {
        'test': test,
        'question': question,
        'form': form,
        'progress': progress,
        'answered_questions': total_questions - total_unanswered_questions,
        'total_questions': total_questions
    })
	