from abc import ABC, abstractmethod
from decimal import Decimal
from typing import ClassVar, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict

InputT = TypeVar("InputT", bound="CalculatorInput")


def camel_case(value: str) -> str:
    first, *remaining = value.split("_")
    return first + "".join(part.capitalize() for part in remaining)


class APIModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=camel_case,
        extra="forbid",
        populate_by_name=True,
        serialize_by_alias=True,
    )


class CalculatorInput(APIModel):
    model_config = ConfigDict(
        alias_generator=camel_case,
        extra="forbid",
        populate_by_name=True,
        serialize_by_alias=True,
    )


class FAQ(APIModel):
    question: str
    answer: str


class SeoMetadata(APIModel):
    title: str
    description: str
    faqs: list[FAQ]


SummaryFormat = Literal["money", "percent", "number", "text"]
ChartType = Literal["pie", "line", "bar", "area"]


class SummaryItem(APIModel):
    key: str
    label: str
    value: Decimal | str
    format: SummaryFormat


class ChartSeries(APIModel):
    name: str
    values: list[Decimal]


class Chart(APIModel):
    chart_type: ChartType
    title: str
    labels: list[str]
    series: list[ChartSeries]


class TableResult(APIModel):
    columns: list[str]
    rows: list[list[Decimal | int | str]]


class CalculationResult(APIModel):
    summary: list[SummaryItem]
    charts: list[Chart]
    table: list[TableResult]
    notes: list[str]


class BaseCalculator(ABC, Generic[InputT]):
    slug: ClassVar[str]
    name: ClassVar[str]
    category: ClassVar[str]
    icon: ClassVar[str]
    description: ClassVar[str]
    seo: ClassVar[SeoMetadata]
    is_live: ClassVar[bool] = False
    InputModel: ClassVar[type[InputT]]

    @classmethod
    @abstractmethod
    def calculate(cls, inputs: InputT) -> CalculationResult:
        raise NotImplementedError
