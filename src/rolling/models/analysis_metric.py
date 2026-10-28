from dataclasses import dataclass

from rolling.models.metric_format import (
    MetricFormat
)


@dataclass
class AnalysisMetric:
    """
    Represents a rolling analysis
    metric.

    :param name:
        Human-readable metric name.
        Win Count, Average CAGR, ...

    :param description:
        One or two sentences explaining what the
        metric measures and whether higher or
        lower is better. Shown under the name in
        reports.

    :param values:
        Metric values grouped by
        strategy.

    :param reverse:
        Whether larger values are
        considered better when
        sorting results.

    :param format:
        Display format used by
        reporting components.
    """

    name: str
    description: str
    values: dict[str, float]
    reverse: bool
    format: MetricFormat
