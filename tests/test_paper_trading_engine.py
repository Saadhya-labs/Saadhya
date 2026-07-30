from app.portfolio.paper_trading_engine import PaperTradingEngine


engine = PaperTradingEngine()


trade = engine.open_trade(

    symbol="HAL.NS",

    direction="BUY",

    quantity=200,

    entry_price=4581.40,

    stop_loss=4480,

    target=4800

)


engine.close_trade(

    trade,

    4665

)


print("=" * 60)
print("SAADHYA PAPER TRADING")
print("=" * 60)

print()

print("Symbol:", trade.symbol)
print("Status:", trade.status)
print("Entry:", trade.entry_price)
print("Exit:", trade.exit_price)
print("Quantity:", trade.quantity)
print("PnL:", round(trade.pnl, 2))