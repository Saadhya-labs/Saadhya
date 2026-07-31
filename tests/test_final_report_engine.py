from app.reports.final_report_engine import FinalReportEngine
from app.reports.final_report_formatter import FinalReportFormatter



def test_final_report_generation():


    report = FinalReportEngine().generate(

        {

            "view":"BULLISH",

            "regime":"RISK_ON"

        },


        {

            "symbol":"HAL.NS",

            "direction":"BUY",

            "confidence":85

        },


        {

            "contract":"4600 CE",

            "expiry":"CURRENT",

            "entry":"120-140",

            "target":"220-250"

        }

    )


    text = FinalReportFormatter().format(
        report
    )


    assert "SAADHYA MARKET INTELLIGENCE REPORT" in text

    assert "HAL.NS" in text

    assert "4600 CE" in text