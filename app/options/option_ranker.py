class OptionRanker:


    def calculate_score(self, option, direction):

        score = 0

        breakdown = {}


        # Direction alignment

        if direction == "BUY" and option.option_type == "CE":
            direction_score = 25

        elif direction == "SELL" and option.option_type == "PE":
            direction_score = 25

        else:
            direction_score = 0


        breakdown["direction"] = direction_score

        score += direction_score



        # Delta

        delta_score = 0

        if 0.45 <= abs(option.delta) <= 0.65:
            delta_score = 25

        elif 0.30 <= abs(option.delta) < 0.45:
            delta_score = 15


        breakdown["delta"] = delta_score

        score += delta_score



        # Liquidity

        liquidity = 0

        if option.volume > 500000:
            liquidity += 10

        if option.open_interest > 1000000:
            liquidity += 10


        breakdown["liquidity"] = liquidity

        score += liquidity



        # Theta decay

        theta_score = 0

        if abs(option.theta) < 3:
            theta_score = 15

        elif abs(option.theta) < 5:
            theta_score = 8


        breakdown["theta"] = theta_score

        score += theta_score



        # IV

        iv_score = 0

        if 15 <= option.implied_volatility <= 30:
            iv_score = 15

        elif option.implied_volatility < 40:
            iv_score = 8


        breakdown["iv"] = iv_score

        score += iv_score



        return {
            "score": min(score,100),
            "breakdown": breakdown
        }