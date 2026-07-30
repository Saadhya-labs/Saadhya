from app.models.option_trade_candidate import OptionTradeCandidate


class OptionTradeEngine:


    def generate(self, analysis_report):

        contract = analysis_report.best_contract


        entry = contract.premium


        target = round(
            entry * 1.30,
            2
        )


        stop_loss = round(
            entry * 0.85,
            2
        )


        risk = entry - stop_loss

        reward = target - entry


        risk_reward = round(
            reward / risk,
            2
        )


        confidence = analysis_report.score


        if confidence >= 70:
            recommendation = "BUY"

        elif confidence >= 50:
            recommendation = "WATCH"

        else:
            recommendation = "AVOID"



        return OptionTradeCandidate(

            symbol=contract.symbol,

            option_contract=contract,

            score=analysis_report.score,

            recommendation=recommendation,

            entry=entry,

            target=target,

            stop_loss=stop_loss,

            risk_reward=risk_reward,

            confidence=confidence

        )