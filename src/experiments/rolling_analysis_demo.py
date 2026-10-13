from math import floor
from typing import Final

from analysis.rolling_results_analyzer import RollingResultsAnalyzer
from data.yahoo_loader import YahooLoader
from factories.strategy_factory import StrategyFactory

from transformers.rolling_window_builder import RollingWindowBuilder

from analysis.rolling_backtest_engine import RollingBacktestEngine

from models.contribution_frequency import ContributionFrequency

from strategies.all_in import AllIn
from strategies.dca import DCA
from strategies.drawdown_dca import DrawdownDCA

INITIAL_CAPITAL: Final = 100000
WINDOW_YEARS: Final = 3
# Reserve the final period for portfolio valuation.
INVESTMENT_PERIODS: Final = 52 * WINDOW_YEARS - 1


# URTH   -> 2012-
# VT     -> 2008-
# ^GSPC  -> 1990-
def main():
    prices = YahooLoader.load(
        ticker="^GSPC",
        start_date="1990-01-01",
        end_date="2027-01-01"
    )

    '''
        TODO: 
        prices
            aparte de tener running_max, deberia tener running_avg
        windows
            las windows estan bien. recalculan los running values inyectan index
            habria que calcular el running avg
        weekly contribution
            no tiene sentido calcular aqui eso. depende de la duracion de la window
        strategies
            no tiene sentido pasarle a una strategy su weekly contribution
            no viene definida por una wkly contribution 
            una strategy viene definida por 
                levels: list[tuple[float, float]],
                frequency: ContributionFrequency
            podemos pasarle la wkly_contribution al llamar a contribute
            strategy puede funcionar en base a un max o a un avg
        RollingBacktestEngine
            esta bien como esta. es el maestro que lo tiene todo.
            tiene las windows y puede calcular la weekly contribution
        RollingWindowResult:
            igual deberia tener su intial_capital. 
            _get_strategy_cagrs(
                results: list[RollingWindowResult],
                initial_capital: float,
                years: int
            solo hace falta pasar la list.. nada mas. la wndws Result lo tiene todo
            
    '''

    windows = RollingWindowBuilder.create_windows(
        prices=prices,
        window_years=WINDOW_YEARS
    )

    weekly_contribution = floor(INITIAL_CAPITAL / INVESTMENT_PERIODS)

    strategies = StrategyFactory.create(
        contribution_amount=weekly_contribution
    )

    results = RollingBacktestEngine.run(
        windows=windows,
        strategies=strategies,
        initial_capital=INITIAL_CAPITAL
    )

    print("\nWin Count")

    wins = RollingResultsAnalyzer.get_win_count(
        results
    )

    for (
            strategy_name,
            win_count
    ) in sorted(
        wins.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{win_count}"
        )

    print("\nAverage CAGR")

    average_cagrs = (
        RollingResultsAnalyzer.get_average_cagr(
            results=results,
            initial_capital=INITIAL_CAPITAL,
            years=WINDOW_YEARS
        )
    )

    for (
            strategy_name,
            cagr
    ) in sorted(
        average_cagrs.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        print(
            f"{strategy_name}: "
            f"{cagr:.2%}"
        )


if __name__ == "__main__":
    main()
