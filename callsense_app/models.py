from django.db import models

# Create your models here.
# app/models.py
from django.db import models

class Transcription(models.Model):
    call_id = models.CharField(max_length=100)
    agent_id = models.CharField(max_length=50)
    customer_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    full_text = models.TextField()

class Segment(models.Model):
    transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE, related_name='segments')
    speaker = models.CharField(max_length=50)
    start_time = models.FloatField()
    end_time = models.FloatField()
    text = models.TextField()
    sentiment = models.CharField(max_length=20)

class CoachableMoment(models.Model):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)  # e.g. "objection", "buying signal"
