# app/serializers.py
from rest_framework import serializers
from .models import Transcription, Segment, CoachableMoment

class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = '__all__'

class TranscriptionSerializer(serializers.ModelSerializer):
    segments = SegmentSerializer(many=True, read_only=True)

    class Meta:
        model = Transcription
        fields = '__all__'

class CoachableMomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachableMoment
        fields = '__all__'


from .models import CoachableMoment

class CoachableMomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachableMoment
        fields = ['id', 'label', 'segment']
