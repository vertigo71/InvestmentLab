"""
Application entry point.

Used for manual experiments
and quick strategy comparisons.
"""

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


def main():
    """
        Empty
    """

    print(f'Go to experiments')


if __name__ == "__main__":
    main()
