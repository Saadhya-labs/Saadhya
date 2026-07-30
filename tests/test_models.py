from app.models.analysis_report import AnalysisReport
from app.models.risk_report import RiskReport
from app.models.market_context import MarketContext


report = AnalysisReport(
    symbol="TEST",
    price=100,
    signals={},
    recommendation="BUY",
    confidence=80,
    direction="BUY",
    opportunity_score=85,
    risk="MEDIUM",
    holding="Swing",
    simple_reasons=[
        "Trend is improving"
    ],
    technical_reasons=[
        "EMA Bullish"
    ],
    suggested_action="Consider buying gradually",
    invalidation=[
        "Trend reversal"
    ]
)


risk = RiskReport(
    risk_level="MEDIUM",
    stop_loss=95,
    target=110,
    risk_reward=2
)


market = MarketContext(
    nifty="BULLISH",
    sensex="BULLISH",
    banknifty="NEUTRAL",
    vix="LOW",
    market_bias="POSITIVE"
)


print(report)
print()
print(risk)
print()
print(market)