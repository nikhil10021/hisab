from decimal import Decimal
from typing import Literal

from pydantic import JsonValue
from pydantic.fields import FieldInfo

FieldKind = Literal["number", "currency", "percent", "years", "months"]


def _numeric_field(
    *,
    field_type: FieldKind,
    label: str,
    minimum: Decimal | int,
    maximum: Decimal | int,
    default: Decimal | int,
    step: Decimal | int,
    unit: str,
    help_text: str,
) -> FieldInfo:
    step_value: JsonValue = str(step) if isinstance(step, Decimal) else step
    field_metadata: dict[str, JsonValue] = {
        "input_type": field_type,
        "unit": unit,
        "step": step_value,
    }
    return FieldInfo.from_field(
        default=default,
        ge=minimum,
        le=maximum,
        title=label,
        description=help_text,
        json_schema_extra=field_metadata,
    )


def money_field(
    *,
    label: str,
    minimum: Decimal,
    maximum: Decimal,
    default: Decimal,
    step: Decimal,
    help_text: str,
) -> FieldInfo:
    return _numeric_field(
        field_type="currency",
        label=label,
        minimum=minimum,
        maximum=maximum,
        default=default,
        step=step,
        unit="INR",
        help_text=help_text,
    )


def rate_percent_field(
    *,
    label: str,
    minimum: Decimal,
    maximum: Decimal,
    default: Decimal,
    step: Decimal,
    help_text: str,
) -> FieldInfo:
    return _numeric_field(
        field_type="percent",
        label=label,
        minimum=minimum,
        maximum=maximum,
        default=default,
        step=step,
        unit="%",
        help_text=help_text,
    )


def years_field(
    *,
    label: str,
    minimum: int,
    maximum: int,
    default: int,
    step: int,
    help_text: str,
) -> FieldInfo:
    return _numeric_field(
        field_type="years",
        label=label,
        minimum=minimum,
        maximum=maximum,
        default=default,
        step=step,
        unit="years",
        help_text=help_text,
    )
