from app.core.saadhya_app import SaadhyaApp



def test_saadhya_app_generates_report():


    app = SaadhyaApp()


    opportunities = [

        {
            "rank":1,
            "type":"OPTION",
            "symbol":"NIFTY",
            "score":90,
            "details":{
                "risk":"LOW"
            }
        }

    ]


    report = app.generate_report(
        opportunities
    )


    assert report["title"] == "SAADHYA OPPORTUNITY REPORT"

    assert report["total_opportunities"] == 1

    assert report["top_opportunities"][0]["symbol"] == "NIFTY"