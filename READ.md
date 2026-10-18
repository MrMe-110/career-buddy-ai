
# Career Buddy AI — ResumeAI

An AI-powered career assistant that helps users create, improve, and manage resumes using natural language.

## Features

- AI career assistance and conversational chat
- AI-powered resume generation
- Resume-aware conversation context using LangChain
- Download resumes as Microsoft Word documents
- User authentication using Supabase
- Save and manage resumes
- Store chat history in Supabase PostgreSQL
- Groq language models for AI responses
- Streamlit web interface

## Technology Stack

- Python
- Streamlit
- LangChain
- Groq API
- Supabase PostgreSQL
- Python-DOCX
- Python Dotenv

## Project Structure

ResumeAI/
- app.py
- ai_chain.py
- database.py
- memory_service.py
- resume_generator.py
- requirements.txt
- .gitignore
- README.md
- .streamlit/
  - config.toml

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ResumeAI
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual repository URL.

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
```

Replace the example values with your own credentials.

Never commit your `.env` file to GitHub.

### 4. Run the application

```bash
streamlit run app.py
```

## Database

The application uses Supabase PostgreSQL.

Expected tables:

### resumes

- id
- user_id
- title
- content
- created_at
- updated_at

### chat_messages

- id
- user_id
- session_id
- role
- content
- created_at

The tables must exist in Supabase before using the application.

## Security

- Keep API keys and credentials private.
- Use appropriate Supabase Row Level Security policies.
- Restrict resume and chat access to the authenticated user.
- Never expose a Supabase service-role key in client-facing configuration.

## Future Improvements

- Job description and resume matching
- Resume keyword analysis
- Resume scoring and improvement suggestions
- PDF resume export
- Interview preparation

## Author

AI and Machine Learning Project
