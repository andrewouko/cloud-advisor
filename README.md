# CloudAdvisor

AI-powered cloud technology and IT consulting assistant built with FastAPI, Next.js, and Claude AI.

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | Next.js 16, React 19, Tailwind CSS 4 |
| Backend   | FastAPI, Python 3.11, Pydantic v2   |
| AI        | Anthropic Claude (Haiku 4.5)        |
| State     | React Query (client), in-memory (server) |

## Project Structure

```
cloud-advisor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory
│   │   ├── config.py            # Pydantic settings
│   │   ├── exceptions.py        # Custom exception handlers
│   │   ├── routers/             # API route handlers
│   │   │   ├── query.py         # POST /api/query
│   │   │   ├── history.py       # GET/DELETE /api/history
│   │   │   └── health.py        # GET /api/health
│   │   ├── services/
│   │   │   ├── claude_service.py # Anthropic SDK integration
│   │   │   └── history_service.py # In-memory conversation store
│   │   ├── schemas/             # Request/response models
│   │   └── prompts/             # System prompt configuration
│   ├── tests/                   # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js App Router
│   ├── components/
│   │   ├── chat/                # ChatWindow, ChatMessage, ChatInput
│   │   ├── history/             # HistorySidebar, HistoryItem
│   │   ├── layout/              # Header
│   │   └── ui/                  # EmptyState, ErrorBanner, Shimmer
│   ├── hooks/                   # useChat, useHistory
│   ├── lib/                     # API client, utilities
│   ├── types/                   # TypeScript interfaces
│   └── Dockerfile
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 22+
- Anthropic API key

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs at `http://localhost:3000`.

### Docker (recommended)

```bash
cp backend/.env.example backend/.env
# Add your ANTHROPIC_API_KEY to backend/.env
docker compose up --build
```

Frontend: `http://localhost:3000` | Backend: `http://localhost:8000`

## API Endpoints

| Method   | Endpoint        | Description                        |
|----------|-----------------|------------------------------------|
| `POST`   | `/api/query`    | Submit a question, get AI response |
| `GET`    | `/api/history`  | Paginated conversation history     |
| `DELETE` | `/api/history`  | Clear all history                  |
| `GET`    | `/api/health`   | Health check                       |

### Example Request

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I migrate to Google Workspace?"}'
```

## Testing

### Backend

```bash
cd backend
pytest -v
```

### Frontend

```bash
cd frontend
npm test
```

## Architecture Decisions

- **In-memory history**: OrderedDict with LRU eviction (max 100 items). Suitable for demo; production would use PostgreSQL/Redis.
- **No authentication**: Single-user scope for this assessment.
- **Standalone Next.js output**: Enables containerised deployment without `node_modules`.
- **React Query**: Handles server state, caching (30s stale time), and automatic refetching.
- **Factory pattern**: `create_app()` enables dependency injection for testing with mocked Claude service.

## Deployment

- **Frontend**: Vercel (see `frontend/vercel.json`)
- **Backend**: Railway (see `backend/railway.json`)