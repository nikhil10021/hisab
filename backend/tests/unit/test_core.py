from decimal import Decimal
from typing import Annotated

from pydantic import Field

from app.core.base import CalculationResult, CalculatorInput
from app.core.fields import money_field, rate_percent_field, years_field
from app.core.money import round_money
from app.core.result import chart, note, summary_card, table


def _numeric_branch(schema: dict[str, object]) -> dict[str, object]:
    branches = schema.get("anyOf")
    if isinstance(branches, list):
        for branch in branches:
            if isinstance(branch, dict) and branch.get("type") == "number":
                return branch
    return schema


def test_money_field_contains_form_metadata_and_constraints() -> None:
    class AmountInput(CalculatorInput):
        amount: Annotated[
            Decimal,
            money_field(
                label="Amount",
                minimum=Decimal("1"),
                maximum=Decimal("500"),
                default=Decimal("100"),
                step=Decimal("0.50"),
                help_text="Enter an amount.",
            ),
        ]

    field = AmountInput.model_fields["amount"]
    schema = AmountInput.model_json_schema(by_alias=True)["properties"]["amount"]

    assert field.title == "Amount"
    assert field.description == "Enter an amount."
    numeric_schema = _numeric_branch(schema)
    assert numeric_schema["minimum"] == 1.0
    assert numeric_schema["maximum"] == 500.0
    assert schema["default"] == "100"
    assert schema["input_type"] == "currency"
    assert schema["unit"] == "INR"
    assert schema["step"] == "0.50"
    assert AmountInput(amount=Decimal("25")).amount == Decimal("25")


def test_other_reusable_fields_set_input_type_and_unit() -> None:
    class FormInput(CalculatorInput):
        rate: Annotated[
            Decimal,
            rate_percent_field(
                label="Rate",
                minimum=Decimal("0"),
                maximum=Decimal("100"),
                default=Decimal("5"),
                step=Decimal("0.01"),
                help_text="Annual rate.",
            ),
        ]
        years: Annotated[
            int,
            years_field(
                label="Years",
                minimum=1,
                maximum=50,
                default=10,
                step=1,
                help_text="Duration in years.",
            ),
        ]

    schema = FormInput.model_json_schema()["properties"]

    rate_schema = _numeric_branch(schema["rate"])
    assert rate_schema["type"] == "number"
    assert schema["rate"]["input_type"] == "percent"
    assert schema["rate"]["unit"] == "%"
    assert schema["years"]["type"] == "integer"
    assert schema["years"]["input_type"] == "years"
    assert schema["years"]["unit"] == "years"


def test_money_rounding_is_decimal_and_half_up() -> None:
    assert round_money(Decimal("1.005")) == Decimal("1.01")
    assert round_money(Decimal("-1.005")) == Decimal("-1.01")


def test_result_builders_emit_standard_shape_and_decimal_strings() -> None:
    result = CalculationResult(
        summary=[summary_card("amount", "Amount", Decimal("12.34"), "money")],
        charts=[
            chart(
                chart_type="bar",
                title="Values",
                labels=["One"],
                series=[("Amount", [Decimal("12.34")])],
            )
        ],
        table=[table(["Amount"], [[Decimal("12.34")]])],
        notes=[note("Estimate only.")],
    )

    serialized = result.model_dump(mode="json", by_alias=True)

    assert set(serialized) == {"summary", "charts", "table", "notes"}
    assert serialized["summary"][0]["value"] == "12.34"
    assert serialized["charts"][0]["chartType"] == "bar"
    assert serialized["charts"][0]["series"][0]["values"] == ["12.34"]
    assert serialized["table"][0]["rows"] == [["12.34"]]
    assert serialized["notes"] == ["Estimate only."]


def test_input_models_allow_camel_case_aliases() -> None:
    class FormInput(CalculatorInput):
        sample_value: int = Field(alias="sampleValue")

    assert FormInput.model_validate({"sampleValue": 2}).sample_value == 2
    assert FormInput.model_validate({"sample_value": 2}).model_dump(by_alias=True) == {
        "sampleValue": 2
    }


def test_input_models_reject_extra_fields() -> None:
    class FormInput(CalculatorInput):
        sample_value: int

    try:
        FormInput.model_validate({"sample_value": 1, "unexpected": True})
    except ValueError:
        pass
    else:
        raise AssertionError("Unexpected fields must be rejected.")
