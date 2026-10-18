"""
Provides historical market context.
"""


class MarketContextProvider:
    """
    Provides relevant market events
    associated with a given year.
    """

    _CONTEXT = {

        1870: "Franco-Prussian War. Postwar US reconstruction.",
        1871: "Post-Civil War expansion. Great Chicago Fire.",
        1872: "Railroad boom.",
        1873: "Panic of 1873. Long Depression begins.",
        1874: "Depression deepens.",
        1875: "Long Depression continues.",
        1876: "Deflation. Weak markets.",
        1877: "Great Railroad Strike.",
        1878: "Long Depression bottom.",
        1879: "Return to gold standard. Recovery begins.",

        1880: "Strong recovery. Railroad expansion.",
        1881: "Garfield assassination. Market peak.",
        1882: "Recession begins.",
        1883: "Recession continues.",
        1884: "Panic of 1884.",
        1885: "Recovery begins.",
        1886: "Expansion. Haymarket affair.",
        1887: "Interstate Commerce Act.",
        1888: "Modest growth.",
        1889: "Expansion.",

        1890: "Baring crisis. Sherman Antitrust Act.",
        1891: "Recovery.",
        1892: "Expansion. Strain on gold reserves.",
        1893: "Panic of 1893. Severe depression.",
        1894: "Depression. Pullman strike.",
        1895: "Morgan-led gold rescue of the Treasury.",
        1896: "Free silver election. Market bottom.",
        1897: "Recovery begins.",
        1898: "Spanish-American War.",
        1899: "Merger boom.",

        1900: "Recovery after 1890s depression.",
        1901: "Northern Pacific corner. May panic.",
        1902: "Steady expansion. Coal strike.",
        1903: "Rich man's panic. Bear market.",
        1904: "Recovery begins.",
        1905: "Strong bull market.",
        1906: "San Francisco earthquake. Tight credit.",
        1907: "Panic of 1907. Bank runs.",
        1908: "Recovery after panic.",
        1909: "Expansion. Market peak.",

        1910: "Recession. Market decline.",
        1911: "Standard Oil breakup.",
        1912: "Modest growth.",
        1913: "Federal Reserve created. Recession begins.",
        1914: "WWI outbreak. NYSE closed for months.",
        1915: "War-driven boom.",
        1916: "War production boom.",
        1917: "US enters WWI. Bear market.",
        1918: "WWI ends. Spanish flu pandemic.",
        1919: "Postwar boom. Inflation.",

        1920: "Depression of 1920-21. Deflation.",
        1921: "Recession bottom. Recovery begins.",
        1922: "Roaring Twenties begin.",
        1923: "Short recession.",
        1924: "Expansion resumes.",
        1925: "Florida land boom.",
        1926: "Florida land bust. Steady growth.",
        1927: "Fed easing. Bull market.",
        1928: "Speculative boom.",
        1929: "Stock market crash.",

        1930: "Great Depression begins. Smoot-Hawley tariff.",
        1931: "Bank failures. UK leaves gold standard.",
        1932: "Market bottom. Dow -89% from peak.",
        1933: "New Deal. US leaves gold standard.",
        1934: "Recovery. Securities Exchange Act.",
        1935: "Strong recovery.",
        1936: "Continued recovery.",
        1937: "Recession of 1937-38.",
        1938: "Recession ends.",
        1939: "WWII begins in Europe.",

        1940: "Fall of France.",
        1941: "Pearl Harbor. US enters WWII.",
        1942: "Wartime bottom. Market turns.",
        1943: "War economy. Price controls.",
        1944: "D-Day. Bretton Woods.",
        1945: "WWII ends.",
        1946: "Postwar inflation. Market drop.",
        1947: "Marshall Plan.",
        1948: "Recession begins.",
        1949: "Recession ends. Long bull market begins.",

        1950: "Korean War.",
        1951: "Fed-Treasury Accord.",
        1952: "Steady growth.",
        1953: "Korean War ends. Recession.",
        1954: "Strong bull market.",
        1955: "Postwar boom.",
        1956: "Suez Crisis.",
        1957: "Recession. Sputnik.",
        1958: "Recovery.",
        1959: "Expansion.",

        1960: "Recession.",
        1961: "Bay of Pigs. Expansion begins.",
        1962: "Flash crash. Cuban Missile Crisis.",
        1963: "Kennedy assassination.",
        1964: "Tax cuts. Strong growth.",
        1965: "Go-go years. Vietnam escalation.",
        1966: "Credit crunch. Bear market.",
        1967: "Recovery.",
        1968: "Speculative peak. Social unrest.",
        1969: "Inflation. Bear market begins.",

        1970: "Recession. Penn Central collapse.",
        1971: "Nixon shock. End of gold convertibility.",
        1972: "Nifty Fifty peak.",
        1973: "Oil embargo. Bear market.",
        1974: "Stagflation. Deep bear market.",
        1975: "Recovery begins.",
        1976: "Expansion.",
        1977: "Rising inflation.",
        1978: "High inflation.",
        1979: "Second oil shock. Volcker at the Fed.",

        1980: "Double-digit inflation. Recession.",
        1981: "Volcker rate hikes. Recession.",
        1982: "Rates fall. Bull market begins.",
        1983: "Strong recovery.",
        1984: "Expansion.",
        1985: "Plaza Accord.",
        1986: "Oil price collapse. Tax reform.",
        1987: "Black Monday crash.",
        1988: "Recovery after crash.",
        1989: "Savings and loan crisis. Berlin Wall falls.",

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
