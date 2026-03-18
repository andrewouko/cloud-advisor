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

| Layer      | Technology                           |
|------------|--------------------------------------|
| Frontend   | Next.js 16, React 19, Tailwind CSS 4 |
| Backend    | FastAPI, Python 3.11, Pydantic v2    |
| AI         | Anthropic Claude (Haiku 4.5)         |
| Database   | PostgreSQL 16 (async via SQLAlchemy) |
| Cache      | Redis 7 (response cache + rate limit)|
| State      | React Query (client)                 |

## Project Structure

```
cloud-advisor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory + lifespan
│   │   ├── config.py            # Pydantic settings (DB, Redis, AI)
│   │   ├── exceptions.py        # Custom exception handlers
│   │   ├── routers/             # API route handlers
│   │   │   ├── query.py         # POST /api/query
│   │   │   ├── history.py       # GET/DELETE /api/history
│   │   │   └── health.py        # GET /api/health
│   │   ├── models/
│   │   │   └── conversation.py  # SQLAlchemy ORM model
│   │   ├── services/
│   │   │   ├── claude_service.py      # Anthropic SDK integration
│   │   │   ├── history_service.py     # PostgreSQL conversation store
│   │   │   ├── cache_service.py       # Redis caching + rate limiting
│   │   │   ├── validation_service.py  # AI response validation
│   │   │   └── database.py            # Async engine + session factory
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
└── docker-compose.yml           # Full stack: backend + frontend + postgres + redis
```

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended — runs everything with one command)
- Python 3.11+ (only needed for running without Docker)
- Node.js 22+ (only needed for running without Docker)
- An [Anthropic API key](https://console.anthropic.com/)

### Option 1: Docker Compose (recommended)

This is the simplest way to run the full stack. Docker Compose starts PostgreSQL, Redis, the backend, and the frontend in one command.

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set ANTHROPIC_API_KEY=<your-key>

docker compose up --build
```

| Service    | URL                        |
|------------|----------------------------|
| Frontend   | http://localhost:3000       |
| Backend    | http://localhost:8000       |
| API Docs   | http://localhost:8000/docs  |
| PostgreSQL | localhost:5432              |
| Redis      | localhost:6379              |

To stop everything: `docker compose down` (add `-v` to also remove database volumes).

To reclaim all Docker resources (containers, images, volumes, and build cache) after you're done:

```bash
docker compose down -v
docker system prune -af --volumes
```

> **Warning:** `docker system prune` removes **all** unused Docker resources on your machine, not just those from this project. If you have other Docker projects, use `docker compose down -v --rmi all` instead to only clean up CloudAdvisor resources.

### Option 2: Manual Setup

Run PostgreSQL and Redis yourself (e.g. via Homebrew, native install, or standalone Docker containers), then start the backend and frontend separately.

**Start the infrastructure services:**

```bash
# Using Docker for just the databases (if not installed natively)
docker run -d --name cloudadvisor-pg -p 5432:5432 \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=cloudadvisor \
  postgres:16-alpine

docker run -d --name cloudadvisor-redis -p 6379:6379 \
  redis:7-alpine
```

**Start the backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY, DATABASE_URL, and REDIS_URL
uvicorn app.main:app --reload
```

**Start the frontend:**

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

> **Note:** The backend runs in degraded mode if Redis is unavailable — caching and rate limiting are simply disabled. PostgreSQL is required for conversation history.

## AI Configuration

### Model Selection

CloudAdvisor uses **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) as its default model. Haiku was chosen for this use case because:

- **Low latency** — consulting responses feel conversational at ~1–2s, which matters for a chat-style UI
- **Cost efficiency** — significantly cheaper per token than Sonnet/Opus, making it practical for a demo with no auth/billing
- **Sufficient quality** — cloud/IT consulting responses are well within Haiku's capability; the structured system prompt compensates for the smaller model

The model is configurable via the `MODEL_NAME` environment variable, so switching to Sonnet or Opus requires no code change.

### Token Limit (`MAX_TOKENS=1024`)

Set to 1024 to keep responses focused and concise. Cloud consulting answers benefit from structured brevity — bullet points, tables, and step-by-step guides — rather than long-form prose. This also controls cost per request and keeps response times low. The system prompt reinforces this by instructing the model to use headings and bullet points.

### Temperature (`TEMPERATURE=0.7`)

Set to 0.7 as a balance between:

- **Factual accuracy** (lower temperature) — important for cloud architecture advice, migration steps, and security recommendations
- **Natural variation** (higher temperature) — avoids robotic, repetitive phrasing across similar questions

