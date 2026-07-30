from app.data.mock_option_provider import MockOptionProvider
from app.options.scanner import OptionScanner
from app.options.smart_ranker import SmartOptionRanker
from app.options.auto_scanner import AutomaticOptionScanner



class DummyStock:


    symbol = "HAL.NS"

    direction = "BUY"

    confidence = 90



scanner = AutomaticOptionScanner(

    MockOptionProvider(),

    OptionScanner(),

    SmartOptionRanker()

)



result = scanner.scan(
    DummyStock()
)



print("="*60)
print("AUTOMATIC OPTION PICK")
print("="*60)


for key,value in result.items():

    print(
        key,
        ":",
        value
    )