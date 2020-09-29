from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'

def home(request):
    if request.user.is_authenticated:
        if request.user.is_manager:
            return redirect('managers:test_change_list')
        elif request.user.is_employee:
            return redirect('employees:test_list')
        else:
            return redirect('admin:index')
    return render(request, 'tests/home.html')
