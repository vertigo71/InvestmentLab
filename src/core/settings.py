"""
Experiment settings loaded from YAML.

The active experiment is named in configs/active_yaml.txt.
Its file, configs/<name>.yaml, defines the initial capital,
the cash interest rate, the rolling window, the data source
and the strategies. See configs/config_help.txt.

The settings are loaded once, the first time this module is
imported, and exposed as SETTINGS. Any error in the files
stops the program with a message naming the file and the
field to fix.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Final, TypeVar

import yaml

from core.config import CONFIG_FOLDER, INPUT_FOLDER
from core.models.contribution_frequency import ContributionFrequency
from core.models.data_frequency import DataFrequency
from core.models.reference_price import ReferencePrice
from core.providers.csv_source import CsvSource
from core.providers.data_source import DataSource
from core.providers.yahoo_source import YahooSource
from core.strategies.all_in import AllIn
from core.strategies.dca import DCA
from core.strategies.drawdown_dca import DrawdownDCA
from core.strategies.rebalance import Rebalance
from core.strategies.strategy import Strategy

# File naming the experiment to run.
ACTIVE_FILE: Final = CONFIG_FOLDER / "active_yaml.txt"

# Any Enum class, used by _enum().
E = TypeVar("E", bound=Enum)


# ============================================================
# Settings model
# ============================================================

@dataclass(frozen=True)
class RollingSettings:
    """
    Settings of the rolling-window analysis.

    :param window_years:
        Length of each rolling window, in years.

    :param start_date:
        First date of the data, YYYY-MM-DD.

    :param end_date:
        End date of the data (excluded), YYYY-MM-DD.

    :param data_source:
        Where the prices come from.

    :param strategies:
        Strategies to compare.
    """

    window_years: int
    start_date: str
    end_date: str
    data_source: DataSource
    strategies: list[Strategy]


@dataclass(frozen=True)
class Settings:
    """
    Complete settings of one experiment.

    :param experiment:
        Experiment name (YAML file name
        without extension).

    :param initial_capital:
        Capital at the start of each window.

    :param cash_annual_rate:
        Annual rate earned by uninvested cash.

    :param rolling:
        Rolling-window analysis settings.

    :param yaml_text:
        Exact content of the YAML file, as read
        when the settings were loaded.

    """

    experiment: str
    initial_capital: float
    cash_annual_rate: float
    rolling: RollingSettings
    yaml_text: str

    def save_copy(self, output_file: Path) -> Path:
        """
        Saves the experiment YAML next to an
        exported file, with the same name and
        a .yaml extension:

            20261020_rolling_analysis_3y.csv
            20261020_rolling_analysis_3y.yaml

        The content written is the one read at
        start-up, so it always matches the
        settings actually used, even if the YAML
        file was edited during the run.

        :param output_file:
            Exported file the copy belongs to.

        :return:
            Path of the saved copy.
        """

        copy_file = output_file.with_suffix(".yaml")

        copy_file.write_text(
            self.yaml_text,
            encoding="utf-8"
        )

        return copy_file


# ============================================================
# Loading
# ============================================================

def read_active_experiment() -> str:
    """
    Returns the experiment name written in
    active_yaml.txt.

    Lines starting with # and empty lines are
    ignored. Exactly one name must remain.

    :raises ValueError:
        If no name or more than one name is found.
    """

    names = [
        line.strip()
        for line in ACTIVE_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
           and not line.strip().startswith("#")
    ]

    if len(names) != 1:
        raise ValueError(
            f"{ACTIVE_FILE.name}: expected exactly one "
            f"experiment name, found {len(names)}: "
            f"{names}"
        )

    # Accept the name with or without extension.
    return names[0].removesuffix(".yaml")


def load_settings(experiment: str) -> Settings:
    """
    Loads and validates the settings of an
    experiment.

    :param experiment:
        Experiment name, i.e. the YAML file name in
        the configs folder without extension.

    :return:
        Validated settings.

    :raises ValueError:
        If the file does not exist or any field is
        missing, unknown or invalid.
    """

    path = CONFIG_FOLDER / f"{experiment}.yaml"

    if not path.exists():
        available = sorted(
            file.stem  # without the extension
            for file in CONFIG_FOLDER.glob("*.yaml")
        )

        raise ValueError(
            f"Experiment '{experiment}' not found in "
            f"{CONFIG_FOLDER}. Available: "
            f"{', '.join(available) or 'none'}"
        )

    # Kept as text, so save_copy() can write
    # exactly what was used.
    yaml_text = path.read_text(encoding="utf-8")

    data = yaml.safe_load(yaml_text)

    # Prefix of every error message, e.g.
    # "sp500_weekly.yaml: rolling.window_years".
    context = path.name

    data = _as_dict(data, context)

    _check_keys(
        data,
        required={"initial_capital", "cash_annual_rate", "rolling"},
        optional=set(),
        context=context
    )

    initial_capital = _number(
        data["initial_capital"],
        f"{context}: initial_capital"
    )

    if initial_capital <= 0:
        raise ValueError(
            f"{context}: initial_capital must be "
            f"positive, got {initial_capital}"
        )

    cash_annual_rate = _number(
        data["cash_annual_rate"],
        f"{context}: cash_annual_rate"
    )

    # Negative rates are possible (e.g. EUR 2015-2021),
    # but cash cannot lose 100% or more per year.
    if cash_annual_rate <= -1:
        raise ValueError(
            f"{context}: cash_annual_rate must be "
            f"greater than -1, got {cash_annual_rate}"
        )

    return Settings(
        experiment=experiment,
        initial_capital=initial_capital,
        cash_annual_rate=cash_annual_rate,
        rolling=_parse_rolling(
            data["rolling"],
            f"{context}: rolling"
        ),
        yaml_text=yaml_text
    )


# ============================================================
# Sections
# ============================================================

def _parse_rolling(
        value: Any,
        context: str
) -> RollingSettings:
    """
    Builds the rolling settings section.
    """

    data = _as_dict(value, context)

    _check_keys(
        data,
        required={
            "window_years",
            "start_date",
            "end_date",
            "data_source",
            "strategies"
        },
        optional=set(),
        context=context
    )

    window_years = data["window_years"]

    if (
            not isinstance(window_years, int)
            or isinstance(window_years, bool)
            or window_years <= 0
    ):
        raise ValueError(
            f"{context}.window_years: expected a "
            f"positive whole number, got "
            f"{window_years!r}"
        )

    start_date = _date(
        data["start_date"],
        f"{context}.start_date"
    )

    end_date = _date(
        data["end_date"],
        f"{context}.end_date"
    )

    if end_date <= start_date:
        raise ValueError(
            f"{context}: end_date ({end_date}) must be "
            f"later than start_date ({start_date})"
        )

    strategies_data = data["strategies"]

    if not isinstance(strategies_data, list) or not strategies_data:
        raise ValueError(
            f"{context}.strategies: expected a "
            f"non-empty list"
        )

    return RollingSettings(
        window_years=window_years,
        start_date=start_date,
        end_date=end_date,
        data_source=_parse_data_source(
            data["data_source"],
            f"{context}.data_source"
        ),
        strategies=[
            _parse_strategy(
                item,
                f"{context}.strategies, strategy {number}"
            )
            # Numbered from 1, as read in the file.
            for number, item in enumerate(
                strategies_data,
                start=1
            )
        ]
    )


def _parse_data_source(
        value: Any,
        context: str
) -> DataSource:
    """
    Builds a YahooSource or CsvSource.
    """

    data = _as_dict(value, context)

    source_type = data.get("type")

    if source_type == "yahoo":
        _check_keys(
            data,
            required={"type", "ticker"},
            optional={"frequency", "auto_adjust"},
            context=context
        )

        auto_adjust = data.get("auto_adjust", True)

        if not isinstance(auto_adjust, bool):
            raise ValueError(
                f"{context}.auto_adjust: expected true "
                f"or false, got {auto_adjust!r}"
            )

        return YahooSource(
            ticker=_text(
                data["ticker"],
                f"{context}.ticker"
            ),
            frequency=_enum(
                DataFrequency,
                data.get("frequency", "WEEKLY"),
                f"{context}.frequency"
            ),
            auto_adjust=auto_adjust
        )

    if source_type == "csv":
        _check_keys(
            data,
            required={"type", "label", "path", "frequency"},
            optional=set(),
            context=context
        )

        # Relative to the inputs folder.
        path = INPUT_FOLDER / _text(
            data["path"],
            f"{context}.path"
        )

        # Checked here, so a wrong name fails before
        # any work is done.
        if not path.exists():
            raise ValueError(
                f"{context}.path: file not found: {path}"
            )

        return CsvSource(
            label=_text(
                data["label"],
                f"{context}.label"
            ),
            path=path,
            frequency=_enum(
                DataFrequency,
                data["frequency"],
                f"{context}.frequency"
            )
        )

    raise ValueError(
        f"{context}.type: expected yahoo or csv, "
        f"got {source_type!r}"
    )


def _parse_strategy(
        value: Any,
        context: str
) -> Strategy:
    """
    Builds an AllIn, DCA or DrawdownDCA strategy.
    """

    data = _as_dict(value, context)

    strategy_type = data.get("type")

    if strategy_type == "all_in":
        _check_keys(
            data,
            required={"type"},
            optional=set(),
            context=context
        )

        return AllIn()

    if strategy_type == "dca":
        _check_keys(
            data,
            required={"type", "frequency"},
            optional=set(),
            context=context
        )

        return DCA(
            frequency=_enum(
                ContributionFrequency,
                data["frequency"],
                f"{context}.frequency"
            )
        )

    if strategy_type == "drawdown_dca":
        _check_keys(
            data,
            required={
                "type",
                "frequency",
                "reference_price",
                "levels"
            },
            optional={"base_multiplier"},
            context=context
        )

        levels = _levels(
            data["levels"],
            f"{context}.levels"
        )

        base_multiplier = _number(
            data.get("base_multiplier", 1.0),
            f"{context}.base_multiplier"
        )

        # DrawdownDCA validates the levels and the
        # base multiplier; its error is reported
        # with the position in the file.
        try:
            return DrawdownDCA(
                levels=levels,
                frequency=_enum(
                    ContributionFrequency,
                    data["frequency"],
                    f"{context}.frequency"
                ),
                reference_price=_enum(
                    ReferencePrice,
                    data["reference_price"],
                    f"{context}.reference_price"
                ),
                base_multiplier=base_multiplier
            )

        except ValueError as error:
            raise ValueError(
                f"{context}: {error}"
            ) from error

    if strategy_type == "rebalance":
        _check_keys(
            data,
            required={
                "type",
                "equity_weight",
                "frequency"
            },
            optional={"tolerance"},
            context=context
        )

        # Rebalance validates the weight and the
        # tolerance; its error is reported with
        # the position in the file.
        try:
            return Rebalance(
                equity_weight=_number(
                    data["equity_weight"],
                    f"{context}.equity_weight"
                ),
                frequency=_enum(
                    ContributionFrequency,
                    data["frequency"],
                    f"{context}.frequency"
                ),
                tolerance=_number(
                    data.get("tolerance", 0.0),
                    f"{context}.tolerance"
                )
            )

        except ValueError as error:
            raise ValueError(
                f"{context}: {error}"
            ) from error

    raise ValueError(
        f"{context}.type: expected all_in, dca, "
        f"drawdown_dca or rebalance, got "
        f"{strategy_type!r}"
    )

# ============================================================
# Field helpers
# ============================================================

def _as_dict(value: Any, context: str) -> dict:
    """
    Checks that a YAML value is a mapping
    (key: value pairs).
    """

    if not isinstance(value, dict):
        raise ValueError(
            f"{context}: expected key: value pairs, "
            f"got {value!r}"
        )

    return value


def _check_keys(
        data: dict,
        required: set[str],
        optional: set[str],
        context: str
) -> None:
    """
    Checks that all required keys are present and
    that there are no unknown keys, which catches
    typos such as 'frequncy'.
    """

    missing = required - data.keys()
    unknown = data.keys() - required - optional

    # Both are reported together: a typo such as
    # 'frequncy' is a missing and an unknown key.
    problems: list[str] = []

    if missing:
        problems.append(
            f"missing {', '.join(sorted(missing))}"
        )

    if unknown:
        problems.append(
            f"unknown {', '.join(sorted(map(str, unknown)))}"
        )

    if problems:
        allowed = sorted(required | optional)

        raise ValueError(
            f"{context}: {'; '.join(problems)} "
            f"(allowed: {', '.join(allowed)})"
        )


def _number(value: Any, context: str) -> float:
    """
    Checks that a value is a number.

    Returned unchanged, so whole numbers stay
    integers: a multiplier of 2 keeps appearing
    as 2, not 2.0, in strategy names.
    """

    # bool is a subclass of int in Python,
    # so true/false would pass as 1/0.
    if isinstance(value, bool) or not isinstance(
            value,
            (int, float)
    ):
        raise ValueError(
            f"{context}: expected a number, "
            f"got {value!r}"
        )

    return value


def _text(value: Any, context: str) -> str:
    """
    Checks that a value is a non-empty text.
    """

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{context}: expected a text, "
            f"got {value!r}"
        )

    return value


def _date(value: Any, context: str) -> str:
    """
    Checks that a value is a YYYY-MM-DD date and
    returns it as text.

    Unquoted dates are read by YAML as date
    objects; they are accepted too.
    """

    if isinstance(value, date):
        return value.isoformat()

    try:
        return date.fromisoformat(
            _text(value, context)
        ).isoformat()

    except ValueError as error:
        raise ValueError(
            f"{context}: expected a YYYY-MM-DD date, "
            f"got {value!r}"
        ) from error


def _enum(
        enum_type: type[E],
        value: Any,
        context: str
) -> E:
    """
    Converts a name such as 'MONTHLY' into the
    member of an Enum.
    """

    allowed = [member.name for member in enum_type]

    if value not in allowed:
        raise ValueError(
            f"{context}: expected one of "
            f"{', '.join(allowed)}, got {value!r}"
        )

    return enum_type[value]


def _levels(
        value: Any,
        context: str
) -> list[tuple[float, float]]:
    """
    Converts [[threshold, multiplier], ...] into a
    list of pairs. Their values are validated by
    DrawdownDCA.
    """

    if not isinstance(value, list):
        raise ValueError(
            f"{context}: expected a list of "
            f"[threshold, multiplier] pairs"
        )

    levels: list[tuple[float, float]] = []

    for index, pair in enumerate(value):

        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError(
                f"{context}[{index}]: expected "
                f"[threshold, multiplier], got {pair!r}"
            )

        levels.append((
            _number(pair[0], f"{context}[{index}]"),
            _number(pair[1], f"{context}[{index}]")
        ))

    return levels


# ============================================================
# Active settings
# ============================================================

# Settings of the experiment named in active_yaml.txt,
# loaded once when the module is first imported.
SETTINGS: Final = load_settings(
    read_active_experiment()
)
