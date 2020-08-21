from django import template
from questions.models import Question
from django.db.models import Count, F


register = template.Library()

@register.inclusion_tag('sidebar.html')
def show_hot_top():
 
    questions = Question.non_hidden.annotate(
        uvoters=Count('u_voters'),
        dvoters=Count('d_voters')
    ).order_by(F('dvoters') - F('uvoters'), '-date_pub')
    
    return {'questions': questions}
