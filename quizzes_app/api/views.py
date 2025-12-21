import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import QuizCreateSerializer, QuizDetailSerializer
from quizzes_app.models import Quiz, Question
from .utils import extract_video_id, download_audio, transcribe_audio, generate_quiz_from_transcript

class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        input_url = serializer.validated_data['url']
        
        clean_url = extract_video_id(input_url)
        if not clean_url:
            return Response({"error": "Invalid YouTube URL"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            temp_filename = f"temp_audio_{request.user.id}"
            audio_file = download_audio(clean_url, output_path=temp_filename)
            
            if not audio_file:
                return Response({"error": "Audio download failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            transcript = transcribe_audio(audio_file)
            
            if os.path.exists(audio_file):
                os.remove(audio_file)

            quiz_data = generate_quiz_from_transcript(transcript)
            if not quiz_data:
                return Response({"error": "Quiz generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            quiz = Quiz.objects.create(
                user=request.user,
                title=quiz_data.get('title', 'Generated Quiz'),
                description=quiz_data.get('description', ''),
                video_url=clean_url
            )

            for q_data in quiz_data.get('questions', []):
                Question.objects.create(
                    quiz=quiz,
                    question_title=q_data['question_title'],
                    question_options=q_data['question_options'],
                    answer=q_data['answer']
                )

            response_serializer = QuizDetailSerializer(quiz)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            if 'audio_file' in locals() and audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)