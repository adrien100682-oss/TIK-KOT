name: Collecte quotidienne
on:
  schedule:
    - cron: "17 4 * * *"
  workflow_dispatch:
permissions:
  contents: write
concurrency: collecte
jobs:
  collect:
    runs-on: ubuntu-latest
    timeout-minutes: 180
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Collecte
        run: python collect.py
        env:
          TWITCH_CLIENT_ID: ${{ secrets.TWITCH_CLIENT_ID }}
          TWITCH_CLIENT_SECRET: ${{ secrets.TWITCH_CLIENT_SECRET }}
          EBAY_APP_ID: ${{ secrets.EBAY_APP_ID }}
          EBAY_CERT_ID: ${{ secrets.EBAY_CERT_ID }}
      - name: Sauvegarde des données
        run: |
          git config user.name "collecte-bot"
          git config user.email "bot@users.noreply.github.com"
          git add data
          git diff --cached --quiet || (git commit -m "données $(date -u +%F)" && git push)
