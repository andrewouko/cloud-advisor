# CloudAdvisor

AI-powered cloud technology and IT consulting assistant built with FastAPI, Next.js, and Claude AI.

## Live Demo

| Service  | URL                                                                  |
|----------|----------------------------------------------------------------------|
| Frontend | https://frontend-lemon-two-26.vercel.app                             |
| Backend  | https://sparkling-contentment-production.up.railway.app              |
| API Docs | https://sparkling-contentment-production.up.railway.app/docs         |
| Health   | https://sparkling-contentment-production.up.railway.app/api/health   |

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

The app is deployed with **Railway** (backend) and **Vercel** (frontend). Below are step-by-step instructions for a fresh deployment.

### Prerequisites

- [Railway CLI](https://docs.railway.com/guides/cli) installed and authenticated (`railway login`)
- [Vercel CLI](https://vercel.com/docs/cli) installed and authenticated (`vercel login`)
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Deploy the Backend (Railway)

```bash
cd backend

# Initialize a new Railway project
railway init

# Deploy the service (creates the service automatically)
railway up --detach

# Link the newly created service
railway service <service-name>

# Set environment variables
railway variables set ANTHROPIC_API_KEY=<your-api-key>
railway variables set MODEL_NAME=claude-haiku-4-5-20251001
railway variables set MAX_TOKENS=1024
railway variables set TEMPERATURE=0.7
railway variables set DEBUG=false

# Generate a public domain
railway domain
```

Note the Railway domain URL (e.g. `https://<project>-production.up.railway.app`). Verify the backend is running:

```bash
curl https://<your-railway-domain>/api/health
```

### 2. Deploy the Frontend (Vercel)

```bash
cd frontend

# Deploy to production (follow the prompts to create a new project)
vercel --prod

# Set the backend URL as an environment variable
echo "https://<your-railway-domain>" | vercel env add NEXT_PUBLIC_API_URL production

# Redeploy so the frontend picks up the new env var
vercel --prod
```

Note the Vercel production URL from the output.

### 3. Configure CORS

Update Railway to allow requests from the Vercel frontend:

```bash
cd backend
railway variables set ALLOWED_ORIGINS=https://<your-vercel-domain>
```

Railway will automatically redeploy with the new variable.

### 4. Verify

- Open the Vercel frontend URL in your browser
- Ask a question to confirm the backend responds
- Check the health endpoint: `https://<your-railway-domain>/api/health`

### Environment Variables Reference

**Backend (Railway)**

| Variable          | Description                     | Example                            |
|-------------------|---------------------------------|------------------------------------|
| `ANTHROPIC_API_KEY` | Anthropic API key             | `sk-ant-api03-...`                 |
| `MODEL_NAME`      | Claude model to use             | `claude-haiku-4-5-20251001`        |
| `MAX_TOKENS`      | Max response tokens             | `1024`                             |
| `TEMPERATURE`     | Sampling temperature            | `0.7`                              |
| `ALLOWED_ORIGINS` | CORS allowed origins            | `https://your-app.vercel.app`      |
| `DEBUG`           | Enable debug logging            | `false`                            |

**Frontend (Vercel)**

| Variable              | Description          | Example                                          |
|-----------------------|----------------------|--------------------------------------------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://your-project-production.up.railway.app`  |