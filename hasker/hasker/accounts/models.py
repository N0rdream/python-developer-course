from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings


class Account(AbstractUser):
    avatar = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('accounts:page', kwargs={'pk': self.pk})

    def send_email(self):
        message = f'Hello, {self.username}. You have a new answer for your question.'
        send_mail(
            'HASKER: New answer.',
            message,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False,
        )
