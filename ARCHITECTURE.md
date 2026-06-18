# Architecture Document

## 1. Frontend Architecture
The frontend is built using **Next.js 16 (App Router)** and **TypeScript**. 
- **Routing**: Client-side routing with Next.js App Router for simplified file-based routing. Protected routes redirect to login if the `token` is missing.
- **State Management**: **Zustand** is utilized to maintain global state, specifically the user session (`user`, `token`).
- **Styling**: **Tailwind CSS** handles the styling, ensuring responsive, modern UI design.
- **Components**: The UI is broken into reusable components (`Navbar`, `RunReview`, `Chat`, `History`).
- **API Communication**: **Axios** is configured with an interceptor to automatically attach the JWT token to every request.

## 2. Backend Architecture
The backend is built with **FastAPI** to provide high-performance asynchronous API endpoints.
- **Structure**: The app is divided into modular routers:
  - `auth_router.py`: Handles JWT generation, registration, and login.
  - `project_router.py`: Manages project creation, ZIP uploads, and file extraction.
  - `review_router.py`: Initiates code reviews by forwarding code contexts to the AI module.
  - `chat_router.py`: Manages contextual chats using codebase files as context.
  - `provider_router.py`: Manages the user's AI configurations.
- **AI Module**: A dedicated `ai.py` file centralizes all logic for communicating with OpenAI-compatible APIs asynchronously.

## 3. Database Design
The application uses **SQLAlchemy** (ORM) to handle database interactions. It supports PostgreSQL (preferred) and defaults to SQLite if the `DATABASE_URL` is omitted.

### Schema:
- **Users**: Stores `email` and `hashed_password`.
- **Projects**: Links to `Users`. Contains `name`, `description`, `creation_date`.
- **Files**: Links to `Projects`. Stores `file_path` and raw `content`.
- **AI Providers**: Links to `Users`. Stores `base_url`, `api_key`, `model_name`, `is_default`.
- **Reviews**: Links to `Projects`. Stores `review_type`, `target_files` (JSON array), `summary`, `issues` (JSON), and `recommendations` (JSON).
- **Chat Sessions**: Links to `Projects`. Tracks independent chat threads.
- **Messages**: Links to `Chat Sessions`. Stores `role` (user/assistant) and `content`.

## 4. AI Integration Flow
1. **Configuration**: The user specifies an AI provider URL, model name, and optionally an API key via the settings page.
2. **Review Generation Flow**:
   - The frontend requests a review for specific files or the entire project.
   - The backend gathers the requested files from the DB and concatenates them into a formatted code context.
   - The backend retrieves the user's default `AI Provider` configuration and instantiates an `AsyncOpenAI` client pointing to the user's base URL.
   - The AI is prompted with a strictly defined JSON schema to return issues (with severity) and recommendations.
   - The JSON response is parsed, stored in the DB as a review entity, and returned to the frontend.
3. **Chat Context Flow**:
   - The entire codebase is fetched from the DB.
   - The backend feeds the previous conversation history and the complete code context as a system prompt to the configured AI provider.
   - The assistant's reply is returned synchronously (via async execution) to the frontend to build a continuous chat.
