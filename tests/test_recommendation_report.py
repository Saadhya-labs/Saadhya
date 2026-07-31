from app.reports.recommendation_report import RecommendationReport



def test_recommendation_report_generation():


    opportunities = [

        {

            "rank":1,

            "type":"OPTION",

            "symbol":"HAL",

            "score":92,

            "details":
            {
                "risk":"LOW"
            }

        }

    ]


    report = RecommendationReport().generate(
        opportunities
    )


    assert report["title"] == "SAADHYA OPPORTUNITY REPORT"

    assert report["total_opportunities"] == 1

    assert report["top_opportunities"][0]["recommendation"] == "HIGH PROBABILITY OPPORTUNITY"

    assert report["top_opportunities"][0]["risk"] == "LOW"