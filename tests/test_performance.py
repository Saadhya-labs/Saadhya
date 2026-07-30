from app.portfolio.paper_trading_engine import PaperTradingEngine
from app.portfolio.trade_journal import TradeJournal
from app.portfolio.performance import PerformanceAnalyzer


engine = PaperTradingEngine()

journal = TradeJournal()


trade = engine.open_trade(

    symbol="HAL.NS",

    direction="BUY",

    quantity=200,

    entry_price=4500,

    stop_loss=4400,

    target=4700

)

engine.close_trade(

    trade,

    4600

)

journal.record_trade(

    trade

)


trade = engine.open_trade(

    symbol="TCS.NS",

    direction="BUY",

    quantity=50,

    entry_price=3500,

    stop_loss=3450,

    target=3600

)

engine.close_trade(

    trade,

    3440

)

journal.record_trade(

    trade

)


report = PerformanceAnalyzer(

    journal

).summary()


print("=" * 60)
print("SAADHYA PERFORMANCE REPORT")
print("=" * 60)
print()

for key, value in report.items():

    print(

        f"{key:<20}",

        value

    )