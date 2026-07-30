from app.strategy.signal_engine import SignalEngine

signals = {
    "EMA": "BUY",
    "RSI": "HOLD",
    "MACD": "BUY",
    "VWAP": "BUY",
    "SUPERTREND": "BUY"
}

engine = SignalEngine()

result = engine.generate(signals)

print(result)