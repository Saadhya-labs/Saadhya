from app.broker.paper_broker import PaperBroker


def test_paper_broker_places_and_fills_order():

    broker = PaperBroker()


    order = broker.place_order(

        symbol="HAL.NS",

        direction="BUY",

        quantity=10,

        price=4500

    )


    assert order.status == "PENDING"


    filled = broker.fill_order(
        order.order_id
    )


    assert filled.status == "FILLED"

    assert filled.symbol == "HAL.NS"