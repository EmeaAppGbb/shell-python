# spec2cloud shell — Python

AI-powered spec-driven development shell for building authenticated web applications on Azure. This shell implements a **UserAuth Basic** pattern using FastAPI (backend), Next.js (frontend), and Cosmos DB (data), deployed to Azure Container Apps via .NET Aspire orchestration.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   .NET Aspire AppHost                │
│                  (Dev Orchestrator)                   │
├──────────────────┬──────────────────┬────────────────┤
│                  │                  │                │
│   ┌──────────┐   │   ┌──────────┐   │  ┌──────────┐  │
│   │ FastAPI  │   │   │ Next.js  │   │  │ MkDocs   │  │
│   │ Backend  │◄──┼───│ Frontend │   │  │ Docs     │  │
│   │ :5000    │   │   │ :3001    │   │  │ :8000    │  │
│   └────┬─────┘   │   └──────────┘   │  └──────────┘  │
│        │         │                  │                │
│   ┌────▼─────┐   │                  │                │
│   │ Cosmos DB│   │                  │                │
│   │ (or mem) │   │                  │                │
│   └──────────┘   │                  │                │
└──────────────────┴──────────────────┴────────────────┘

Azure Deployment:
  ┌──────────────────────────────┐
  │  Azure Container Apps Env    │
  │  ┌────────┐   ┌────────┐    │
  │  │  API   │   │  Web   │    │
  │  │ (ACA)  │◄──│ (ACA)  │    │
  │  └───┬────┘   └────────┘    │
  │      │                      │
  │  ┌───▼──────────┐           │
  │  │  Cosmos DB    │           │
  │  │  (NoSQL)      │           │
  │  └───────────────┘           │
  └──────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url> && cd shell-python
cd src/api && pip install -e ".[dev]" && cd ../web && npm ci && cd ../..

# 2. Run with Aspire (orchestrates backend + frontend + docs)
dotnet run --project apphost.cs

# 3. Open browser
open http://localhost:3001
```

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start full stack via Aspire (API + Web + Docs) |
| `npm run dev:api` | Start FastAPI backend only (port 5000) |
| `npm run dev:web` | Start Next.js frontend only |
| `npm run build:all` | Build API and Web for production |
| `npm run test:api` | Run backend pytest suite |
| `npm run test:web` | Lint frontend code |
| `npm run test:bdd` | Run Behave BDD tests against API |
| `npm run test:e2e` | Run Playwright E2E tests |
| `npm run test:all` | Run all test suites |
| `npm run docs:serve` | Serve MkDocs documentation locally |

## Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | FastAPI + Uvicorn | REST API with JWT auth |
| Frontend | Next.js 15 (App Router) | Server-rendered React UI |
| Auth | JWT (HTTP-only cookies) + bcrypt | Stateless authentication |
| Database | Cosmos DB (in-memory for dev) | User data persistence |
| Orchestration | .NET Aspire | Local dev service orchestration |
| Infrastructure | Bicep + Azure Container Apps | Cloud deployment |
| E2E Tests | Playwright | Browser automation tests |
| BDD Tests | Behave + httpx | API-level behavior tests |
| API Tests | pytest + httpx | Unit/integration tests |

## Testing

### E2E Tests (Playwright)

Browser-based tests covering registration, login, logout, profile, admin, and landing page flows:

```bash
npm run test:e2e              # Run with Aspire auto-start
npx playwright test --ui      # Interactive mode (from e2e/)
```

### BDD Tests (Behave)

Gherkin feature files with step definitions hitting the FastAPI backend directly:

```bash
npm run test:bdd              # Run all BDD scenarios
cd tests && behave --tags=@auth  # Run tagged scenarios
```

### API Unit Tests

```bash
npm run test:api              # Run pytest suite
cd src/api && pytest -v       # Verbose output
```

## Documentation

- **[docs/](./docs/)** — Project documentation (architecture, concepts, quickstart)
- **[specs/](./specs/)** — Specifications, contracts, and feature files
- **[AGENTS.md](./AGENTS.md)** — spec2cloud orchestrator instructions and skills catalog

## spec2cloud

This shell is built with the [spec2cloud](./AGENTS.md) orchestrator — an AI-powered workflow that transforms specifications into deployed cloud applications. See `AGENTS.md` for the full skills catalog and automation patterns.
