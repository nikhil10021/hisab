from decimal import Decimal

from app.calculators.base import CalculationResult
from app.calculators.lumpsum import LumpsumCalculator, LumpsumInputs
from app.calculators.sip import SipCalculator, SipInputs


def summary_values(result: CalculationResult) -> dict[str, Decimal | str]:
    return {item.key: item.value for item in result.summary}


def test_sip_known_value_uses_month_end_contributions() -> None:
    result = SipCalculator.calculate(
        SipInputs(
            monthly_investment=Decimal(100),
            annual_rate_percent=Decimal(12),
            years=1,
        )
    )

    assert summary_values(result) == {
        "invested_amount": Decimal("1200.00"),
        "estimated_returns": Decimal("68.25"),
        "total_value": Decimal("1268.25"),
    }
    assert result.charts[1].labels == ["1"]
    assert result.charts[1].series[0].values == [Decimal("1200.00")]
    assert result.charts[1].series[1].values == [Decimal("1268.25")]


def test_lumpsum_known_value_uses_monthly_compounding() -> None:
    result = LumpsumCalculator.calculate(
        LumpsumInputs(
            investment_amount=Decimal(1000),
            annual_rate_percent=Decimal(12),
            years=1,
        )
    )

    assert summary_values(result) == {
        "invested_amount": Decimal("1000.00"),
        "estimated_returns": Decimal("126.83"),
        "total_value": Decimal("1126.83"),
    }
    assert result.charts[1].series[0].values == [Decimal("1000.00")]
    assert result.charts[1].series[1].values == [Decimal("1126.83")]


def test_sip_zero_rate_returns_only_investments() -> None:
    result = SipCalculator.calculate(
        SipInputs(
            monthly_investment=Decimal(100),
            annual_rate_percent=Decimal(0),
            years=1,
        )
    )

    assert summary_values(result)["total_value"] == Decimal("1200.00")


def test_calculators_support_their_maximum_valid_inputs() -> None:
    sip_result = SipCalculator.calculate(
        SipInputs(
            monthly_investment=Decimal(1000000000),
            annual_rate_percent=Decimal(100),
            years=100,
        )
    )
    lumpsum_result = LumpsumCalculator.calculate(
        LumpsumInputs(
            investment_amount=Decimal(1000000000),
            annual_rate_percent=Decimal(100),
            years=100,
        )
    )

    assert summary_values(sip_result)["total_value"] > Decimal(0)
    assert summary_values(lumpsum_result)["total_value"] > Decimal(0)
