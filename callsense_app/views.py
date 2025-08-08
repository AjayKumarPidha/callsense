from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import status
from django.http import FileResponse
from .models import Transcription, Segment, CoachableMoment
from .serializers import TranscriptionSerializer, CoachableMomentSerializer
import tempfile
import os
import subprocess
import whisper
from transformers import pipeline
from gtts import gTTS

# Global variables for lazy-loading
_whisper_model = None
_sentiment_pipeline = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        # Use "tiny" to reduce RAM usage
        _whisper_model = whisper.load_model("tiny")
    return _whisper_model


def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    return _sentiment_pipeline


class TranscribeView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        audio = request.FILES.get('audio')
        call_id = request.POST.get('call_id')
        agent_id = request.POST.get('agent_id')
        customer_id = request.POST.get('customer_id')

        if not audio:
            return Response({'error': 'Audio file required.'}, status=400)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            for chunk in audio.chunks():
                tmp_file.write(chunk)
            tmp_mp4_path = tmp_file.name

        # Convert to WAV for Whisper
        tmp_wav_path = tmp_mp4_path.replace(".mp4", ".wav")
        try:
            subprocess.run(
                ['ffmpeg', '-y', '-i', tmp_mp4_path, '-ar', '16000', '-ac', '1', tmp_wav_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            os.remove(tmp_mp4_path)
            return Response({'error': 'Invalid or unreadable audio file.'}, status=400)

        try:
            model = get_whisper_model()
            result = model.transcribe(tmp_wav_path)
        except Exception as e:
            os.remove(tmp_mp4_path)
            os.remove(tmp_wav_path)
            return Response({'error': str(e)}, status=500)

        transcription = Transcription.objects.create(
            call_id=call_id,
            agent_id=agent_id,
            customer_id=customer_id,
            full_text=result['text']
        )

        sentiment_model = get_sentiment_pipeline()
        for seg in result.get("segments", []):
            sentiment = sentiment_model(seg['text'])[0]['label']
            segment = Segment.objects.create(
                transcription=transcription,
                speaker=f"Speaker {seg.get('speaker', 'Unknown')}",
                start_time=seg['start'],
                end_time=seg['end'],
                text=seg['text'],
                sentiment=sentiment
            )
            if "price" in seg['text'].lower():
                CoachableMoment.objects.create(segment=segment, label="objection")

        os.remove(tmp_mp4_path)
        os.remove(tmp_wav_path)

        return Response(TranscriptionSerializer(transcription).data)


class SpeakView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        text = request.data.get('text')
        if not text:
            return Response({'error': 'Text is required'}, status=400)

        tts = gTTS(text=text)
        tmp_path = tempfile.mktemp(suffix=".mp3")
        tts.save(tmp_path)

        return FileResponse(open(tmp_path, "rb"), content_type="audio/mpeg", filename="tts.mp3")


class CoachableMomentListView(APIView):
    def get(self, request, transcription_id):
        moments = CoachableMoment.objects.filter(segment__transcription_id=transcription_id)
        return Response(CoachableMomentSerializer(moments, many=True).data)


class ReplayView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        moment_id = request.data.get("moment_id")
        try:
            moment = CoachableMoment.objects.select_related('segment').get(id=moment_id)
        except CoachableMoment.DoesNotExist:
            return Response({'error': 'Moment not found'}, status=404)


        tts = gTTS(text=moment.segment.text)
        tmp_path = tempfile.mktemp(suffix=".mp4")
        tts.save(tmp_path)

        return FileResponse(open(tmp_path, "rb"), content_type="audio/mpeg", filename="replay.mp4")
