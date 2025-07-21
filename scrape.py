name: Run Polymarket REST Scraper

on:
  workflow_dispatch:     # Allows manual run
  schedule:
    - cron: '0 * * * *'  # Every hour UTC

jobs:
  run-script:
    runs-on: ubuntu-latest

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

      - name: List files (debug step)
        run: ls -l

      - name: Upload CSV file as artifact
        uses: actions/upload-artifact@v3
        with:
          name: polymarket-large-bets
          path: large_bets.csv
