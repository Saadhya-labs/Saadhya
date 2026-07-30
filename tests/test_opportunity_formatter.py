from app.options.opportunity_formatter import OpportunityFormatter


dummy = {


    "symbol":"HAL.NS",

    "direction":"BUY",


    "option":{

        "option":type(
            "Option",
            (),
            {

                "strike":4600,
                "option_type":"CE",
                "expiry":"NEXT_MONTH",
                "premium":120

            }
        )(),


        "score":100,


        "breakdown":{

            "delta":25

        }

    }

}


result = OpportunityFormatter().format(dummy)


print("="*60)
print("SAADHYA OPPORTUNITY")
print("="*60)


for k,v in result.items():

    print(
        k,
        ":",
        v
    )