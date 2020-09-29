from django.urls import path, include
from .views import tests, employees, managers

urlpatterns = [
	path('', tests.home, name='home'),

	path('employees/', include(([
        path('', employees.TestListView.as_view(), name='test_list'),
        path('taken/', employees.TakenTestListView.as_view(), name='taken_test_list'),
        path('test/<int:pk>/', employees.take_test, name='take_test'),        
        path('test/<int:pk>/employeeresults/', employees.TestResultsView.as_view(), name='employee_test_results'),
    ], 'tests'), namespace='employees')),

    path('managers/', include(([
        path('', managers.TestListView.as_view(), name='test_change_list'),
        path('test/add/', managers.TestCreateView.as_view(), name='test_add'),
        path('test/<int:pk>/', managers.TestUpdateView.as_view(), name='test_change'),
        path('test/<int:pk>/delete/', managers.TestDeleteView.as_view(), name='test_delete'),
        path('test/<int:pk>/results/', managers.TestResultsView.as_view(), name='test_results'),
        path('test/<int:pk>/question/add/', managers.question_add, name='question_add'),
        path('test/<int:test_pk>/question/<int:question_pk>/', managers.question_change, name='question_change'),
        path('test/<int:test_pk>/question/<int:question_pk>/delete/', managers.QuestionDeleteView.as_view(), name='question_delete'),
    ], 'tests'), namespace='managers')),
]
