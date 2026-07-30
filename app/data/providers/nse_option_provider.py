import requests

from app.data.providers.option_provider import OptionDataProvider
from app.options.models import OptionContract


class NSEOptionProvider(OptionDataProvider):

    BASE_URL = "https://www.nseindia.com"

    API_URL = (
        "https://www.nseindia.com/api/option-chain-equities"
    )

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/138.0 Safari/537.36"
                ),
                "Accept": "application/json,text/plain,*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.nseindia.com/",
                "Connection": "keep-alive",
            }
        )

    def _initialize_session(self):

        response = self.session.get(

            self.BASE_URL,

            timeout=10

        )

        response.raise_for_status()

    def get_option_chain(

        self,

        symbol

    ):

        self._initialize_session()

        response = self.session.get(

            self.API_URL,

            params={
                "symbol": symbol
            },

            timeout=10

        )

        response.raise_for_status()

        data = response.json()

        if "records" not in data:

            print("\nReturned JSON:\n")
            print(data)

            raise RuntimeError(
                "NSE did not return option-chain data."
            )

        contracts = []

        for item in data["records"]["data"]:

            expiry = item.get("expiryDate")

            strike = item.get("strikePrice")

            for option_type in ("CE", "PE"):

                if option_type not in item:
                    continue

                option = item[option_type]

                contracts.append(

                    OptionContract(

                        symbol=symbol,

                        expiry=expiry,

                        strike=strike,

                        option_type=option_type,

                        premium=option.get("lastPrice", 0),

                        volume=option.get(
                            "totalTradedVolume",
                            0
                        ),

                        open_interest=option.get(
                            "openInterest",
                            0
                        ),

                        implied_volatility=option.get(
                            "impliedVolatility",
                            0
                        ),

                        delta=0,

                        theta=0

                    )

                )

        return contracts