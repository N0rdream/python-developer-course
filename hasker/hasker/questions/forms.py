from django import forms
from .models import Question, Answer
from django.core.exceptions import ValidationError


class QuestionForm(forms.ModelForm):

    tags = forms.CharField(max_length=100)

    class Meta:
        model = Question
        fields = ['title', 'content']

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        tags = set(tag.strip() for tag in tags.split(',') if tag.strip())
        if not tags:
            raise ValidationError('No tags added.')
        if len(tags) > 3:
            raise ValidationError('Too many tags added.')
        return tags


class AnswerForm(forms.ModelForm):
    
    class Meta:
        model = Answer
        fields = ['content']