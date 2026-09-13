import math


class OptionRanker:


    def calculate_score(self, option, direction):

        score = 0

        breakdown = {}

        warnings = []


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

        greeks_available = not (option.delta == 0 and option.theta == 0)

        if not greeks_available:
            warnings.append("Delta and theta are unavailable; Greeks were not scored.")

        elif 0.45 <= abs(option.delta) <= 0.65:
            delta_score = 25

        elif 0.30 <= abs(option.delta) < 0.45:
            delta_score = 15


        breakdown["delta"] = delta_score

        score += delta_score



        # Liquidity

        # Continuous scoring avoids hundreds of live contracts collapsing to
        # the same threshold score. Log scaling keeps very large index volume
        # from overwhelming otherwise tradable stock contracts.
        volume = max(0, float(option.volume or 0))
        open_interest = max(0, float(option.open_interest or 0))
        volume_score = max(0, min(10, (math.log10(volume + 1) - 3) / 3 * 10))
        oi_score = max(0, min(10, (math.log10(open_interest + 1) - 4) / 3 * 10))
        liquidity = round(volume_score + oi_score, 2)


        breakdown["liquidity"] = liquidity

        score += liquidity



        # Theta decay

        theta_score = 0

        if not greeks_available:
            theta_score = 0

        elif abs(option.theta) < 3:
            theta_score = 15

        elif abs(option.theta) < 5:
            theta_score = 8


        breakdown["theta"] = theta_score

        score += theta_score



        # IV

        iv_score = 0

        iv_available = option.implied_volatility > 0

        if 15 <= option.implied_volatility <= 30:
            iv_score = 15

        elif iv_available and option.implied_volatility < 40:
            iv_score = 8

        elif not iv_available:
            warnings.append("Implied volatility is unavailable; IV was not scored.")


        breakdown["iv"] = iv_score

        score += iv_score



        # Normalize only across fields that are actually available. Kite does
        # not provide exchange Greeks or IV, so missing fields neither earn
        # points nor depress every candidate into the same default bucket.
        available_max = 45
        if greeks_available:
            available_max += 40
        if iv_available:
            available_max += 15

        return {
            "score": round(min(score / available_max * 100, 100), 1),
            "breakdown": breakdown,
            "warnings": warnings
        }
