# Label Manager

Print ZPL labels to Zebra printers via a REST API. Built with FastAPI, PostgreSQL, and an Expo React Native frontend.

## Quick start

```sh
docker compose up -d
```

This starts three containers:

| Service | Port   | Purpose             |
| ------- | ------ | ------------------- |
| `app`   | `8000` | FastAPI backend     |
| `db`    | `5432` | PostgreSQL 17       |
| `demo`  | `5173` | Web frontend (Expo) |

The database is automatically initialized with sample printers, templates, and triggers.

Open the web UI at `http://localhost:5173` or use the API directly.

## API

| Method | Path                    | Description                      |
| ------ | ----------------------- | -------------------------------- |
| `GET`  | `/printers`             | List all printers                |
| `POST` | `/printers/{id}/print`  | Print a label (sync)             |
| `GET`  | `/printers/health`      | Real-time TCP connectivity check |
| `POST` | `/printers/batch/print` | Queue multiple labels (async)    |
| `GET`  | `/printers/jobs`        | List pending print jobs          |
| `GET`  | `/printers/jobs/{id}`   | Get job status                   |
| `GET`  | `/printers/templates`   | List label templates             |
| `POST` | `/printers/templates`   | Create a label template          |
| `POST` | `/webhook/print`        | ERP/webhook endpoint (async)     |
| `GET`  | `/health`               | Service health                   |

### Print a label (sync)

```sh
curl -X POST http://localhost:8000/printers/<id>/print \
  -H "Content-Type: application/json" \
  -d '{"text": "Caja 1 de 5", "qr_data": "ORD-12345", "copies": 2}'
```

| Field     | Type    | Default        | Description      |
| --------- | ------- | -------------- | ---------------- |
| `text`    | string  | `"Hola Mundo"` | Label text       |
| `qr_data` | string  | `null`         | QR code content  |
| `copies`  | integer | `1`            | Number of copies |

### Webhook (async — for ERP integration)

```sh
curl -X POST http://localhost:8000/webhook/print \
  -H "Content-Type: application/json" \
  -d '{"printer_id": "<id>", "text": "Pedido #123", "copies": 1}'
```

Returns a job ID. The print is processed in the background with automatic retries.

### Batch print

```sh
curl -X POST http://localhost:8000/printers/batch/print \
  -H "Content-Type: application/json" \
  -d '{"jobs": [{"printer_id": "<id>", "text": "Box 1"}, {"printer_id": "<id>", "text": "Box 2"}]}'
```

### Health check

```sh
curl http://localhost:8000/printers/health
```

Returns online status per printer via real TCP connection (timeout: 5s):

```json
[
  {
    "printer_id": "a1b2c3d4-...",
    "name": "Almacen Principal",
    "ip_address": "192.168.1.100",
    "port": 9100,
    "is_online": true,
    "latency_ms": 4.2
  }
]
```

### Label templates

```sh
# List templates
curl http://localhost:8000/printers/templates

# Create a template
curl -X POST http://localhost:8000/printers/templates \
  -H "Content-Type: application/json" \
  -d '{"name": "shipping", "content_template": "Order {{order_id}} - {{customer}}"}'
```

Templates use `{{variable}}` placeholders that are resolved at print time.

### Print queue

```sh
# Pending jobs
curl http://localhost:8000/printers/jobs

# Job status
curl http://localhost:8000/printers/jobs/<job_id>
```

## Automation features

- **Webhook endpoint** — External systems (ERP, Odoo, SAP) push print jobs
- **Batch printing** — Print hundreds of labels from a single request
- **Print queue** — Jobs are queued in PostgreSQL and processed asynchronously
- **Auto-retry** — Failed jobs retry up to 3 times; exhausted jobs are marked `failed`
- **LISTEN/NOTIFY** — PostgreSQL triggers wake up the worker on new jobs instantly
- **Label templates** — Reusable templates with `{{variable}}` substitution

## Environment variables

Create a `.env` file (a `.env.example` is provided):

| Variable            | Required    | Default | Description                  |
| ------------------- | ----------- | ------- | ---------------------------- |
| `postgres_dsn`      | Yes         | —       | PostgreSQL connection string |
| `postgres_user`     | Docker only | —       | DB user                      |
| `postgres_password` | Docker only | —       | DB password                  |
| `postgres_db`       | Docker only | —       | DB name                      |

The default `docker-compose.yml` configures all variables automatically.

## Development

```sh
# Backend
poetry install
poetry run uvicorn label_manager.main:app --reload

# Tests
poetry run pytest

# Frontend
cd frontend && npm install && npm start
```

## Architecture

```text
src/label_manager/
├── main.py                      # FastAPI entrypoint + background queue worker
├── api/                         # Routes, schemas, DI
├── application/                 # Use cases, label builder, template engine
├── domain/                      # Entities, repository & service interfaces
└── infrastructure/              # PostgreSQL, Zebra TCP, settings
```

Uses Clean Architecture with dependency inversion via FastAPI's `Depends`.

## Database

The schema is defined in `db/init.sql`. Tables:

- `Printer` — Registered printers
- `print_job` — Queued/processed print jobs (with retry tracking)
- `label_template` — Reusable label templates with `{{var}}` placeholders

## Tech stack

- **Backend:** Python 3.13, FastAPI, asyncpg, pydantic-settings
- **Frontend:** Expo (React Native), React Navigation
- **Database:** PostgreSQL 17
- **Infrastructure:** Docker Compose

## License

MIT
