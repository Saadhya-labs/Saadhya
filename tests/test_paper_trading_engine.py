from app.portfolio.paper_trading_engine import PaperTradingEngine


def test_paper_trade_open_and_close():

    engine = PaperTradingEngine()


    trade = engine.open_trade(

        symbol="HAL.NS",

        direction="BUY",

        quantity=200,

        entry_price=4581.40,

        stop_loss=4480,

        target=4800

    )


    assert trade.symbol == "HAL.NS"

    assert trade.status == "OPEN"

    assert trade.quantity == 200



    engine.close_trade(

        trade,

        4665

    )


    assert trade.status == "CLOSED"

    assert trade.exit_price == 4665

    assert trade.pnl > 0