
from pathlib import Path
import pandas as pd

# Project root is the parent of the scripts folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STOCK_FILES = {
    "RELIANCE": RAW_DIR / "reliance.csv",
    "TCS": RAW_DIR / "tcs.csv",
    "ICICIBANK": RAW_DIR / "icici_bank.csv",
}

required_columns = [
    "Date", "Open", "High", "Low",
    "Close", "Volume"
]

for symbol, file_path in STOCK_FILES.items():
    print(f"\nProcessing {symbol}...")

    if not file_path.exists():
        print(f"File not found: {file_path}")
        continue

    try:
        df = pd.read_csv(file_path)

        # Normalize column names
        df.columns = [
            str(column).strip().replace(" ", "_")
            for column in df.columns
        ]

        # Handle common date-column naming variations
        date_column = next(
            (column for column in df.columns
             if column.lower() in ["date", "datetime"]),
            None
        )

        if date_column is None:
            print(f"No date column found in {file_path.name}")
            continue

        if date_column != "Date":
            df.rename(columns={date_column: "Date"}, inplace=True)

        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            print(
                f"Missing columns in {file_path.name}: "
                f"{missing_columns}"
            )
            print(f"Available columns: {list(df.columns)}")
            continue

        # Parse dates and numeric fields
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        numeric_columns = [
            "Open", "High", "Low", "Close", "Volume"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            )

        # Remove invalid dates and duplicate dates
        df.dropna(subset=["Date"], inplace=True)
        df.drop_duplicates(subset=["Date"], keep="last", inplace=True)

        # Remove rows without usable price data
        df.dropna(subset=["Close"], inplace=True)
        df = df[df["Close"] > 0]

        # Sort chronologically
        df.sort_values("Date", inplace=True)

        # Add the stock symbol
        df["Symbol"] = symbol

        # Save cleaned data
        output_file = OUTPUT_DIR / f"{symbol.lower()}.csv"
        df.to_csv(output_file, index=False)

        print(f"Saved: {output_file}")
        print(f"Rows retained: {len(df)}")
        print(f"Missing values:\n{df.isna().sum()}")

    except Exception as error:
        print(f"Could not process {symbol}: {error}")

print("\nCleaning process finished.")
