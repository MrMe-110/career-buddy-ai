# Career Buddy AI — ResumeAI

An AI-powered career assistant built with Streamlit that helps users create, improve, and manage resumes through natural-language conversations. The application combines Groq language models with LangChain and Supabase to provide AI-powered career guidance, resume generation, and saved conversation history.

## Features

- **AI Career Assistant:** Get career guidance and answers through conversational chat.
- **AI Resume Generation:** Generate resumes using natural-language instructions.
- **Resume-Aware Conversations:** Use saved resume information as context for relevant follow-up questions.
- **Word Document Export:** Download generated resumes in Microsoft Word format.
- **User Authentication:** Sign up and log in using Supabase authentication.
- **Resume Management:** Save and retrieve resumes associated with the authenticated user.
- **Chat History:** Store and retrieve conversations using Supabase PostgreSQL.
- **LLM Integration:** Generate AI responses using Groq language models through LangChain.
- **Interactive Web Interface:** Access the application through a Streamlit interface.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Web interface |
| LangChain | LLM integration and prompt management |
| Groq API | Language model inference |
| Supabase | Authentication and PostgreSQL database |
| python-docx | Generate downloadable Word documents |
| python-dotenv | Load environment variables locally |

## Project Structure

```text
career-buddy-ai/
├── app.py
├── ai_chain.py
├── database.py
├── memory_service.py
├── resume_generator.py
├── requirements.txt
├── .gitignore
├── README.md
├── .streamlit/
│   └── config.toml
└── components/
    ├── __init__.py
    ├── auth.py
    ├── chat_ui.py
    ├── sidebar.py
    └── styles.py
```

## Installation and Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/MrMe-110/career-buddy-ai.git
cd career-buddy-ai
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
COOKIE_PASSWORD=your_cookie_password
```

Replace the example values with your actual credentials. Use a strong, private value for `COOKIE_PASSWORD`.

**Security:** Never upload `.env`, API keys, database credentials, or other secrets to GitHub. For deployment, configure these values using your hosting provider's secrets settings.

### 5. Configure Supabase

Create a Supabase project and configure authentication. Ensure the database contains the required tables and appropriate access policies.

#### `resumes`

Expected columns:

- `id`
- `user_id`
- `title`
- `content`
- `created_at`
- `updated_at`

#### `chat_messages`

Expected columns:

- `id`
- `user_id`
- `session_id`
- `role`
- `content`
- `created_at`

The column types, constraints, and access policies must match the application's database operations. Apply appropriate Row Level Security (RLS) policies to protect user data.

### 6. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal.

## Deployment

The application can be deployed using Streamlit Community Cloud.

1. Push the project to GitHub.
2. Connect the repository to Streamlit Community Cloud.
3. Set the main application file to `app.py`.
4. Add the required environment variables through Streamlit's Secrets settings.
5. Configure the Supabase authentication redirect URLs to include your deployed application URL.
6. Test registration, login, resume generation, resume retrieval, and chat history.

Keep all credentials out of the GitHub repository.

## Security and Privacy

- Keep API keys and authentication credentials private.
- Apply appropriate Supabase Row Level Security policies.
- Ensure users can access only their own resumes and chat history.
- Never expose the Supabase service-role key in client-facing configuration.
- Configure authentication redirect URLs for the correct deployment environment.

## Future Improvements

- Job description and resume matching
- Resume keyword analysis and ATS-oriented suggestions
- Resume scoring and improvement recommendations
- PDF resume export
- Interview preparation and practice
- Job-specific resume customization

## Author

AI and Machine Learning Developer

**GitHub:** https://github.com/MrMe-110

---

*Career Buddy AI is a learning and development project focused on AI-powered career assistance and resume management.*