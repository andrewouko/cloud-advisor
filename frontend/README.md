# CloudAdvisor Frontend

Next.js 16 frontend for CloudAdvisor — an AI-powered cloud consulting chat interface.

## Tech Stack

- **Framework**: Next.js 16 (App Router, Turbopack)
- **UI**: React 19, Tailwind CSS 4, `@tailwindcss/typography`
- **State**: TanStack React Query v5 (server state, caching, refetching)
- **Markdown**: `react-markdown` with `react-syntax-highlighter` for code blocks
- **Testing**: Vitest, React Testing Library, jsdom
- **Linting**: ESLint with `eslint-config-next`

## Project Structure

```
frontend/
├── app/                    # Next.js App Router (layout, page, global styles)
├── components/
│   ├── chat/               # ChatWindow, ChatMessage, ChatInput, TypingIndicator
│   ├── history/            # HistorySidebar, HistoryItem
│   ├── layout/             # Header
│   └── ui/                 # EmptyState, ErrorBanner, Shimmer
├── hooks/
│   ├── useChat.ts          # Chat submission, streaming, query management
│   └── useHistory.ts       # Conversation history CRUD
├── lib/
│   ├── api.ts              # Backend API client
│   ├── providers.tsx       # React Query provider setup
│   └── utils.ts            # Shared utilities
├── types/
│   └── index.ts            # TypeScript interfaces
├── tests/                  # Vitest test suite
├── vercel.json             # Vercel deployment config
└── Dockerfile              # Container build for Docker Compose
```

## Getting Started

### Prerequisites

- Node.js 22+
- Backend running at `http://localhost:8000` (see [backend README](../backend/))

### Development

```bash
npm install
cp .env.example .env.local
npm run dev
```

Runs at `http://localhost:3000`.

### Environment Variables

| Variable              | Description          | Default                  |
|-----------------------|----------------------|--------------------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000`  |

## Scripts

| Command          | Description                  |
|------------------|------------------------------|
| `npm run dev`    | Start dev server (Turbopack) |
| `npm run build`  | Production build             |
| `npm start`      | Serve production build       |
| `npm run lint`   | Run ESLint                   |
| `npm test`       | Run tests (single run)       |
| `npm run test:watch` | Run tests in watch mode  |

## Deployment

Deployed to **Vercel**. See the [deployment guide](../README.md#deployment) in the root README.