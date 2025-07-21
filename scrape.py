import requests
import csv
from datetime import datetime, timedelta, timezone
import os

API_URL = "https://data-api.polymarket.com/trades"

def fetch_trades(limit=500, offset=0):
    params = {"limit": limit, "offset": offset}
    resp = requests.get(API_URL, params=params)
    resp.raise_for_status()
    return resp.json()

def scrape_large_trades(hours=6, size_threshold=500.0):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    all_trades = fetch_trades(limit=500)
    large = []
    for t in all_trades:
        t_time = datetime.fromtimestamp(t["timestamp"], tz=timezone.utc)
        size = float(t["size"])
        if t_time > cutoff and size >= size_threshold:
            large.append({
                "marketId": t["marketId"],
                "side": t["side"],
                "price": t["price"],
                "size": size,
                "timestamp": t_time.isoformat(),
            })
    return sorted(large, key=lambda x: -x["size"])

def write_csv(trades, filename="large_bets.csv"):
    if not trades:
        print("No large trades found.")
        return
    keys = trades[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(trades)
    print(f"Wrote {len(trades)} trades to {filename}")
    print("✅ File exists:", os.path.exists(filename))

def main():
    print("🔍 Scraping large trades in the past 6 hours...")
    trades = scrape_large_trades(hours=6, size_threshold=500)
    write_csv(trades)

if __name__ == "__main__":
    main()
