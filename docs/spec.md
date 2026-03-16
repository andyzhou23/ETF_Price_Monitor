# ETF Price Monitor Spec

## 1. Project Overview

A single-page web application that allows traders to view historical prices for a given ETF and its top holdings. Users upload a CSV file containing ETF constituent weights, and the app displays an interactive table of constituents, a zoomable time series chart of the reconstructed ETF price, and a bar chart of the top 5 holdings.

### Tech Stack

| Layer     | Technology                |
|-----------|---------------------------|
| Frontend  | React (Vite + TypeScript) |
| Backend   | Python FastAPI             |
| Database  | SQLite                     |
| Cache     | Redis                      |
| Deploy    | Docker Compose (local)     |

### Input Data

**Static (bundled with the application):**

| File | Description | Format |
|------|-------------|--------|
| `data/prices.csv` | Historical closing prices for 26 constituents (A–Z), 100 trading days (2017-01-01 to 2017-04-10) | Columns: `DATE`, then one column per constituent ticker |

This file is pre-loaded into the SQLite database at backend startup.

**User-uploaded (via the frontend):**

ETF definition CSVs are uploaded at runtime through the web UI. Each file must follow this schema:

| Column | Type   | Description                              |
|--------|--------|------------------------------------------|
| `name` | string | Constituent ticker (must exist in prices) |
| `weight` | float | Weight of the constituent in the ETF      |

Sample files (`ETF1.csv`, `ETF2.csv`) are provided in `data/` for reference only.

### Assumptions

- Constituent weights are static (do not change over time).
- The prices CSV is pre-loaded into the database at startup.
- ETF price at time _t_ = sum of (weight_i * price_i(t)) for all constituents.
- All 26 constituents share the same 100 trading dates (no missing data).
- Constituent tickers are single uppercase letters A–Z.
- No authentication is required.

---

## 2. Features

### F1 — CSV Upload

- User uploads an ETF definition CSV (any file following the `name,weight` schema) via a file input.
- Backend parses the CSV (columns: `name`, `weight`), validates that all constituent names exist in the database, and stores the ETF definition.
- The ETF id is a SHA-256 hash (truncated to 16 hex chars) of the sorted `name:weight` pairs. Uploading the same constituents with the same weights returns the existing ETF (idempotent).
- On success, the frontend receives the ETF id and refreshes all views.

### F2 — Constituents Table

- Interactive, sortable table with three columns:
  - **Constituent** — ticker symbol (e.g. `A`)
  - **Weight** — decimal weight from the uploaded CSV (e.g. `0.02`)
  - **Latest Close Price** — most recent closing price from the database (e.g. `$20.05`)

### F3 — ETF Price Time Series

- Zoomable line chart showing the reconstructed ETF price over the full date range.
- ETF price = weighted sum of constituent prices per date.
- Supports pan and zoom (e.g. via Recharts brush or Plotly rangeslider).

### F4 — Top 5 Holdings Bar Chart

- Bar chart of the 5 largest holdings as of the latest market close.
- Holding value = weight * latest close price.
- Bars labeled with constituent name and value.

---

## 3. Architecture

### System Components

The application follows a three-tier architecture deployed as three Docker containers managed by Docker Compose.

**Frontend (React SPA, port 5173)** — A single-page React application built with Vite and TypeScript, served via nginx in production. It communicates with the backend exclusively over HTTP/JSON REST calls. All rendering, charting, and user interaction happen client-side.

**Backend (FastAPI, port 8000)** — A Python FastAPI server responsible for CSV parsing, data validation, ETF price computation, and serving all API endpoints. It connects to both SQLite for persistent storage and Redis for caching. CORS is configured to allow requests from the frontend origin.

**SQLite (file-based)** — Stores constituent price history (seeded from the prices CSV at startup) and ETF definitions (constituent weights, persisted on upload). The database file is persisted via a Docker volume mount so data survives container restarts.

**Redis (port 6379)** — Caches precomputed ETF results (constituent tables, price history, top holdings) keyed by the ETF's content hash. On upload, the backend computes all results and caches them. GET endpoints serve from Redis when available; on cache miss, results are recomputed from the ETF definitions stored in SQLite.

### Data Flow

1. **Startup** — The backend reads the bundled `prices.csv` and seeds the `constituent_prices` table in SQLite (skipped if already populated). This loads 100 daily prices for 26 constituents (A–Z) spanning 2017-01-01 to 2017-04-10.
2. **Upload** — The user selects an ETF CSV file in the frontend. The frontend POSTs it to `/api/etfs/upload`. The backend parses the `name` and `weight` columns, validates that every constituent name exists in the database, computes a content hash as the ETF id, persists the ETF definition (weights) to SQLite, precomputes all results (constituents table, price history, top 5 holdings) using the uploaded weights + SQLite prices, caches them in Redis, and returns the ETF metadata.
3. **Table / Time Series / Bar Chart** — The frontend GETs `/api/etfs/{id}/...`. The backend serves from Redis cache when available. On cache miss, results are recomputed from the ETF definition stored in SQLite and re-cached. A 404 is returned only if the ETF ID has never been uploaded.

