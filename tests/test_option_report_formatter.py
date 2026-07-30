from app.reports.option_report_formatter import OptionReportFormatter



class Option:

    strike = 4600

    option_type = "CE"

    expiry = "NEXT_MONTH"



opportunity = {


    "symbol": "HAL.NS",

    "direction": "BUY",


    "option": {

        "option": Option(),

        "score": 100

    },


    "probability": {

        "probability":75,

        "confidence":"HIGH"

    },


    "explanation": {

        "reasons":[

            "Stock trend confirms bullish direction",

            "Option quality is excellent"

        ],

        "risks":[

            "Market reversal",

            "Momentum loss"

        ]

    }

}



result = OptionReportFormatter().format(
    opportunity
)


print(result)