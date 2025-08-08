from django.contrib import admin
from .models import Transcription, Segment, CoachableMoment

admin.site.register(Transcription)
admin.site.register(Segment)
admin.site.register(CoachableMoment)
