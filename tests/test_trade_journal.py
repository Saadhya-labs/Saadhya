from app.portfolio.trade_journal import TradeJournal
from app.portfolio.trade import Trade

from datetime import datetime



def test_trade_journal_metrics():


    journal = TradeJournal()


    trade1 = Trade(

        symbol="HAL.NS",

        direction="BUY",

        quantity=100,

        entry_price=100,

        stop_loss=90,

        target=120,

        entry_time=datetime.now(),

        exit_price=110,

        status="CLOSED",

        pnl=1000

    )


    trade2 = Trade(

        symbol="RELIANCE.NS",

        direction="BUY",

        quantity=100,

        entry_price=100,

        stop_loss=90,

        target=120,

        entry_time=datetime.now(),

        exit_price=95,

        status="CLOSED",

        pnl=-500

    )


    journal.record(trade1)

    journal.record(trade2)


    assert journal.trade_count() == 2

    assert journal.total_pnl() == 500

    assert journal.win_rate() == 50

    assert journal.average_pnl() == 250