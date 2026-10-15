"""
Provides historical market context.
"""

class MarketContextProvider:
    """
    Provides relevant market events
    associated with a given year.
    """

    _CONTEXT = {

        1990: "Iraq invasion of Kuwait. Oil shock.",
        1991: "Gulf War. Recovery begins.",
        1992: "European currency crisis.",
        1993: "Economic recovery.",
        1994: "Fed tightening cycle.",
        1995: "Technology-driven bull market.",
        1996: "Continued expansion.",
        1997: "Asian Financial Crisis.",
        1998: "Russian default. LTCM collapse.",
        1999: "Dot-com bubble acceleration.",

        2000: "Dot-com bubble peak.",
        2001: "Dot-com crash. September 11.",
        2002: "Bear market continues.",
        2003: "New bull market begins.",
        2004: "Global economic expansion.",
        2005: "Steady growth.",
        2006: "Housing bubble concerns.",
        2007: "Subprime mortgage crisis.",
        2008: "Global Financial Crisis.",
        2009: "Recovery after financial crisis.",

        2010: "Eurozone debt concerns.",
        2011: "US downgrade. Eurozone stress.",
        2012: "ECB intervention. Market recovery.",
        2013: "Strong bull market.",
        2014: "Low volatility growth.",
        2015: "China slowdown fears.",
        2016: "Brexit. US election.",
        2017: "Global synchronized growth.",
        2018: "Trade war. Q4 correction.",
        2019: "Strong pre-pandemic rally.",

        2020: "COVID crash and recovery.",
        2021: "Post-pandemic expansion.",
        2022: "Inflation shock. Bear market.",
        2023: "AI-driven recovery.",
        2024: "Broad bull market.",
        2025: "AI investment cycle."
    }

    @staticmethod
    def get(year: int) -> str:
        """
        Returns market context for a year.

        :param year:
            Year to query.

        :return:
            Associated market description.
        """

        return MarketContextProvider._CONTEXT.get(
            year,
            "No context available."
        )

    @staticmethod
    def get_window_context(
            start_year: int,
            end_year: int
    ) -> list[str]:
        """
        Returns the market context for all
        years in the specified range.

        The end year is excluded.
        """

        return [
            MarketContextProvider.get(year)
            for year in range(
                start_year,
                end_year
            )
        ]
