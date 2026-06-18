# AGENTS.md — label-manager

FastAPI app for managing printers and printing ZPL labels via Zebra printers. Uses Poetry, asyncpg, PostgreSQL.

## Commands

```sh
poetry install                          # install deps (Python >=3.13)
poetry run uvicorn label_manager.main:app --reload

# Tests
poetry run pytest                       # runs 37 tests (23 unit + 14 integration)

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
├── main.py                            # FastAPI entrypoint + lifespan (db connect/disconnect, background queue worker)
├── api/
│   ├── dependencies.py                # DI chain: db → repo → use case
│   ├── routers/printers.py            # all REST endpoints
│   └── schemas/printer.py             # request/response models
├── application/
│   ├── services/
│   │   ├── label_builder.py           # builds dynamic ZPL (text, QR, copies)
│   │   └── template_engine.py         # resolves {{var}} in label templates
│   └── use_cases/                     # get_printers, print_label, check_printers_health,
│                                      # webhook_print, batch_print, process_print_queue
├── domain/
│   ├── entities/
│   │   ├── printer.py                 # Printer dataclass
│   │   ├── print_job.py               # PrintJob dataclass
│   │   └── label_template.py          # LabelTemplate dataclass
│   ├── repositories/
│   │   ├── printer_repository.py      # ABC (get_all, get_by_id)
│   │   ├── print_job_repository.py    # ABC (create, get_pending, update_status, increment_retry)
│   │   └── label_template_repository.py  # ABC (get_all, get_by_id, get_by_name, create)
│   └── services/
│       └── printer_service.py         # ABC (print, check_health)
└── infrastructure/
    ├── constants.py                   # ZPL_TEMPLATE
    ├── settings.py                    # pydantic-settings from .env
    ├── data/
    │   ├── base.py + postgres.py      # asyncpg pool
    │   └── repositories/             # PostgresPrinterRepository, PostgresPrintJobRepository, PostgresLabelTemplateRepository
    └── services/zebra_printer_service.py  # async TCP socket via asyncio

frontend/                              # Expo React Native app
├── App.tsx                            # entry + stack navigator
├── src/api/labelManager.ts            # fetch wrapper → backend API
└── src/screens/
    ├── PrinterListScreen.tsx          # list & select printers (health check per printer)
    └── PrintLabelScreen.tsx           # print label with text/QR/copies inputs + status feedback

tests/
├── conftest.py                        # shared fixtures
├── unit/                              # 23 tests (label builder, template engine, use cases)
└── integration/                       # 14 tests (API via httpx ASGITransport)
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/printers` | List all printers |
| POST | `/printers/{printer_id}/print` | Print a label directly (sync) |
| GET | `/printers/health` | Real-time TCP connectivity for every printer |
| POST | `/printers/batch/print` | Queue multiple labels for printing (async) |
| GET | `/printers/jobs` | List pending print jobs |
| GET | `/printers/jobs/{job_id}` | Get job status |
| GET | `/printers/templates` | List label templates |
| POST | `/printers/templates` | Create a label template |
| POST | `/webhook/print` | ERP/webhook endpoint — queues a print job |
| GET | `/health` | Service health |

### Print a label (sync)
```json
POST /printers/{id}/print
{"text": "Caja 1", "qr_data": "ORD-123", "copies": 2}
```

### Webhook (async, queued)
```json
POST /webhook/print
{"printer_id": "...", "text": "Pedido #123", "variables": {"order": "123"}}
```

### Batch print (async, queued)
```json
POST /printers/batch/print
{"jobs": [{"printer_id": "...", "text": "Box 1"}, {"printer_id": "...", "text": "Box 2"}]}
```

### Templates
```json
POST /printers/templates
{"name": "shipping", "content_template": "Order {{order_id}} - {{customer}}"}
```

## Print queue & retry

- Jobs created via webhook/batch get `status: pending`
- Background worker (`process_print_queue_use_case`) polls for pending jobs every 3s
- On print failure: increments `retry_count`. After 3 failures, marks as `failed`
- Uses PostgreSQL `LISTEN/NOTIFY` for instant wake-up on new jobs

## DB tables

| Table | Purpose |
|---|---|
| `Printer` | Registered printers |
| `print_job` | Queued/processed print jobs |
| `label_template` | Reusable label templates with `{{var}}` placeholders |

## Quirks & gotchas

- **Imports use `src.label_manager.` prefix**. Do not use relative imports.
- **Required env vars**: `postgres_dsn`, `postgres_user`, `postgres_password`, `postgres_db`. Loaded from `.env` via pydantic-settings.
- **`PostgresDatabase` pool** — created in `lifespan` handler, stored in `app.state.db`.
- **`ZebraPrinterService`** — uses `asyncio.open_connection` (raw TCP, no TLS).
- **Background queue worker** — started in `lifespan`, uses a dedicated DB connection for `LISTEN/NOTIFY`.
- **Integration tests** — mock lifespan + override all dependencies via `httpx.ASGITransport`.
- **Frontend `EXPO_PUBLIC_API_URL`** — defaults to `http://10.0.2.2:8000` (Android emulator localhost).