A temperature of 0.0 would produce deterministic but monotone answers. A temperature of 1.0 would risk hallucinated recommendations. 0.7 provides variety in phrasing while keeping technical content reliable.

### System Prompt

The system prompt (`backend/app/prompts/system_prompt.py`) establishes CloudAdvisor as a specialist in cloud technology and IT solutions with a focus on Google Cloud. It includes:

- A defined set of expertise areas (migration, security, GCP, Workspace, cost optimisation, etc.)
- Response formatting rules: headings (`##`), bullet points, comparison tables, estimated timelines
- Guardrails: acknowledge out-of-scope questions, avoid jargon, provide actionable guidance

### Response Validation

Before returning a response to the user, the `ValidationService` checks:

| Check              | What it catches                                          |
|--------------------|----------------------------------------------------------|
| Minimum length     | Empty or trivially short responses                       |
| Refusal detection  | Responses that say "I cannot help" instead of answering  |
| Domain relevance   | Responses that stray from cloud/IT topics                |
| Hallucinated URLs  | URLs to domains not in an approved whitelist              |
| Truncation         | Unclosed markdown code fences (incomplete output)        |

If validation fails, the query router retries the Claude API call up to 2 more times. If all attempts fail validation, the response is served anyway (a potentially imperfect answer is better than no answer).

## Data Architecture

### PostgreSQL — Conversation History

PostgreSQL stores all conversation history persistently, replacing the initial in-memory `OrderedDict` implementation.

**`conversations` table:**

| Column         | Type                     | Description                            |
|----------------|--------------------------|----------------------------------------|
| `id`           | `VARCHAR(36)` PK         | UUID generated per conversation        |
| `question`     | `TEXT`                   | The user's original question           |
| `answer`       | `TEXT`                   | Claude's markdown response             |
| `model`        | `VARCHAR(100)`           | Model ID that generated the response   |
| `input_tokens` | `INTEGER`                | Tokens consumed by the prompt          |
| `output_tokens`| `INTEGER`                | Tokens consumed by the response        |
| `timestamp`    | `TIMESTAMPTZ`            | When the conversation occurred (UTC)   |

Tables are auto-created on startup via SQLAlchemy's `create_all`. The async engine uses `asyncpg` for non-blocking database access that matches FastAPI's async request handling. The `DATABASE_URL` is automatically normalised at startup — if a provider (e.g. Railway) supplies `postgresql://`, it is rewritten to `postgresql+asyncpg://`.

**Why PostgreSQL over the in-memory store:**

- Conversations survive restarts and redeployments
- Token usage tracking enables cost monitoring
- Pagination queries are handled by the database, not Python
- Standard tooling for backups, monitoring, and scaling

### Redis — Response Cache and Rate Limiting

Redis serves two purposes:

**1. Response caching (1-hour TTL)**

Identical questions (normalised to lowercase, hashed with SHA-256) return cached responses instantly without calling the Claude API. This reduces API costs and improves latency for repeated questions.

| Key pattern                    | Value                | TTL    |
|--------------------------------|----------------------|--------|
| `cache:response:<hash16>`      | JSON: content, model, tokens | 1 hour |

**2. Per-IP rate limiting (20 requests / 60-second window)**

A sliding window counter per client IP prevents abuse and controls API spend. When the limit is exceeded, the API returns `429 Too Many Requests`.

| Key pattern              | Value         | TTL       |
|--------------------------|---------------|-----------|
| `ratelimit:<client_ip>`  | Request count | 60 seconds|

**Why Redis:**

- Sub-millisecond lookups for cache hits
- Built-in key expiry handles TTL without cleanup logic
- Atomic `INCR` + `EXPIRE` provides simple, race-condition-free rate limiting
- Graceful degradation — if Redis is unavailable, the app runs without caching or rate limiting

**Why both PostgreSQL and Redis (not just one):**

PostgreSQL and Redis solve different problems. PostgreSQL provides durable, queryable storage for conversation history — data that must survive restarts and support pagination. Redis provides ephemeral, high-speed storage for cache entries and rate limit counters — data that is disposable and time-bounded. Using Redis for history would lose data on restart; using PostgreSQL for rate limiting would add unnecessary latency to every request.

## API Endpoints

| Method   | Endpoint        | Description                                        |
|----------|-----------------|----------------------------------------------------|
| `POST`   | `/api/query`    | Submit a question, get AI response (cached if available) |
| `GET`    | `/api/history`  | Paginated conversation history                     |
| `DELETE` | `/api/history`  | Clear all history                                  |
| `GET`    | `/api/health`   | Health check (includes DB and Redis status)        |

