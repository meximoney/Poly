import requests
import csv
from datetime import datetime, timedelta, timezone
import os

TRADE_API = "https://data-api.polymarket.com/trades"
MARKET_API = "https://data-api.polymarket.com/markets/"

def fetch_trades(limit=500, offset=0):
    params = {"limit": limit, "offset": offset}
    resp = requests.get(TRADE_API, params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_market_title(market_id, cache):
    if market_id in cache:
        return cache[market_id]

    try:
        resp = requests.get(MARKET_API + market_id)
        resp.raise_for_status()
        data = resp.json()
        title = data.get("question", "Unknown Market")
    except Exception:
        title = "Unavailable"

    cache[market_id] = title
    return title

def scrape_large_trades(hours=6, size_threshold=500.0):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    all_trades = fetch_trades(limit=500)
    print("📦 Sample Trade Object:")
print(all_trades[0])  # Just the first trade
exit()  # Temporarily stop the script after this

    large = []
    title_cache = {}

    for t in all_trades:
        t_time = datetime.fromtimestamp(t["timestamp"], tz=timezone.utc)
        size = float(t["size"])
        if t_time > cutoff and size >= size_threshold:
            market_id = t.get("marketId", "N/A")
            title = fetch_market_title(market_id, title_cache)

            large.append({
                "marketId": market_id,
                "event": title,
                "side": t.get("side", "N/A"),
                "price": t.get("price", "N/A"),
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
