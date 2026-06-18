# AI-Powered Code Review Assistant

A full-stack application that enables developers to upload source code projects and receive structured AI-generated code reviews. This project demonstrates modern frontend development, backend architecture, databases, file processing, and AI integration.

## Features

- **Authentication**: Secure user registration, login, and protected routes using JWT.
- **Project Management**: Create, view, and delete projects (e.g., Portfolio Website, CRM Backend).
- **Code Upload**: Upload project files via ZIP files.
- **Code Explorer**: View uploaded files and their structure.
- **AI Review Engine**: Analyze single files, multiple files, or the entire project to get structured feedback (Summary, Issues, Recommendations) with severity levels.
- **Review Templates**: Support for Security Review, Performance Review, Code Quality Review, Architecture Analysis, and Documentation Generator.
- **Review History**: Keep track of previous AI reviews and view their details at any time.
- **AI Chat With Code**: Chat seamlessly with an AI assistant that has the context of the uploaded codebase.
- **Configurable AI Providers**: Use OpenAI, LM Studio, Ollama, OpenRouter, or any OpenAI-compatible endpoint. Switch models easily via the Settings page.

## Technologies Used

- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind CSS, Zustand, Framer Motion, Axios.
- **Backend**: FastAPI (Python), SQLAlchemy, Pydantic, Passlib, python-jose.
- **Database**: PostgreSQL (via psycopg2) with a fallback to SQLite for easy local development without installing PostgreSQL.
- **AI Integration**: OpenAI Python SDK used for OpenAI and locally hosted OpenAI-compatible endpoints.

## Setup Instructions

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL (Optional, fallback to SQLite is implemented out-of-the-box)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure Environment Variables:
   Create a `.env` file in the `backend` directory (optional):
   ```env
   DATABASE_URL=sqlite:///./sql_app.db
   SECRET_KEY=your_secret_key_here
   ```
   *(Note: The application will automatically create an SQLite DB if DATABASE_URL is not provided or points to SQLite.)*

5. Run the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:3000`.

## Architecture Overview

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed information on the frontend architecture, backend architecture, database schema, and AI integration flow.
