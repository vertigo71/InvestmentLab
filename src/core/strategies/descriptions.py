"""
Text helpers shared by strategy descriptions.
"""


def deployment_text(deploy_years: float | None) -> str:
    """
    Describes the deployment time of the
    capital, for strategy descriptions.

        None -> "over the whole window"
        3    -> "over 3 years, then holds"
        1    -> "over 1 year, then holds"
    """

    if deploy_years is None:
        return "over the whole window"

    unit = "year" if deploy_years == 1 else "years"

    return f"over {deploy_years:g} {unit}, then holds"
