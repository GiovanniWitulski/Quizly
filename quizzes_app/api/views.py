import os
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import QuizCreateSerializer, QuizDetailSerializer, QuizListSerializer
from quizzes_app.models import Quiz, Question
from .utils import extract_video_id, download_audio, transcribe_audio, generate_quiz_from_transcript

class CreateQuizView(APIView):
    """
    API View to create a new quiz based on a YouTube video.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Initiates the quiz generation process.

        1. Validates the YouTube URL.
        2. Downloads the audio.
        3. Transcribes the audio.
        4. Generates questions and answers via AI.
        5. Saves the quiz and questions to the database.

        Request Body:
            - url (str): YouTube video URL.

        Returns:
            201: Quiz created successfully (response includes quiz details with timestamps).
            400: Invalid URL.
            500: Error during download, transcription, or generation.
        """
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
        
class QuizListView(APIView):
    """
    API View to retrieve all quizzes for a user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns a list of all quizzes belonging to the authenticated user.
        
        Uses the QuizListSerializer (excluding question timestamps) to reduce payload size.

        Returns:
            200: List of quizzes.
        """
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizListSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuizDetailView(APIView):
    """
    API View for CRUD operations on a single quiz.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """
        Helper method: Retrieves a quiz by ID, but only if it belongs to the user.
        """
        obj = get_object_or_404(Quiz, pk=pk)
        if obj.user != user:
            return None
        return obj

    def get(self, request, pk):
        """
        Retrieves details of a specific quiz.

        Returns:
            200: Quiz details.
            403: Access denied (quiz belongs to another user).
            404: Quiz not found.
        """
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response({"detail": "You do not have permission to view this quiz."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = QuizListSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Partially updates a quiz (e.g., title).

        Returns:
            200: Quiz updated successfully.
            400: Validation errors.
            403: Access denied.
        """
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response({"detail": "You do not have permission to edit this quiz."}, status=status.HTTP_403_FORBIDDEN)

        serializer = QuizListSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Permanently deletes a quiz and its questions.

        Returns:
            204: Quiz deleted successfully.
            403: Access denied.
        """
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response({"detail": "You do not have permission to delete this quiz."}, status=status.HTTP_403_FORBIDDEN)

        quiz.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)