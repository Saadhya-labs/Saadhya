from app.execution.execution_engine import ExecutionEngine



def test_execution_engine_places_and_fills_order():


    engine = ExecutionEngine()


    order = engine.place_order(

        symbol="HAL.NS",

        direction="BUY",

        quantity=200,

        price=4581.40

    )


    assert order.status == "PENDING"


    filled = engine.execute(order)


    assert filled.status == "FILLED"

    assert filled.filled_price == 4581.40

    assert len(
        engine.filled_orders()
    ) == 1