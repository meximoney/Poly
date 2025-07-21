name: Run Polymarket REST Scraper

on:
  workflow_dispatch:
  schedule:
    - cron: '0 * * * *'

jobs:
  run-script:
    runs-on: ubuntu-latest
    fail-fast: false

    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install requests

      - name: Run scraper script
        run: python scrape.py

      - name: List all files (debug)
        run: ls -la

      - name: Upload CSV as artifact
        uses: actions/upload-artifact@v3
        with:
          name: polymarket-large-bets
          path: large_bets.csv
