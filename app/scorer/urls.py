from django.urls import path
from .views import ScoreView

urlpatterns=[path('score/', ScoreView.as_view(), name='score')]
