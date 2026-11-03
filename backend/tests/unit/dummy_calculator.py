from decimal import Decimal
from typing import Annotated, ClassVar

from app.core.base import (
    BaseCalculator,
    CalculationResult,
    CalculatorInput,
    SeoMetadata,
    SummaryItem,
)
from app.core.fields import money_field


class DummyInput(CalculatorInput):
    sample_amount: Annotated[
        Decimal,
        money_field(
            label="Sample amount",
            minimum=Decimal("1.005"),
            maximum=Decimal("100.009"),
            default=Decimal("10.00"),
            step=Decimal("0.50"),
            help_text="A test-only amount.",
        ),
    ]


class DummyCalculator(BaseCalculator[DummyInput]):
    slug: ClassVar[str] = "dummy-calculator"
    name: ClassVar[str] = "Dummy Calculator"
    category: ClassVar[str] = "Test"
    icon: ClassVar[str] = "test"
    description: ClassVar[str] = "A test-only calculator."
    seo: ClassVar[SeoMetadata] = SeoMetadata(
        title="Dummy Calculator",
        description="Test-only metadata.",
        faqs=[],
    )
    is_live: ClassVar[bool] = True
    InputModel: ClassVar[type[DummyInput]] = DummyInput

    @classmethod
    def calculate(cls, inputs: DummyInput) -> CalculationResult:
        return CalculationResult(
            summary=[
                SummaryItem(
                    key="sample_amount",
                    label="Sample amount",
                    value=inputs.sample_amount,
                    format="money",
                )
            ],
            charts=[],
            table=[],
            notes=[],
        )
