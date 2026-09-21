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

The default is externally configured, read-only Kite market data. Set
`DATA_MODE=mock` for a deterministic offline scan or `DATA_MODE=live` for the
public live providers; network-backed providers are not used by the default
test suite.

## Desktop application

Double-click `saadhya_desktop.pyw` to open the Windows desktop interface. It
defaults to the full NSE F&O universe, automatically ranks the top
opportunities, and provides mock/live/Kite selection, an editable scan
universe, source warnings, and JSON export. Dedicated recommendation views show
the price at recommendation, target scenario, projected ROI, supporting
analysis evidence, and risks; projected ROI is not a guaranteed return or a
calibrated probability. It can auto-refresh with a 60-second minimum interval
to respect data-provider limits. The packaged Windows application is generated
as `outputs\Saadhya.exe`.

In live mode, Saadhya reads recent Google News RSS headlines for each stock and labels their keyword-based impact as positive, negative, neutral, or unavailable. This is transparent context for the technical recommendation; it does not alter the technical score or act as a forecast.

The desktop application is recommendation-only. It never sends orders to a broker.

Kite market-data providers remain alive between desktop refreshes. If a
temporary disconnect occurs after a successful fetch, Saadhya keeps the last
known stock history or option chain visible and marks the connection as
`DEGRADED / CACHED` until fresh data succeeds again.
Stock candles with invalid prices or volume and nonfinite or malformed live
prices are also treated as unavailable; they cannot replace last-known-good
market data or appear as fresh recommendations.
During a full-universe refresh, a failed Kite quote batch falls back only for
the affected underlyings; successful batches remain fresh, and an uncached
symbol failure does not discard recommendations from the rest of the scan.
  A successful response that omits listed contracts or contains unusable quote
  values is treated as incomplete, so Saadhya never replaces a complete chain
  with silently partial data.
Cached option recommendations retain their original quote timestamp. Tracked
contracts that disappear from a later scan keep their last known price but are
marked unavailable instead of being presented as freshly updated.
Expired contracts are never restored from the last-known-good chain during a
disconnect; if no unexpired cached contracts remain, that chain is unavailable.
Long-running desktop sessions refresh Kite's equity and derivative instrument
masters after a date rollover, so newly listed symbols and expiries become
available without restarting the application. Empty, malformed, or temporarily
unavailable daily masters never replace the last complete copy; Saadhya keeps
using that copy, marks the connection degraded, and retries on the next refresh.
If a rollover download loses more than a fifth of previously listed symbols,
still-live option contracts overall, or the live contracts for any one
underlying, Saadhya treats it as truncated and preserves the prior universe.
This prevents one damaged index or stock chain from silently losing a future
expiry while the rest of a large master looks complete. Contracts that expired
at rollover are excluded from that check.
If an entire refresh fails, the last successful option rows also remain visible
but switch to `UNAVAILABLE IN LATEST SCAN` until a successful refresh replaces them.

In Kite mode, enter `ALL_FNO` to analyze the complete listed NSE F&O universe.
Saadhya combines index and stock option quote requests into Kite-safe batches
of 400 instruments, then ranks recommendations independently for each of the
front, next, and far expiries in the dedicated options view. Relative expiry
buckets keep all three levels visible even when index and stock contracts have
different exact expiry dates.

### Private Zerodha Kite Connect data

For a private, read-only Kite Connect setup, provide the API key and current
access token through the local runtime configuration before starting Saadhya.
Select `kite` in the desktop data selector and run a scan; authentication and
token lifecycle management remain outside the application.
The Kite provider calls only instrument, quote, and historical-data endpoints;
Saadhya does not contain order-placement calls in this flow.

## Configuration

Settings are read from `.env` or the environment:

| Variable | Default | Meaning |
| --- | --- | --- |
| `DATA_MODE` | `kite` | `mock`, `live`, or externally configured `kite` market data |
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
