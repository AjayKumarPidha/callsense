# app/urls.py
from django.urls import path
from .views import TranscribeView, SpeakView, ReplayView, CoachableMomentListView

urlpatterns = [
    path('transcribe/', TranscribeView.as_view(), name='transcribe'),
    path('speak/', SpeakView.as_view(), name='speak'),
    path('replay/', ReplayView.as_view(), name='replay'),
    path('moments/<int:transcription_id>/', CoachableMomentListView.as_view(), name='coachable-moments'),
]

