from app.data.mock_option_provider import MockOptionProvider


provider = MockOptionProvider()


options = provider.get_option_chain(
    "HAL"
)


for option in options:

    print(
        option
    )