from django.db import models, transaction
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings


class Tag(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class VoteMixin:

    @transaction.atomic
    def vote_up(self, user):
        if user in self.d_voters.all():
            self.d_voters.remove(user)
        if user not in self.u_voters.all():
            self.u_voters.add(user)
        self.save()

    @transaction.atomic
    def vote_down(self, user):
        if user in self.u_voters.all():
            self.u_voters.remove(user)
        if user not in self.d_voters.all():
            self.d_voters.add(user)
        self.save()

    def get_rating(self):
        return self.u_voters.count() - self.d_voters.count()


class NonHiddenQuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_hidden=False)


class Question(VoteMixin, models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_pub = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='questions',
        null=True
    )
    best_answer = models.OneToOneField('Answer', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='parent_question')
    u_voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='question_upvoters', blank=True)
    d_voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='question_downvoters', blank=True)
    tags = models.ManyToManyField(Tag, related_name='questions')
    is_hidden = models.BooleanField(default=False)

    objects = models.Manager()
    non_hidden = NonHiddenQuestionManager()


    class Meta:
        ordering = ['-date_pub']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('questions:detail', kwargs={'pk': self.id})

    def get_answers_count(self):
        return self.answers.count()

    def clear_best(self):
        self.best_answer = None
        self.save()

    def get_tags_str(self):
        return ', '.join(tag.title for tag in self.tags.all())


class Answer(VoteMixin, models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name='answers')
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='answers',
        null=True
    )
    content = models.TextField()
    date_pub = models.DateTimeField(auto_now_add=True)
    u_voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='answer_upvoters', blank=True)
    d_voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='answer_downvoters', blank=True)

    
    def __str__(self):
        return f'{self.account.username}'

    def is_best(self):
        return self.question.best_answer == self

    def make_best(self):
        self.question.best_answer = self
        self.question.save()
