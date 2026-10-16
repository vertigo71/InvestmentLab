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

    values: dict[str, float]

    reverse: bool

    format: MetricFormat
