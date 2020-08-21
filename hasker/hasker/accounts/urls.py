from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'accounts'

urlpatterns = [
    path('sign_up/', views.SignUp.as_view(), name='sign_up'),
    path('sign_in/', auth_views.LoginView.as_view(template_name='accounts/sign_in.html'), name='sign_in'),
    re_path(r'^(?P<pk>\d+)/$', views.AccountDetail.as_view(), name='page'),
]
