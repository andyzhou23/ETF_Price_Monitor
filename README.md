# ETF Price Monitor

This project is a single-page web application that allows users to monitor historical prices for an ETF and its top holdings. It's built with React, FastAPI, SQLite, and Redis, designed to run with Docker Compose.

## Assumptions

*   Constituent price data is static and pre-loaded at startup (100 trading days, 26 tickers).
*   An ETF is uniquely identified by its constituents and their weights, not by its filename. Uploading the same composition produces the same ETF ID regardless of the file used.
*   Constituent weights are static and do not change over time.
*   ETF price at time *t* is the weighted sum of constituent prices: sum(weight_i * price_i(t)).
*   All constituents share the same set of trading dates (no missing data).
*   No authentication is required.

## Architecture

*   **Frontend**: React 18 (Vite + TypeScript) with Ant Design for UI components (tables, layout, file upload) and Recharts for data visualization (line chart with brush zoom for time series, bar chart for top holdings). Axios handles API communication.
*   **Backend**: Python FastAPI with Uvicorn ASGI server. Pandas is used for CSV parsing and data manipulation. Pydantic handles request/response validation.
*   **Database**: SQLite for persistent storage of constituent price history and ETF definitions.
*   **Cache**: Redis (cache-aside pattern) to cache computed ETF results. On cache miss, results are recomputed from SQLite.

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
