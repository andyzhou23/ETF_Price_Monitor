# ETF Price Monitor

This project is a single-page web application that allows users to monitor historical prices for an ETF and its top holdings. It's built with React, FastAPI, SQLite, and Redis, designed to run with Docker Compose.

## Architecture

*   **Frontend**: React (Vite + TypeScript) displaying charts and interactive tables.
*   **Backend**: Python FastAPI serving API endpoints, managing valid ETF data.
*   **Database**: SQLite to persist the required historical prices and ETF definitions.
*   **Cache**: Redis to cache expensive computations (e.g. price aggregation, holdings).

## How to Run

1.  Make sure you have Docker and Docker Compose installed.
2.  Also ensure you have the `data` directory with the `prices.csv` at the root of the project.
3.  Run the application using Docker Compose:

```bash
docker compose up --build
```

4.  Once running, you can access the application:
    *   **Frontend**: `http://localhost:5173`
    *   **Backend API**: `http://localhost:8000`

## Features

1.  **CSV Upload**: Upload a CSV detailing ETF constituents and weights.
2.  **Constituents Table**: Track constituent ticker, weight, and latest close price.
3.  **ETF Price Time Series**: Examine the reconstructed ETF performance over time via an interactive chart.
4.  **Top 5 Holdings**: Visualize the largest constituents in your ETF based on computed holding values.