### Caching Strategy

- **Cache-aside pattern**: On upload, the backend precomputes and caches all three result sets in Redis keyed by the ETF content hash (e.g. `etf:a3f1b2c4d5e6f7a8:price_history`). On GET, results are served from Redis; on cache miss, they are recomputed from the ETF definition in SQLite and re-cached.
- Uploading the same constituent composition produces the same hash, refreshing the cache.
- TTL: 1 hour. Since the underlying price data is historical and static, cache staleness is not a concern.
- Redis is configured with `maxmemory 64mb` and `allkeys-lru` eviction policy, so least-recently-used entries are evicted when memory is full.

---

## 4. API Specification

### `POST /api/etfs/upload`

Upload an ETF definition CSV.

- **Request**: `multipart/form-data` with field `file` (CSV)
- **Response** `201`:
  ```json
  {
    "id": "a3f1b2c4d5e6f7a8",
    "name": "ETF1",
    "constituent_count": 25
  }
  ```
- **Error** `400`: invalid CSV or unknown constituents.

### `GET /api/etfs/{id}/constituents`

Return the constituent table for a given ETF.

- **Response** `200`:
  ```json
  [
    { "name": "A", "weight": 0.02, "latest_price": 20.05 },
    { "name": "B", "weight": 0.05, "latest_price": 43.12 }
  ]
  ```

### `GET /api/etfs/{id}/price-history`

Return the reconstructed ETF price time series.

- **Query params** (optional): `start_date`, `end_date`
- **Response** `200`:
  ```json
  [
    { "date": "2017-01-01", "price": 52.34 },
    { "date": "2017-01-02", "price": 53.01 }
  ]
  ```

### `GET /api/etfs/{id}/top-holdings`

Return the top 5 holdings by value (weight * latest price).

- **Response** `200`:
  ```json
  [
    { "name": "U", "weight": 0.155, "latest_price": 72.48, "holding_value": 11.23 },
    { "name": "X", "weight": 0.122, "latest_price": 48.36, "holding_value": 5.90 }
  ]
  ```

### `GET /api/health`

Health check endpoint.

- **Response** `200`: `{ "status": "ok" }`

---

## 5. Data Model

### SQLite Tables

```sql
CREATE TABLE constituent_prices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    date        TEXT    NOT NULL,  -- ISO 8601 (YYYY-MM-DD)
    close_price REAL    NOT NULL,
    UNIQUE(name, date)
);

CREATE INDEX idx_prices_name ON constituent_prices(name);
CREATE INDEX idx_prices_date ON constituent_prices(date);

CREATE TABLE etf_definitions (
    etf_id TEXT NOT NULL,
    name   TEXT NOT NULL,
    weight REAL NOT NULL,
    PRIMARY KEY (etf_id, name)
);
```

ETF definitions are persisted in SQLite on upload. They serve as the source of truth for recomputing cached results on Redis cache miss.

### Redis Keys

| Key Pattern                        | Value                          | TTL   |
|------------------------------------|--------------------------------|-------|
| `etf:{id}:constituents`           | JSON array of constituent data | 1 hr  |
| `etf:{id}:price_history`          | JSON array of date/price pairs | 1 hr  |
| `etf:{id}:top_holdings`           | JSON array of top 5 holdings   | 1 hr  |

---

## 6. Implementation Notes

### Project Structure

```
ETF_Price_Monitor/
├── docker-compose.yml
├── data/
│   ├── prices.csv              # Static price data, bundled with the app
│   ├── ETF1.csv                # Sample ETF file (reference only)
│   └── ETF2.csv                # Sample ETF file (reference only)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # FastAPI app, lifespan, CORS
│   │   ├── routers/
│   │   │   └── etf.py         # ETF endpoints
│   │   ├── services/
│   │   │   ├── etf_service.py # Business logic
│   │   │   └── cache.py       # Redis helpers
│   │   ├── models.py          # Pydantic schemas
│   │   ├── database.py        # SQLite connection & seeding
│   │   └── config.py          # Settings (env vars)
│   └── data/                   # Volume-mounted from repo root data/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.tsx
│       ├── components/
│       │   ├── FileUpload.tsx
│       │   ├── ConstituentTable.tsx
│       │   ├── PriceChart.tsx
│       │   └── TopHoldingsChart.tsx
│       └── api/
│           └── client.ts       # Axios/fetch wrapper
└── docs/
    ├── spec.md
    └── function_description.md
```

### Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_PATH=/app/data/etf.db
      - PRICES_CSV=/app/data/prices.csv
    depends_on: [redis]

  frontend:
    build: ./frontend
    ports: ["5173:80"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### Key Libraries

| Component | Libraries                                    |
|-----------|----------------------------------------------|
| Backend   | fastapi, uvicorn, aiofiles, redis, pandas    |
| Frontend  | react, recharts (or plotly.js), axios, antd   |

### Startup Sequence

1. `docker compose up --build`
2. Redis starts first.
3. Backend starts, checks if `constituent_prices` table is empty, and seeds from the bundled `prices.csv` if needed.
4. Frontend serves the SPA via nginx.
5. User opens `http://localhost:5173`.
