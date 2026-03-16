import pandas as pd
from io import StringIO
from fastapi import HTTPException
from ..database import get_db_connection
from ..models import ETFResponse, ConstituentModel, PriceDateModel, TopHoldingModel
from .cache import redis_cache

def process_etf_upload(name: str, file_content: bytes) -> ETFResponse:
    try:
        df = pd.read_csv(StringIO(file_content.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    if 'name' not in df.columns or 'weight' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'name' and 'weight' columns")

    conn = get_db_connection()
    c = conn.cursor()

    # Validate constituents exist in prices
    c.execute('SELECT DISTINCT name FROM constituent_prices')
    valid_names = set(row['name'] for row in c.fetchall())

    provided_names = set(df['name'].unique())
    invalid_names = provided_names - valid_names

    if invalid_names:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Unknown constituents: {', '.join(invalid_names)}")

    # Insert ETF definition
    c.execute('INSERT INTO etfs (name) VALUES (?)', (name,))
    etf_id = c.lastrowid

    # Insert constituents
    constituents_data = [(etf_id, row['name'], row['weight']) for _, row in df.iterrows()]
    c.executemany('INSERT INTO etf_constituents (etf_id, name, weight) VALUES (?, ?, ?)', constituents_data)
    
    conn.commit()
    conn.close()

    # Invalidate cache if replacing ETF? Spec says "invalidated when uploaded with same name", but we just create a new ETF definition for simplicity
    
    return ETFResponse(id=etf_id, name=name, constituent_count=len(constituents_data))

def get_etf_constituents(etf_id: int) -> list[ConstituentModel]:
    cache_key = f"etf:{etf_id}:constituents"
    cached = redis_cache.get(cache_key)
    if cached:
        return [ConstituentModel(**c) for c in cached]

    conn = get_db_connection()
    c = conn.cursor()
    
    query = '''
    SELECT c.name, c.weight, p.close_price as latest_price
    FROM etf_constituents c
    JOIN (
        SELECT name, close_price 
        FROM constituent_prices 
        WHERE date = (SELECT MAX(date) FROM constituent_prices)
    ) p ON c.name = p.name
    WHERE c.etf_id = ?
    '''
    c.execute(query, (etf_id,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="ETF not found or has no valid constituents")

    result = [ConstituentModel(**dict(row)) for row in rows]
    # Use mode_dump() in pydantic 2.x
    redis_cache.set(cache_key, [r.model_dump() for r in result], ttl=3600)
    return result

def get_etf_price_history(etf_id: int) -> list[PriceDateModel]:
    cache_key = f"etf:{etf_id}:price_history"
    cached = redis_cache.get(cache_key)
    if cached:
        return [PriceDateModel(**p) for p in cached]

    conn = get_db_connection()
    c = conn.cursor()

    query = '''
    SELECT p.date, SUM(c.weight * p.close_price) as price
    FROM etf_constituents c
    JOIN constituent_prices p ON c.name = p.name
    WHERE c.etf_id = ?
    GROUP BY p.date
    ORDER BY p.date ASC
    '''
    c.execute(query, (etf_id,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="ETF not found or has no history")

    result = [PriceDateModel(**dict(row)) for row in rows]
    redis_cache.set(cache_key, [r.model_dump() for r in result], ttl=3600)
    return result

def get_etf_top_holdings(etf_id: int) -> list[TopHoldingModel]:
    cache_key = f"etf:{etf_id}:top_holdings"
    cached = redis_cache.get(cache_key)
    if cached:
        return [TopHoldingModel(**h) for h in cached]

    conn = get_db_connection()
    c = conn.cursor()

    query = '''
    SELECT c.name, c.weight, p.close_price as latest_price, 
           (c.weight * p.close_price) as holding_value
    FROM etf_constituents c
    JOIN (
        SELECT name, close_price 
        FROM constituent_prices 
        WHERE date = (SELECT MAX(date) FROM constituent_prices)
    ) p ON c.name = p.name
    WHERE c.etf_id = ?
    ORDER BY holding_value DESC
    LIMIT 5
    '''
    c.execute(query, (etf_id,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="ETF not found")

    result = [TopHoldingModel(**dict(row)) for row in rows]
    redis_cache.set(cache_key, [r.model_dump() for r in result], ttl=3600)
    return result
