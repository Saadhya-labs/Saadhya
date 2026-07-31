from dataclasses import dataclass


@dataclass
class BrokerCredentials:

    api_key: str

    api_secret: str

    access_token: str | None = None