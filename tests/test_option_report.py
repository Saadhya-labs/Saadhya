from app.options.report import OptionReport


class DummyOption:

    symbol = "HAL.NS"

    final_score = 90

    probability = 72

    risk = "MEDIUM"

    option = type(
        "Option",
        (),
        {
            "strike":4600,
            "option_type":"CE",
            "expiry":"NEXT_MONTH",
            "premium":120
        }
    )()



result = OptionReport().generate(
    {
        "symbol": DummyOption.symbol,
        "option": DummyOption.option,
        "final_score": DummyOption.final_score,
        "probability": DummyOption.probability,
        "risk": DummyOption.risk
    }
)


print("="*60)
print("SAADHYA OPTION OPPORTUNITY")
print("="*60)


for k,v in result.items():

    print(k,":",v)