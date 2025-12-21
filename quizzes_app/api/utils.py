import os
import re
import json
import yt_dlp
import whisper
from google import genai
from django.conf import settings

def extract_video_id(url):
    regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(regex, url)
    
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def download_audio(url, output_path="temp_audio"):
    tmp_filename = f"{output_path}.%(ext)s"
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    for ext in ['webm', 'm4a', 'mp3']:
        potential_file = f"{output_path}.{ext}"
        if os.path.exists(potential_file):
            return potential_file
            
    return None

def transcribe_audio(file_path):
    model = whisper.load_model("base") 
    result = model.transcribe(file_path)
    return result["text"]

def generate_quiz_from_transcript(transcript):
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return None
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
                Based on the following transcript, generate a quiz in valid JSON format.

                The quiz must follow this exact structure:
                {{
                "title": "Create a concise quiz title based on the topic of the transcript.",
                "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
                "questions": [
                    {{
                    "question_title": "The question goes here.",
                    "question_options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "The correct answer from the above options"
                    }},
                    ...
                    (exactly 10 questions)
                ]
                }}

                Requirements:
                - Each question must have exactly 4 distinct answer options.
                - Only one correct answer is allowed per question, and it must be present in 'question_options'.
                - The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
                - Do not include explanations, comments, or any text outside the JSON.

                Transcript:
                {transcript}
            """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        response_text = response.text
        cleaned_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
        
        return json.loads(cleaned_text)

    except Exception as e:
        print(f"Failed to generate quiz: {e}")
        return None