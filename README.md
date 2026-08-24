# Saadhya

Saadhya is an Indian-market research and recommendation tool for stock and option opportunities. It is recommendation-only: it does not place, route, or automate trades.

## What it does

- Collects normalized stock history from mock data or an explicitly selected live provider.
- Evaluates EMA, RSI, MACD, VWAP, and SuperTrend signals.
- Produces transparent stock recommendations with signal reasons and a direction-aware opportunity score.
- Ranks option contracts by direction, liquidity, implied volatility, and available Greeks.
- Creates a console report containing ranked opportunities, assumptions, and warnings.

## Run a scan

Create and activate the project virtual environment, install `requirements.txt`, then run:

```powershell
.\.venv\Scripts\python.exe -m app
```

Use `--format json` for machine-readable output:

```powershell
.\.venv\Scripts\python.exe -m app --format json
```

The default is deterministic mock data. To use live data, set `DATA_MODE=live`; live providers depend on upstream availability and are not used by the default test suite.

## Desktop application

Double-click `saadhya_desktop.pyw` to open the Windows desktop interface. It defaults to the supported NSE universe, automatically ranks the top opportunities, and provides mock/live selection, an editable scan universe, source warnings, and JSON export. It can auto-refresh with a 60-second minimum interval to respect public data-provider limits. The packaged Windows application is generated as `outputs\Saadhya.exe`.

In live mode, Saadhya reads recent Google News RSS headlines for each stock and labels their keyword-based impact as positive, negative, neutral, or unavailable. This is transparent context for the technical recommendation; it does not alter the technical score or act as a forecast.

The desktop application is recommendation-only. It never sends orders to a broker.

## Configuration

Settings are read from `.env` or the environment:

| Variable | Default | Meaning |
| --- | --- | --- |
| `DATA_MODE` | `mock` | `mock` or `live` market data |
| `DEFAULT_SYMBOL` | `HAL.NS` | Default single-symbol analysis target |
| `SCAN_SYMBOLS` | `DEFAULT_SYMBOL` | Comma-separated scan universe |
| `SCAN_LIMIT` | `10` | Positive report display limit |
| `APP_ENV` | `development` | Runtime environment label |

## Testing

Run the deterministic suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests marked `live` require external data access and are excluded by default. Run them intentionally with:

```powershell
.\.venv\Scripts\python.exe -m pytest -m live
```

## Important limitations

- Recommendations and probability values are heuristic model outputs, not forecasts or financial advice.
- Option entry, target, and invalidation zones are illustrative until validated against historical volatility and underlying-price behavior.
- If option Greeks are unavailable, Saadhya records a warning and does not score delta or theta.
- A market-data failure is a data-quality issue, not a signal.

## Architecture

`data providers → signal engine → recommendation engine → opportunity score → stock/option scanners → recommendation report → CLI`

Broker and execution experiments may remain in the repository for historical research, but they are not imported by the recommendation application path.

## Evaluate recommendation quality

`RecommendationEvaluator` performs a walk-forward evaluation over supplied historical data. It records observed directional returns and hit rate; it does not create orders, positions, or simulated fills. Treat these metrics as validation evidence, not a guarantee of future outcomes.
