# 🌍 In-The-Life — Cognitive Geo-Intelligence System

> Event-driven, AI-augmented geographic knowledge management with D3.js Treemap, World Band Grid Navigation, semantic search via pgvector and NATS JetStream.

[![CI/CD](https://github.com/vanVaust/in-the-life/actions/workflows/ci.yml/badge.svg)](https://github.com/vanVaust/in-the-life/actions)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- **World Band Grid** — 3×3 global zone matrix for intuitive navigation
- **Geo Hierarchy** — World → Continent → Country → Region → Locality (PostGIS)
- **D3.js Treemap** — proportional visualization with click-to-drill-down
- **Knowledge Management** — versioned entries, audit trail, stability scoring
- **Semantic Search** — hybrid BM25 + pgvector (384-dim MiniLM embeddings)
- **Event-Driven** — NATS JetStream for async embedding & cache invalidation
- **Production Ready** — Docker, Kubernetes, Prometheus, Grafana, GitHub Actions CI

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.111, SQLAlchemy 2.0, Pydantic v2, Alembic |
| Database | PostgreSQL 16, PostGIS 3.4, pgvector 0.7, pg_trgm |
| Messaging | NATS 2.10 JetStream |
| Cache | Redis 7.2 |
| Frontend | React 18, TypeScript 5, Vite 5, D3.js 7, Zustand, TanStack Query |
| Infra | Docker, Kubernetes 1.28, Traefik, Prometheus, Grafana |
| ML | sentence-transformers paraphrase-multilingual-MiniLM-L12-v2 |

## Quick Start

```bash
git clone https://github.com/vanVaust/in-the-life
cd in-the-life
cp .env.example .env        # fill in secrets
make up                     # start all services
make migrate                # run alembic migrations
make seed                   # seed geo data
# → API:      http://localhost:8000/docs
# → Frontend: http://localhost:3000
# → Grafana:  http://localhost:3000 (admin/see .env)
```

## Project Structure

```
in-the-life/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI routers
│   │   ├── core/            # config, database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # business logic
│   │   └── workers/         # NATS embedding worker
│   ├── alembic/             # migrations
│   ├── tests/               # pytest
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # axios clients
│   │   ├── components/      # React components
│   │   ├── pages/           # route pages
│   │   └── store/           # zustand
│   ├── package.json
│   └── Dockerfile
├── k8s/                     # Kubernetes manifests
├── monitoring/              # Prometheus + Grafana
├── scripts/                 # init_db.sql, healthcheck
├── .github/workflows/       # CI/CD
├── docker-compose.yml       # development
├── docker-compose.prod.yml  # production
└── Makefile                 # 25 targets
```

## Development Commands

```bash
make help          # all available targets
make up            # start dev stack
make test          # run all tests
make test-cov      # coverage report
make lint          # ruff + eslint
make migrate       # alembic upgrade head
make db-shell      # psql shell
make backup        # database backup
```

## API Endpoints

```
GET  /api/v1/geo/                        # list entities
GET  /api/v1/geo/{id}/children           # hierarchical children
GET  /api/v1/geo/world-bands/{row}/{col} # world band query
GET  /api/v1/treemap/{entity_id}         # treemap data
GET  /api/v1/knowledge/{container_id}    # knowledge entries
GET  /api/v1/search?q=...               # hybrid semantic search
GET  /health                            # health check
GET  /metrics                           # prometheus metrics
```

## License

MIT © 2026 vanVaust
