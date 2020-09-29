from django.contrib import admin
from .models import User, Test, Question, Answer, Employee, TakenTest

admin.site.register(User)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Employee)
admin.site.register(TakenTest)
