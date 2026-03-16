import hashlib
import pandas as pd
from io import StringIO
from fastapi import HTTPException
from ..database import get_db_connection
from ..models import ETFResponse, ConstituentModel, PriceDateModel, TopHoldingModel
from .cache import redis_cache


def _hash_constituents(df: pd.DataFrame) -> str:
    """Hash sorted name:weight pairs to produce a deterministic ETF id."""
    pairs = sorted(zip(df['name'], df['weight']))
    key = "|".join(f"{n}:{w}" for n, w in pairs)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _compute_and_cache(etf_id: str, df: pd.DataFrame):
    """Compute constituents, price history, and top holdings, then cache all."""
    conn = get_db_connection()
    c = conn.cursor()

    names = df['name'].tolist()
    placeholders = ','.join('?' * len(names))

    # Latest prices for constituents
    c.execute(f'''
        SELECT name, close_price as latest_price
        FROM constituent_prices
        WHERE date = (SELECT MAX(date) FROM constituent_prices)
        AND name IN ({placeholders})
    ''', names)
    latest_prices = {row['name']: row['latest_price'] for row in c.fetchall()}

    # Constituents table
    constituents = []
    for _, row in df.iterrows():
        constituents.append(ConstituentModel(
            name=row['name'],
            weight=row['weight'],
            latest_price=latest_prices.get(row['name'], 0.0),
        ))
    redis_cache.set(f"etf:{etf_id}:constituents",
                    [r.model_dump() for r in constituents])

    # Price history
    c.execute(f'''
        SELECT date, name, close_price
        FROM constituent_prices
        WHERE name IN ({placeholders})
        ORDER BY date ASC
    ''', names)
    rows = c.fetchall()
    conn.close()

    weights = {row['name']: row['weight'] for _, row in df.iterrows()}
    date_prices: dict[str, float] = {}
    for row in rows:
        d = row['date']
        date_prices[d] = date_prices.get(d, 0.0) + weights[row['name']] * row['close_price']

    price_history = [PriceDateModel(date=d, price=p) for d, p in sorted(date_prices.items())]
    redis_cache.set(f"etf:{etf_id}:price_history",
                    [r.model_dump() for r in price_history])

    # Top 5 holdings
    holdings = []
    for _, row in df.iterrows():
        lp = latest_prices.get(row['name'], 0.0)
        holdings.append(TopHoldingModel(
            name=row['name'],
            weight=row['weight'],
            latest_price=lp,
            holding_value=row['weight'] * lp,
        ))
    holdings.sort(key=lambda h: h.holding_value, reverse=True)
    top5 = holdings[:5]
    redis_cache.set(f"etf:{etf_id}:top_holdings",
                    [r.model_dump() for r in top5])


def process_etf_upload(name: str, file_content: bytes) -> ETFResponse:
    try:
        df = pd.read_csv(StringIO(file_content.decode('utf-8')))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    if 'name' not in df.columns or 'weight' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'name' and 'weight' columns")

    conn = get_db_connection()
    c = conn.cursor()

    # Validate constituents exist in prices
    c.execute('SELECT DISTINCT name FROM constituent_prices')
    valid_names = set(row['name'] for row in c.fetchall())
    conn.close()

    provided_names = set(df['name'].unique())
    invalid_names = provided_names - valid_names

    if invalid_names:
        raise HTTPException(status_code=400, detail=f"Unknown constituents: {', '.join(invalid_names)}")

    etf_id = _hash_constituents(df)

    # Precompute and cache all results
    _compute_and_cache(etf_id, df)

    return ETFResponse(id=etf_id, name=name, constituent_count=len(df))


def get_etf_constituents(etf_id: str) -> list[ConstituentModel]:
    cached = redis_cache.get(f"etf:{etf_id}:constituents")
    if cached:
        return [ConstituentModel(**c) for c in cached]
    raise HTTPException(status_code=404, detail="ETF not found — please re-upload the CSV")


def get_etf_price_history(etf_id: str) -> list[PriceDateModel]:
    cached = redis_cache.get(f"etf:{etf_id}:price_history")
    if cached:
        return [PriceDateModel(**p) for p in cached]
    raise HTTPException(status_code=404, detail="ETF not found — please re-upload the CSV")


def get_etf_top_holdings(etf_id: str) -> list[TopHoldingModel]:
    cached = redis_cache.get(f"etf:{etf_id}:top_holdings")
    if cached:
        return [TopHoldingModel(**h) for h in cached]
    raise HTTPException(status_code=404, detail="ETF not found — please re-upload the CSV")
