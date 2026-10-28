import yfinance as yf
import pandas as pd
import os

# Stocks we want
stocks = {
    "RELIANCE": "RELIANCE.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "TCS": "TCS.NS"
}

all_data = []

for name, symbol in stocks.items():

    print(f"\nDownloading {name}...")

    data = yf.download(
        symbol,
        period="1y",
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        print(f"WARNING: No data found for {name}")
        continue

    # Remove extra yfinance column level
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Keep required columns
    data = data[["Open", "High", "Low", "Close", "Volume"]]

    # Add our stock name
    data.insert(0, "Symbol", name)

    # Make Date a normal column
    data.reset_index(inplace=True)

    all_data.append(data)

    print(f"{name}: {len(data)} rows downloaded.")

# Combine everything
if all_data:

    combined_data = pd.concat(all_data, ignore_index=True)

    # Make sure folder exists
    os.makedirs("data/raw", exist_ok=True)

    # Save the main dataset
    output_file = "data/raw/stock_prices.csv"
    combined_data.to_csv(output_file, index=False)

    print("\n===================================")
    print("DATASET CREATED SUCCESSFULLY")
    print("===================================")
    print(f"Total rows: {len(combined_data)}")
    print(f"Saved to: {output_file}")

    print("\nRows per stock:")
    print(combined_data["Symbol"].value_counts())

else:
    print("\nERROR: No stock data was downloaded.")
    
import yfinance as yf
import pandas as pd
from pathlib import Path

# Create a folder for the datasets
output_folder = Path("datasets")
output_folder.mkdir(exist_ok=True)

# Download the remaining two stocks
stocks = {
    "TCS": "TCS.NS",
    "ICICI_Bank": "ICICIBANK.NS"
}

for company, ticker in stocks.items():
    print(f"Downloading {company}...")

    try:
        data = yf.download(
            ticker,
            period="5y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if data.empty:
            print(f"No data received for {company}. Check connection.")
            continue

        # Handle multi-level column names
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()

        # Save each company's data
        filename = output_folder / f"{company.lower()}.csv"
        data.to_csv(filename, index=False)

        print(f"Saved {len(data)} rows to {filename}")

    except Exception as error:
        print(f"Error downloading {company}: {error}")

print("Download process finished.")
