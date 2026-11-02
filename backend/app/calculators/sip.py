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


class SipInputs(CalculatorInput):
    monthly_investment: Decimal = Field(
        ge=Decimal(1),
        le=Decimal(1000000000),
        json_schema_extra={
            "label": "Monthly investment",
            "type": "currency",
            "unit": "INR",
            "help": "Amount invested at the end of each month.",
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
            "help": "Assumed annual rate, compounded monthly.",
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


class SipCalculator(BaseCalculator[SipInputs]):
    slug = "sip"
    name = "SIP Calculator"
    category = "Investment"
    icon = "chart-line"
    description = "Estimate the future value of monthly investments."
    InputModel = SipInputs

    @classmethod
    def calculate(cls, inputs: SipInputs) -> CalculationResult:
        """Assumes nominal annual return compounded monthly and deposits at each month end."""
        with localcontext() as context:
            context.prec = CALCULATION_PRECISION
            monthly_rate = inputs.annual_rate_percent / Decimal(
                100 * MONTHS_PER_YEAR
            )
            total_months = inputs.years * MONTHS_PER_YEAR

            def future_value(months: int) -> Decimal:
                if monthly_rate == 0:
                    return inputs.monthly_investment * months
                return inputs.monthly_investment * (
                    ((Decimal(1) + monthly_rate) ** months - Decimal(1))
                    / monthly_rate
                )

            labels: list[str] = []
            invested_values: list[Decimal] = []
            total_values: list[Decimal] = []
            for year in range(1, inputs.years + 1):
                labels.append(str(year))
                invested_values.append(
                    inputs.monthly_investment * year * MONTHS_PER_YEAR
                )
                total_values.append(future_value(year * MONTHS_PER_YEAR))

            total = future_value(total_months)
            principal = inputs.monthly_investment * total_months
            return build_growth_result(
                principal,
                total,
                labels,
                invested_values,
                total_values,
            )
