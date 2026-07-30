from app.strategy.explanation_generator import ExplanationGenerator



class DummyReport:

    direction = "BUY"



report = DummyReport()



option = {

    "score":100

}



probability = {

    "probability":75,

    "confidence":"HIGH"

}



result = ExplanationGenerator().generate(

    report,

    option,

    probability

)



print("="*60)

print("SAADHYA TRADE EXPLANATION")

print("="*60)



print()

print(
    result["summary"]
)



print()

print("Reasons:")

for item in result["reasons"]:

    print(
        "✓",
        item
    )



print()

print("Risks:")

for item in result["risks"]:

    print(
        "•",
        item
    )