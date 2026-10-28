
import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
DB_DIR = PROJECT_ROOT / "data"
DB_PATH = DB_DIR / "stocks.db"

DB_DIR.mkdir(parents=True, exist_ok=True)

stock_files = {
    "RELIANCE": DATA_DIR / "reliance.csv",
    "TCS": DATA_DIR / "tcs.csv",
    "ICICIBANK": DATA_DIR / "icicibank.csv",
}

with sqlite3.connect(DB_PATH) as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL NOT NULL,
            volume INTEGER,
            PRIMARY KEY (date, symbol)
        )
    """)

    for symbol, file_path in stock_files.items():
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        df = pd.read_csv(file_path)
        df.columns = [column.strip().lower() for column in df.columns]

        required = {"date", "open", "high", "low", "close", "volume"}
        if not required.issubset(df.columns):
            print(f"Invalid columns in {file_path.name}: {list(df.columns)}")
            continue

        df["date"] = pd.to_datetime(
            df["date"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

        for column in ["open", "high", "low", "close", "volume"]:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df["symbol"] = symbol
        df = df.dropna(subset=["date", "close"])
        df = df[df["close"] > 0]
        df = df.drop_duplicates(subset=["date", "symbol"], keep="last")

        df = df[
            ["date", "symbol", "open", "high", "low", "close", "volume"]
        ]

        # Replace this symbol's rows with the latest cleaned dataset.
        connection.execute(
            "DELETE FROM stock_prices WHERE symbol = ?", (symbol,)
        )

        df.to_sql(
            "stock_prices",
            connection,
            if_exists="append",
            index=False
        )

        print(f"{symbol}: stored {len(df)} rows")

    total = connection.execute(
        "SELECT COUNT(*) FROM stock_prices"
    ).fetchone()[0]

    print(f"\nTotal database rows: {total}")
    print(f"Database saved at: {DB_PATH}")

print("Database setup complete.")
