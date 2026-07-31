from datetime import datetime

from app.execution.order import Order


class ExecutionEngine:


    def __init__(self):

        self.orders = []


    def place_order(

        self,

        symbol,

        direction,

        quantity,

        price,

        order_type="LIMIT"

    ):

        order = Order(

            symbol=symbol,

            direction=direction,

            quantity=quantity,

            order_type=order_type,

            price=price,

            created_at=datetime.now()

        )

        self.orders.append(order)

        return order



    def execute(

        self,

        order

    ):

        order.status = "FILLED"

        order.filled_price = order.price

        order.filled_at = datetime.now()

        return order



    def open_orders(self):

        return [

            order

            for order in self.orders

            if order.status == "PENDING"

        ]



    def filled_orders(self):

        return [

            order

            for order in self.orders

            if order.status == "FILLED"

        ]