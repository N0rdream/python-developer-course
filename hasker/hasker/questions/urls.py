from django.urls import path, re_path
from . import views


app_name = 'questions'

urlpatterns = [
    path('', views.QuestionListView.as_view(), name='list'),
    path('create/', views.QuestionAskView.as_view(), name='ask'),
    re_path(r'^(?P<pk>\d+)/$', views.QuestionDetail.as_view(), name='detail'),
    path('set_best_answer/<int:id_a>/', views.set_best_answer, name='set_best_answer'),
    path('clear_best_answer/<int:id_q>/', views.clear_best_answer, name='clear_best_answer'),
    path('<int:id_q>/u_vote/', views.vote_up_question, name='vote_up_question'),
    path('<int:id_q>/d_vote/', views.vote_down_question, name='vote_down_question'),
    path('answer/<int:id_a>/u_vote/', views.vote_up_answer, name='vote_up_answer'),
    path('answer/<int:id_a>/d_vote/', views.vote_down_answer, name='vote_down_answer'),
]