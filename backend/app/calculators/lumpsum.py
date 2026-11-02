from decimal import Decimal, localcontext

from pydantic import Field

from app.calculators.base import (
    CALCULATION_PRECISION,
    MONTHS_PER_YEAR,
    BaseCalculator,
    CalculationResult,
    CalculatorInput,
    build_growth_result,
)


class LumpsumInputs(CalculatorInput):
    investment_amount: Decimal = Field(
        ge=Decimal(1),
        le=Decimal(1000000000),
        json_schema_extra={
            "label": "Investment amount",
            "type": "currency",
            "unit": "INR",
            "help": "One-time amount invested at the start.",
            "step": 1,
        },
    )
    annual_rate_percent: Decimal = Field(
        ge=Decimal(0),
        le=Decimal(100),
        json_schema_extra={
            "label": "Expected annual return",
            "type": "percent",
            "unit": "%",
            "help": "Assumed nominal annual rate, compounded monthly.",
            "step": Decimal("0.01"),
        },
    )
    years: int = Field(
        ge=1,
        le=100,
        json_schema_extra={
            "label": "Investment period",
            "type": "years",
            "unit": "years",
            "help": "Whole number of years to invest.",
            "step": 1,
        },
    )


class LumpsumCalculator(BaseCalculator[LumpsumInputs]):
    slug = "lumpsum"
    name = "Lumpsum Calculator"
    category = "Investment"
    icon = "coins"
    description = "Estimate the future value of a one-time investment."
    InputModel = LumpsumInputs

    @classmethod
    def calculate(cls, inputs: LumpsumInputs) -> CalculationResult:
        """Assumes one initial investment and a nominal annual return compounded monthly."""
        with localcontext() as context:
            context.prec = CALCULATION_PRECISION
            monthly_rate = inputs.annual_rate_percent / Decimal(
                100 * MONTHS_PER_YEAR
            )
            labels: list[str] = []
            invested_values: list[Decimal] = []
            total_values: list[Decimal] = []

            for year in range(1, inputs.years + 1):
                labels.append(str(year))
                invested_values.append(inputs.investment_amount)
                total_values.append(
                    inputs.investment_amount
                    * (Decimal(1) + monthly_rate) ** (year * MONTHS_PER_YEAR)
                )

            total = total_values[-1]
            return build_growth_result(
                inputs.investment_amount,
                total,
                labels,
                invested_values,
                total_values,
            )
