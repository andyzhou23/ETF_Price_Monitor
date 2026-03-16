import sqlite3
import pandas as pd
import os
from .config import settings

def get_db_connection():
    # Ensure directory exists
    os.makedirs(os.path.dirname(settings.database_path), exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create tables
    c.executescript('''
        CREATE TABLE IF NOT EXISTS constituent_prices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            date        TEXT    NOT NULL,  -- ISO 8601 (YYYY-MM-DD)
            close_price REAL    NOT NULL,
            UNIQUE(name, date)
        );

        CREATE INDEX IF NOT EXISTS idx_prices_name ON constituent_prices(name);
        CREATE INDEX IF NOT EXISTS idx_prices_date ON constituent_prices(date);

        CREATE TABLE IF NOT EXISTS etfs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS etf_constituents (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            etf_id INTEGER NOT NULL REFERENCES etfs(id) ON DELETE CASCADE,
            name   TEXT    NOT NULL,
            weight REAL    NOT NULL,
            UNIQUE(etf_id, name)
        );
    ''')
    conn.commit()

    # Seed constituent prices if empty
    c.execute('SELECT COUNT(*) FROM constituent_prices')
    count = c.fetchone()[0]

    if count == 0:
        if os.path.exists(settings.prices_csv):
            print("Seeding database with prices from CSV...")
            # Using pandas to melt the dataframe
            # The CSV has 'DATE' and then columns A-Z
            df = pd.read_csv(settings.prices_csv)
            # rename DATE to date
            if 'DATE' in df.columns:
                df.rename(columns={'DATE': 'date'}, inplace=True)
            elif 'date' not in df.columns:
                print("Could not find DATE column in prices.csv. Available columns:", df.columns)
            
            # Melt the dataframe so we have date, name (ticker), close_price
            melted = df.melt(id_vars=['date'], var_name='name', value_name='close_price')
            
            # drop NA values
            melted.dropna(subset=['close_price'], inplace=True)

            melted.to_sql('constituent_prices', conn, if_exists='append', index=False)
            print(f"Seeded {len(melted)} price records.")
        else:
            print(f"Warning: {settings.prices_csv} not found, skipping price seeding.")
    else:
        print(f"Database contains {count} price records, skipping seed.")
        
    conn.close()

if __name__ == "__main__":
    init_db()
