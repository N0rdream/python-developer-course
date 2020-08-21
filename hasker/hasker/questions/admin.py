from django.contrib import admin
from .models import Question, Answer


class QuestionModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_pub')
    list_filter = ('date_pub', )
    search_fields = ('title', 'content')
    
    class Meta:
        model = Question


admin.site.register(Question, QuestionModelAdmin)
admin.site.register(Answer)