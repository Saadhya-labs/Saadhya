from app.data.providers.mock_option_provider import MockOptionProvider
from app.data.providers.nse_option_provider import NSEOptionProvider



print("="*60)

print(
    "SAADHYA DATA PROVIDER TEST"
)

print("="*60)



mock = MockOptionProvider()



options = mock.get_option_chain(
    "HAL"
)



for option in options:

    print()

    print(
        option
    )



print()

print(
    "NSE Provider Status:"
)



try:

    NSEOptionProvider().get_option_chain(
        "HAL"
    )


except NotImplementedError as e:

    print(e)