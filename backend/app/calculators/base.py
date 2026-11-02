from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal, localcontext
from typing import ClassVar, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict

InputT = TypeVar("InputT", bound=BaseModel)
SummaryFormat = Literal["currency", "percent", "number", "text"]
ChartType = Literal["pie", "line", "bar", "area"]
CENT = Decimal("0.01")
CALCULATION_PRECISION = 60
MONTHS_PER_YEAR = 12


class CalculatorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SummaryItem(BaseModel):
    key: str
    label: str
    value: Decimal | str
    format: SummaryFormat


class ChartSeries(BaseModel):
    name: str
    values: list[Decimal]


class Chart(BaseModel):
    type: ChartType
    title: str
    labels: list[str]
    series: list[ChartSeries]


class TableResult(BaseModel):
    columns: list[str]
    rows: list[list[str | Decimal]]


class CalculationResult(BaseModel):
    summary: list[SummaryItem]
    charts: list[Chart]
    table: TableResult | None = None


class BaseCalculator(ABC, Generic[InputT]):
    slug: ClassVar[str]
    name: ClassVar[str]
    category: ClassVar[str]
    icon: ClassVar[str]
    description: ClassVar[str]
    InputModel: ClassVar[type[InputT]]

    @classmethod
    @abstractmethod
    def calculate(cls, inputs: InputT) -> CalculationResult:
        raise NotImplementedError


def round_currency(value: Decimal) -> Decimal:
    with localcontext() as context:
        context.prec = max(
            context.prec,
            len(value.as_tuple().digits) + 2,
            value.adjusted() + 3,
        )
        return value.quantize(CENT, rounding=ROUND_HALF_UP)


def build_growth_result(
    principal: Decimal,
    total_value: Decimal,
    labels: list[str],
    invested_values: list[Decimal],
    total_values: list[Decimal],
) -> CalculationResult:
    invested = round_currency(principal)
    returns = round_currency(total_value - principal)
    total = round_currency(total_value)

    return CalculationResult(
        summary=[
            SummaryItem(
                key="invested_amount",
                label="Invested amount",
                value=invested,
                format="currency",
            ),
            SummaryItem(
                key="estimated_returns",
                label="Estimated returns",
                value=returns,
                format="currency",
            ),
            SummaryItem(
                key="total_value",
                label="Total value",
                value=total,
                format="currency",
            ),
        ],
        charts=[
            Chart(
                type="pie",
                title="Invested amount vs estimated returns",
                labels=["Invested amount", "Estimated returns"],
                series=[
                    ChartSeries(
                        name="Value",
                        values=[invested, returns],
                    )
                ],
            ),
            Chart(
                type="area",
                title="Year-wise growth",
                labels=labels,
                series=[
                    ChartSeries(
                        name="Invested amount",
                        values=[round_currency(value) for value in invested_values],
                    ),
                    ChartSeries(
                        name="Total value",
                        values=[round_currency(value) for value in total_values],
                    ),
                ],
            ),
        ],
    )
