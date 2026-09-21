from app.reports.recommendation_report import RecommendationReport
from app.options.models import OptionContract
from app.reports.recommendation_report import projected_roi



def test_recommendation_report_generation():


    opportunities = [

        {

            "rank":1,

            "type":"OPTION",

            "symbol":"HAL",

            "score":92,

            "details":
            {
                "risk":"LOW",
                "news_impact": {"impact": "POSITIVE"}
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

    assert report["top_opportunities"][0]["news_impact"] == "POSITIVE"


def test_option_overview_carries_premium_entry_target_and_projected_roi():
    contract = OptionContract("NIFTY", "2026-09-29", 25000, "CE", 100, 100000, 200000, 0, 0, 0)
    opportunity = {
        "rank": 1, "type": "OPTION", "symbol": "NIFTY", "score": 75,
        "details": {"option": {"option": contract}, "expiry": contract.expiry},
    }
    row = RecommendationReport().generate([opportunity])["top_opportunities"][0]
    assert row["recommendation_price"] == 100
    assert row["current_price"] == 100
    assert row["entry"][0] > 0
    assert row["target"] > 100
    assert row["projected_roi_pct"] > 0


def test_option_lot_value_uses_recommendation_premium_and_exact_lot_size():
    from app.gui.desktop import build_option_recommendation_rows

    contract = OptionContract("NIFTY", "2026-09-29", 25000, "CE", 101.25, 100000, 200000, 0, 0, 0, lot_size=75)
    opportunity = {
        "rank": 1, "type": "OPTION", "symbol": "NIFTY", "score": 75,
        "details": {"option": {"option": contract}, "expiry": contract.expiry},
    }
    ui_row = build_option_recommendation_rows([opportunity])[0]
    report_row = RecommendationReport().generate([opportunity])["top_opportunities"][0]
    assert ui_row["lot_size"] == report_row["lot_size"] == 75
    assert ui_row["one_lot_premium"] == report_row["one_lot_premium"] == 7593.75

    unknown = OptionContract("NIFTY", "2026-09-29", 25000, "CE", 101.25, 100000, 200000, 0, 0, 0)
    assert unknown.one_lot_premium is None


def test_recommendation_report_preserves_price_roi_and_existing_reasons():
    opportunity = {
        "rank": 1,
        "type": "STOCK",
        "symbol": "HAL.NS",
        "score": 80,
        "details": {
            "current_price": 100,
            "target": 112,
            "direction": "BUY",
            "simple_reasons": ["Trend is strengthening."],
            "technical_reasons": ["MACD Bullish"],
        },
    }

    row = RecommendationReport().generate([opportunity])["top_opportunities"][0]

    assert row["recommendation_price"] == 100
    assert row["target"] == 112
    assert row["projected_roi_pct"] == 12.0
    assert row["reasons"] == ["Trend is strengthening.", "MACD Bullish"]
    assert projected_roi(100, 90, "SELL") == 10.0


def test_recommendation_report_preserves_company_name_for_desktop_display():
    opportunity = {
        "rank": 1,
        "type": "STOCK",
        "symbol": "HAL.NS",
        "score": 80,
        "details": {"company_name": "HINDUSTAN AERONAUTICS LIMITED"},
    }

    row = RecommendationReport().generate([opportunity])["top_opportunities"][0]

    assert row["symbol"] == "HAL.NS"
    assert row["company_name"] == "HINDUSTAN AERONAUTICS LIMITED"
