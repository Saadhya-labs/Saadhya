from app.portfolio.trade_journal import TradeJournal


class PerformanceAnalyzer:

    def __init__(

        self,

        journal: TradeJournal

    ):

        self.journal = journal



    def max_drawdown(self):

        equity = 0

        peak = 0

        drawdown = 0


        for trade in self.journal.closed_trades():

            equity += trade.pnl


            if equity > peak:

                peak = equity


            current_drawdown = peak - equity


            if current_drawdown > drawdown:

                drawdown = current_drawdown


        return round(

            drawdown,

            2

        )



    def cumulative_pnl(self):

        equity = 0

        curve = []


        for trade in self.journal.closed_trades():

            equity += trade.pnl

            curve.append(

                equity

            )


        return curve



    def summary(self):

        trades = self.journal.closed_trades()

        wins = self.journal.winning_trades()

        losses = self.journal.losing_trades()


        total = len(trades)


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


        win_rate = 0


        if total:

            win_rate = (

                len(wins)

                / total

                * 100

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


        if gross_loss:

            profit_factor = (

                gross_profit

                / abs(gross_loss)

            )


        expectancy = 0


        if total:

            expectancy = (

                net_profit

                / total

            )


        drawdown = self.max_drawdown()


        recovery_factor = 0


        if drawdown:

            recovery_factor = (

                net_profit

                / drawdown

            )


        return {

            "trades": total,

            "wins": len(wins),

            "losses": len(losses),

            "win_rate": round(win_rate,2),

            "gross_profit": round(gross_profit,2),

            "gross_loss": round(gross_loss,2),

            "net_profit": round(net_profit,2),

            "average_win": round(average_win,2),

            "average_loss": round(average_loss,2),

            "profit_factor": round(profit_factor,2),

            "expectancy": round(expectancy,2),

            "max_drawdown": drawdown,

            "recovery_factor": round(recovery_factor,2)

        }