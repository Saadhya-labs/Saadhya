from datetime import datetime

from app.portfolio.trade import Trade
from app.portfolio.trade_journal import TradeJournal
from app.portfolio.performance import PerformanceAnalyzer



def test_performance_analyzer():


    journal = TradeJournal()


    trades = [

        Trade(

            symbol="HAL",

            direction="BUY",

            quantity=100,

            entry_price=100,

            stop_loss=90,

            target=120,

            entry_time=datetime.now(),

            status="CLOSED",

            pnl=1000

        ),


        Trade(

            symbol="RELIANCE",

            direction="BUY",

            quantity=100,

            entry_price=100,

            stop_loss=90,

            target=120,

            entry_time=datetime.now(),

            status="CLOSED",

            pnl=-400

        ),


        Trade(

            symbol="TATA",

            direction="BUY",

            quantity=100,

            entry_price=100,

            stop_loss=90,

            target=120,

            entry_time=datetime.now(),

            status="CLOSED",

            pnl=500

        )

    ]


    for trade in trades:

        journal.record(trade)



    analyzer = PerformanceAnalyzer(

        journal

    )


    report = analyzer.summary()


    assert report["trades"] == 3

    assert report["net_profit"] == 1100

    assert report["win_rate"] == 66.67

    assert report["max_drawdown"] == 400