from app.scanner.opportunity_ranker import OpportunityRanker



opportunities = [

    {
        "symbol":"HAL.NS",
        "contract":"4600 CE",
        "score":100
    },

    {
        "symbol":"TCS.NS",
        "contract":"2500 CE",
        "score":86
    },

    {
        "symbol":"INFY.NS",
        "contract":"1200 CE",
        "score":74
    }

]


result = OpportunityRanker().rank(
    opportunities
)


print("="*60)
print("SAADHYA TOP OPPORTUNITIES")
print("="*60)


for item in result:

    print()

    print(
        item["rank"],
        item["symbol"]
    )

    print(
        item["contract"]
    )

    print(
        "Score:",
        item["score"]
    )