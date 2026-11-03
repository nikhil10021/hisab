from decimal import Decimal
from typing import Literal

from app.core.base import (
    CalculationResult,
    Chart,
    ChartSeries,
    SummaryItem,
    TableResult,
)

SummaryFormat = Literal["money", "percent", "number", "text"]
ChartType = Literal["pie", "line", "bar", "area"]
TableValue = Decimal | int | str


def summary_card(
    key: str,
    label: str,
    value: Decimal | str,
    value_format: SummaryFormat,
) -> SummaryItem:
    return SummaryItem(key=key, label=label, value=value, format=value_format)


def chart(
    *,
    chart_type: ChartType,
    title: str,
    labels: list[str],
    series: list[tuple[str, list[Decimal]]],
) -> Chart:
    return Chart(
        chart_type=chart_type,
        title=title,
        labels=labels,
        series=[
            ChartSeries(name=series_name, values=values)
            for series_name, values in series
        ],
    )


def table(columns: list[str], rows: list[list[TableValue]]) -> TableResult:
    return TableResult(columns=columns, rows=rows)


def note(text: str) -> str:
    return text


def calculation_result(
    *,
    summary: list[SummaryItem],
    charts: list[Chart],
    tables: list[TableResult],
    notes: list[str],
) -> CalculationResult:
    return CalculationResult(
        summary=summary,
        charts=charts,
        table=tables,
        notes=notes,
    )
