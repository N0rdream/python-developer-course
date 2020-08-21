from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.views import View

from .forms import AccountCreationForm, AccountChangeForm
from .models import Account


class SignUp(CreateView):
    form_class = AccountCreationForm
    success_url = reverse_lazy('questions:list')
    template_name = 'accounts/sign_up.html'


class AccountDisplay(DetailView):
    context_object_name = 'account'
    model = Account
    template_name = 'accounts/account_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.get_object().email
        context['form'] = AccountChangeForm(initial = {'email': email})
        return context


class AccountChangeFormView(UpdateView):
    template_name = 'accounts/account_page.html'
    model = Account
    fields = ['email', 'avatar']
    
    def get_success_url(self):
        return reverse('accounts:page', kwargs={'pk': self.kwargs['pk']})


class AccountDetail(View):
    def get(self, request, *args, **kwargs):
        view = AccountDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = AccountChangeFormView.as_view()
        return view(request, *args, **kwargs)
