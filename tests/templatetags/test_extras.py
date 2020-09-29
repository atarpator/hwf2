from django import template
from django.db.models import Sum
from tests.models import EmployeeAnswer
import hashlib

register = template.Library()

@register.simple_tag
def marked_answer(user,opt):
    employeeanswer = EmployeeAnswer.objects.filter(employee=user.employee, answer =opt)
    if employeeanswer:
        if opt.is_correct:
            return 'correct'
        return 'wrong'
    return ''

@register.filter
def gravatar_url(username, size=40):
    # TEMPLATE USE:  {{ email|gravatar_url:150 }}
    username_hash = hashlib.md5(username.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{username_hash}?s={size}&d=identicon"

