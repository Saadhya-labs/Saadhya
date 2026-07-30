from app.portfolio.paper_trading_engine import PaperTradingEngine
from app.portfolio.trade_journal import TradeJournal


engine = PaperTradingEngine()

journal = TradeJournal()


trade1 = engine.open_trade(

    symbol="HAL.NS",

    direction="BUY",

    quantity=200,

    entry_price=4500,

    stop_loss=4400,

    target=4700

)

engine.close_trade(

    trade1,

    4600

)

journal.record_trade(

    trade1

)


trade2 = engine.open_trade(

    symbol="TCS.NS",

    direction="BUY",

    quantity=50,

    entry_price=3500,

    stop_loss=3450,

    target=3600

)

engine.close_trade(

    trade2,

    3440

)

journal.record_trade(

    trade2

)


print("=" * 60)
print("SAADHYA TRADE JOURNAL")
print("=" * 60)

print()

print(

    "Trades:",

    journal.trade_count()

)

print(

    "Winning Trades:",

    len(

        journal.winning_trades()

    )

)

print(

    "Losing Trades:",

    len(

        journal.losing_trades()

    )

)

print(

    "Net PnL:",

    round(

        journal.total_pnl(),

        2

    )

)

print()

for trade in journal.all_trades():

    print(

        trade.symbol,

        trade.status,

        round(trade.pnl, 2)

    )