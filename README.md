# Quizly - AI-Powered Quiz Generator API

Quizly is a powerful RESTful API built with Django and Django REST Framework. It leverages artificial intelligence to automatically generate interactive quizzes from YouTube videos. By combining `yt-dlp` for audio extraction, OpenAI's Whisper for transcription, and Google's Gemini API for content generation, Quizly turns video content into learning assessments in seconds.

## 🚀 Features

* **User Authentication**: Secure registration and login using JWT (JSON Web Tokens) stored in HTTP-only cookies.
* **YouTube to Quiz**: simply paste a YouTube URL to generate a quiz.
* **AI Transcription**: Uses OpenAI Whisper to accurately transcribe video audio.
* **AI Quiz Generation**: Uses Google Gemini to analyze transcripts and generate relevant questions, options, and answers.
* **Quiz Management**: Full CRUD (Create, Read, Update, Delete) capabilities for managing user quizzes.
* **Performance**: Optimized API endpoints for listing and detailing quizzes.

## 🛠️ Tech Stack

* **Framework**: Django & Django REST Framework
* **Authentication**: `simplejwt` (custom cookie-based implementation)
* **AI & ML**:
    * `google-genai` (Gemini)
    * `openai-whisper`
    * `yt-dlp`
* **Database**: SQLite (Default)
* **Utilities**: `python-dotenv`

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

* Python 3.12+
* **FFmpeg** (Required for `yt-dlp` and `whisper` audio processing)

## ⚙️ Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/GiovanniWitulski/Quizly.git
    cd quizly
    ```

2.  **Create and activate a virtual environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```env
    GEMINI_API_KEY=your_google_gemini_api_key_here
    # Optional:
    # SECRET_KEY=your_django_secret_key
    # DEBUG=True
    ```

5.  **Run Migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Start the Server**
    ```bash
    python manage.py runserver
    ```

## 📚 API Documentation

### Authentication

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/register/` | Register a new user. |
| `POST` | `/api/login/` | Login and set HttpOnly cookies (`access_token`, `refresh_token`). |
| `POST` | `/api/logout/` | Logout and clear auth cookies. |
| `POST` | `/api/token/refresh/` | Refresh the access token using the refresh cookie. |

### Quiz Management

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/createQuiz/` | Generate a new quiz from a YouTube URL. |
| `GET` | `/api/quizzes/` | List all quizzes created by the authenticated user. |
| `GET` | `/api/quizzes/<id>/` | Retrieve details of a specific quiz. |
| `PATCH` | `/api/quizzes/<id>/` | Partially update a quiz (e.g., title). |
| `DELETE` | `/api/quizzes/<id>/` | Permanently delete a quiz. |