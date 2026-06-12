# AGENTS.md — label-manager

FastAPI app for managing printers and printing ZPL labels via Zebra printers. Uses Poetry, asyncpg, PostgreSQL.

## Commands

```sh
poetry install                          # install deps (Python >=3.13)
poetry run uvicorn label_manager.main:app --reload

# Tests
poetry run pytest                       # runs 13 tests (8 unit + 5 integration)

# Frontend (Expo React Native)
cd frontend && npm install && npm start

# Docker
docker compose up -d                    # build & start app + db + frontend
docker compose up -d --build
docker compose down
docker compose logs -f
```

## Architecture

```text
src/label_manager/
├── main.py                            # FastAPI entrypoint + lifespan (db connect/disconnect)
├── api/
│   ├── dependencies.py                # DI chain: db → repo → use case
│   ├── routers/printers.py            # GET /printers, POST /printers/{id}/print
│   └── schemas/printer.py             # PrinterResponse, PrintLabelResponse
├── application/
│   ├── services/label_builder.py      # builds ZPL string from constants
│   └── use_cases/                     # get_printers, print_label
├── domain/
│   ├── entities/printer.py            # Printer dataclass
│   ├── repositories/printer_repository.py  # ABC interface (get_all, get_by_id)
│   └── services/printer_service.py    # ABC interface (print)
└── infrastructure/
    ├── constants.py                   # ZPL_LABEL template
    ├── settings.py                    # pydantic-settings from .env
    ├── data/
    │   ├── base.py + postgres.py      # asyncpg pool
    │   └── repositories/postgres_printer_repository.py  # implements PrinterRepository
    └── services/zebra_printer_service.py  # async TCP socket via asyncio

frontend/                               # Expo React Native app
├── App.tsx                             # entry + stack navigator
├── src/api/labelManager.ts             # fetch wrapper → backend API
└── src/screens/
    ├── PrinterListScreen.tsx           # list & select printers
    └── PrintLabelScreen.tsx            # print label with status feedback

tests/
├── conftest.py                         # shared fixtures (mock repo, service, printer)
├── unit/                               # 8 tests (label builder, use cases)
└── integration/                        # 5 tests (API via httpx ASGITransport)
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/printers` | List all printers |
| POST | `/printers/{printer_id}/print` | Send ZPL label to a printer |

## Quirks & gotchas

- **Imports use `src.label_manager.` prefix** (e.g., `from src.label_manager.domain...`). Do not use relative imports.
- **Required env vars**: `postgres_dsn`, `postgres_user`, `postgres_password`, `postgres_db`. Loaded from `.env` via pydantic-settings.
- **Live credentials in `.env`** — committed to git (security concern).
- **`PostgresDatabase` pool** — created in `lifespan` handler, stored in `app.state.db`. Use `get_database()` dependency to inject.
- **`ZebraPrinterService`** — uses `asyncio.open_connection` (raw TCP, no TLS).
- **Integration tests** — mock lifespan + override dependencies via `httpx.ASGITransport` (no real DB needed).
- **Frontend `EXPO_PUBLIC_API_URL`** — defaults to `http://10.0.2.2:8000` (Android emulator localhost).
