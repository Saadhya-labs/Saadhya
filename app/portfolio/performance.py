from app.portfolio.trade_journal import TradeJournal


class PerformanceAnalyzer:

    def __init__(

        self,

        journal: TradeJournal

    ):

        self.journal = journal


    def summary(self):

        trades = self.journal.all_trades()

        wins = self.journal.winning_trades()

        losses = self.journal.losing_trades()

        total = len(trades)

        win_rate = 0

        if total:

            win_rate = (

                len(wins)

                / total

                * 100

            )

        gross_profit = sum(

            trade.pnl

            for trade in wins

        )

        gross_loss = sum(

            trade.pnl

            for trade in losses

        )

        net_profit = (

            gross_profit

            + gross_loss

        )

        average_win = 0

        if wins:

            average_win = (

                gross_profit

                / len(wins)

            )

        average_loss = 0

        if losses:

            average_loss = (

                gross_loss

                / len(losses)

            )

        profit_factor = 0

        if gross_loss != 0:

            profit_factor = (

                gross_profit

                / abs(gross_loss)

            )

        largest_win = 0

        if wins:

            largest_win = max(

                trade.pnl

                for trade in wins

            )

        largest_loss = 0

        if losses:

            largest_loss = min(

                trade.pnl

                for trade in losses

            )

        expectancy = 0

        if total:

            expectancy = (

                net_profit

                / total

            )

        return {

            "trades": total,

            "wins": len(wins),

            "losses": len(losses),

            "win_rate": round(

                win_rate,

                2

            ),

            "gross_profit": round(

                gross_profit,

                2

            ),

            "gross_loss": round(

                gross_loss,

                2

            ),

            "net_profit": round(

                net_profit,

                2

            ),

            "average_win": round(

                average_win,

                2

            ),

            "average_loss": round(

                average_loss,

                2

            ),

            "profit_factor": round(

                profit_factor,

                2

            ),

            "largest_win": round(

                largest_win,

                2

            ),

            "largest_loss": round(

                largest_loss,

                2

            ),

            "expectancy": round(

                expectancy,

                2

            )

        }