from app.broker.live_broker import LiveBroker


class ZerodhaBroker(LiveBroker):


    def __init__(
        self,
        credentials
    ):

        self.credentials = credentials

        self.connected = False



    def connect(self):

        self.connected = True

        return True



    def place_order(
        self,
        symbol,
        direction,
        quantity,
        price
    ):

        if not self.connected:

            raise Exception(
                "Broker not connected"
            )


        return {

            "broker": "ZERODHA",

            "symbol": symbol,

            "direction": direction,

            "quantity": quantity,

            "price": price

        }



    def get_balance(self):

        return 0



    def get_positions(self):

        return []