### Example Request

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I migrate to Google Workspace?"}'
```

### Example Response

```json
{
  "id": "a1b2c3d4-...",
  "question": "How do I migrate to Google Workspace?",
  "answer": "## Migration Strategy\n\n...",
  "timestamp": "2026-03-18T10:30:00Z",
  "model": "claude-haiku-4-5-20251001",
  "tokens_used": 342,
  "cached": false
}
```

## Testing

### Backend

```bash
cd backend
pytest -v
```

Tests use mock services (no PostgreSQL or Redis required). The test suite includes:
- Query router tests (success, validation, error cases)
- History service tests (CRUD, pagination)
- Health endpoint tests
- Response validation service tests (13 cases covering all checks)

### Frontend

```bash
cd frontend
npm test
```

## Architecture Decisions

- **PostgreSQL for history**: Persistent, queryable conversation storage with token tracking. Replaces the initial in-memory `OrderedDict`.
- **Redis for cache + rate limiting**: Reduces API costs via response caching; protects budget via per-IP rate limiting. Gracefully degrades if unavailable.
- **Response validation**: Guards against empty, off-topic, or truncated AI responses with automatic retry.
- **No authentication**: Single-user scope for this assessment.
- **Standalone Next.js output**: Enables containerised deployment without `node_modules`.
- **React Query**: Handles server state, caching (30s stale time), and automatic refetching.
- **Factory pattern**: `create_app()` enables dependency injection for testing with mocked services.
- **DATABASE_URL normalisation**: Automatically rewrites `postgresql://` to `postgresql+asyncpg://` so Railway's provided URL works without manual editing.

## Deployment

The app is deployed with **Railway** (backend + PostgreSQL + Redis) and **Vercel** (frontend). Deployments are triggered manually via CLI (`railway up`, `vercel --prod`) — there is no automatic deploy on push to `main`. This is intentional: the backend interacts with paid APIs (Anthropic) and provisioned databases, so deployments should be deliberate rather than triggered by every commit.

Below are step-by-step instructions for a fresh deployment.

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

# Add PostgreSQL and Redis databases
railway add -d postgres
railway add -d redis

# Link database URLs to the backend service via reference variables
railway variables set 'DATABASE_URL=${{Postgres.DATABASE_URL}}' 'REDIS_URL=${{Redis.REDIS_URL}}'

# Set remaining environment variables
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

| Variable            | Description                     | Example                            |
|---------------------|---------------------------------|------------------------------------|
| `ANTHROPIC_API_KEY` | Anthropic API key               | `sk-ant-api03-...`                 |
| `MODEL_NAME`        | Claude model to use             | `claude-haiku-4-5-20251001`        |
| `MAX_TOKENS`        | Max response tokens             | `1024`                             |
| `TEMPERATURE`       | Sampling temperature            | `0.7`                              |
| `DATABASE_URL`      | PostgreSQL connection string    | Auto-injected by Railway           |
| `REDIS_URL`         | Redis connection string         | Auto-injected by Railway           |
| `ALLOWED_ORIGINS`   | CORS allowed origins            | `https://your-app.vercel.app`      |
| `DEBUG`             | Enable debug logging            | `false`                            |

**Frontend (Vercel)**

| Variable              | Description          | Example                                          |
|-----------------------|----------------------|--------------------------------------------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `https://your-project-production.up.railway.app`  |

## Potential Improvements

- **Authentication and authorisation** — Add user login (e.g. OAuth via Google) to support per-user history, usage quotas, and role-based access. Currently the app is single-user with no auth, which limits it to demo/internal use.
- **MCP integration for local data** — Integrate the [Model Context Protocol](https://modelcontextprotocol.io/) to let Claude access local knowledge bases, internal documentation, or company-specific infrastructure data. This would make CloudAdvisor context-aware for a specific organisation rather than providing only general advice.
- **Streaming responses** — Replace the current request/response cycle with Server-Sent Events (SSE) so the UI renders tokens as they arrive. This would significantly improve perceived latency, especially for longer answers.
- **Multi-turn conversations** — Currently each query is standalone with no memory of previous messages. Adding conversation context would allow follow-up questions like "Can you elaborate on step 3?" without restating the original topic.
- **Token usage dashboard** — The database already stores `input_tokens` and `output_tokens` per conversation. An admin view could surface cost trends, usage patterns, and budget alerts.
- **Conversation search** — Full-text search over conversation history using PostgreSQL's built-in `tsvector` indexing, allowing users to find past answers without scrolling through the history list.
- **File and document upload** — Allow users to upload architecture diagrams, configuration files, or cloud bills for Claude to analyse and provide tailored recommendations.