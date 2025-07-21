import requests
import time
import csv
from datetime import datetime, timedelta, timezone

GRAPHQL_URL = "https://beta-api.polymarket.com/graphql"

QUERY = """
query MarketsActivity($first: Int!, $after: String) {
  markets(first: $first, after: $after) {
    edges {
      node {
        id
        title
        status
        resolvesAt
        positions {
          id
          side
          outcome
          price
          size
          tradedAt
        }
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

def fetch_activity(first=50, after=None):
    payload = {
        "operationName": "MarketsActivity",
        "query": QUERY,
        "variables": {"first": first, "after": after},
    }
    response = requests.post(GRAPHQL_URL, json=payload)
    response.raise_for_status()
    return response.json()["data"]["markets"]

def scrape_recent_large_bets(hours=6, volume_threshold=500.0):
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    after = None
    large_bets = []

    while True:
        data = fetch_activity(after=after)
        for edge in data["edges"]:
            market = edge["node"]
            for pos in market.get("positions", []):
                try:
                    trade_time = datetime.fromisoformat(pos["tradedAt"].replace("Z", "+00:00"))
                    size = float(pos["size"])
                    if trade_time > cutoff_time and size >= volume_threshold:
                        large_bets.append({
                            "market_title": market["title"],
                            "side": pos["side"],
                            "price": pos["price"],
                            "size": size,
                            "traded_at": trade_time.isoformat(),
                        })
                except Exception as e:
                    continue
        if not data["pageInfo"]["hasNextPage"]:
            break
        after = data["pageInfo"]["endCursor"]
        time.sleep(0.5)

    return sorted(large_bets, key=lambda x: -x["size"])

def write_to_csv(bets, filename="large_bets.csv"):
    if not bets:
        print("No trades to write.")
        return

    keys = bets[0].keys()
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(bets)
    print(f"Saved {len(bets)} trades to {filename}")

def main():
    print("Scraping large trades in the past 6 hours...")
    bets = scrape_recent_large_bets(hours=6, volume_threshold=500)
    write_to_csv(bets)

if __name__ == "__main__":
    main()
