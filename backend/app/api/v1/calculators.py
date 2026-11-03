from decimal import Decimal
from typing import Literal, TypeGuard

from fastapi import APIRouter, Request, Response
from pydantic import Field, JsonValue, ValidationError
from pydantic_core import ErrorDetails
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.base import (
    APIModel,
    BaseCalculator,
    CalculationResult,
    CalculatorInput,
    SeoMetadata,
    camel_case,
)
from app.core.errors import AppError

InputKind = Literal[
    "number",
    "currency",
    "percent",
    "years",
    "months",
    "select",
    "date",
    "boolean",
]
INPUT_KINDS = frozenset(
    {
        "number",
        "currency",
        "percent",
        "years",
        "months",
        "select",
        "date",
        "boolean",
    }
)

router = APIRouter(prefix="/calculators")
limiter = Limiter(key_func=get_remote_address)


class CalculatorSummary(APIModel):
    slug: str
    name: str
    category: str
    icon: str
    description: str
    is_live: bool


class CalculatorInputDefinition(APIModel):
    key: str
    label: str
    type: InputKind
    default: JsonValue | None
    minimum: JsonValue | None = Field(serialization_alias="min")
    maximum: JsonValue | None = Field(serialization_alias="max")
    step: JsonValue | None
    unit: str | None
    help: str | None


class CalculatorDetail(CalculatorSummary):
    inputs: list[CalculatorInputDefinition]
    seo: SeoMetadata


def _field_constraint(
    field_metadata: list[object],
    constraint: str,
) -> object | None:
    for metadata in field_metadata:
        value = getattr(metadata, constraint, None)
        if isinstance(value, (Decimal, int, float, str)):
            return value
    return None


def _metadata_value(value: object, *, is_decimal: bool) -> JsonValue | None:
    if value is None:
        return None
    if is_decimal and isinstance(value, Decimal):
        return str(value)
    if is_decimal and isinstance(value, (int, float, str)):
        return str(value)
    if isinstance(value, (str, int, float, bool)):
        return value
    return None


def _is_input_kind(value: object) -> TypeGuard[InputKind]:
    return isinstance(value, str) and value in INPUT_KINDS


def _input_kind(value: object) -> InputKind:
    if _is_input_kind(value):
        return value
    raise ValueError(f"Unsupported calculator input type: {value}")


def _optional_string(value: object, *, name: str) -> str | None:
    if value is None or isinstance(value, str):
        return value
    raise ValueError(f"Calculator input metadata {name} must be a string.")


def calculator_summary(
    calculator: BaseCalculator[CalculatorInput],
) -> CalculatorSummary:
    return CalculatorSummary(
        slug=calculator.slug,
        name=calculator.name,
        category=calculator.category,
        icon=calculator.icon,
        description=calculator.description,
        is_live=calculator.is_live,
    )


def calculator_detail(
    calculator: BaseCalculator[CalculatorInput],
) -> CalculatorDetail:
    input_model = calculator.InputModel
    schema = input_model.model_json_schema(mode="validation", by_alias=True)
    properties = schema.get("properties", {})
    inputs: list[CalculatorInputDefinition] = []

    for field_name, field_info in input_model.model_fields.items():
        alias = (
            field_info.serialization_alias or field_info.alias or camel_case(field_name)
        )
        field_schema = properties.get(alias, {}) if isinstance(properties, dict) else {}
        if not isinstance(field_schema, dict):
            field_schema = {}
        metadata = field_info.json_schema_extra
        if not isinstance(metadata, dict):
            metadata = {}
        is_decimal = field_info.annotation is Decimal

        inputs.append(
            CalculatorInputDefinition(
                key=alias,
                label=str(metadata.get("label", field_info.title or alias)),
                type=_input_kind(metadata.get("input_type", "number")),
                default=_metadata_value(
                    field_schema.get("default"),
                    is_decimal=is_decimal,
                ),
                minimum=_metadata_value(
                    _field_constraint(field_info.metadata, "ge"),
                    is_decimal=is_decimal,
                ),
                maximum=_metadata_value(
                    _field_constraint(field_info.metadata, "le"),
                    is_decimal=is_decimal,
                ),
                step=_metadata_value(
                    metadata.get("step"),
                    is_decimal=is_decimal,
                ),
                unit=_optional_string(metadata.get("unit"), name="unit"),
                help=_optional_string(
                    metadata.get("help", field_info.description),
                    name="help",
                ),
            )
        )

    return CalculatorDetail(
        **calculator_summary(calculator).model_dump(),
        inputs=inputs,
        seo=calculator.seo,
    )


def get_calculator(
    request: Request,
    slug: str,
) -> BaseCalculator[CalculatorInput]:
    calculators: dict[str, BaseCalculator[CalculatorInput]] = (
        request.app.state.calculators
    )
    calculator = calculators.get(slug)
    if calculator is None:
        raise AppError(
            code="CALCULATOR_NOT_FOUND",
            message="The requested calculator was not found.",
            status_code=404,
        )
    return calculator


def _friendly_validation_message(error: ErrorDetails) -> str:
    error_type = error.get("type")
    if error_type == "missing":
        return "This field is required."
    if error_type == "decimal_parsing":
        return "Enter a valid number."
    if error_type == "extra_forbidden":
        return "This field is not recognized."
    if error_type == "greater_than_equal":
        minimum = _validation_limit(error, "ge")
        return f"Must be at least {minimum}." if minimum else "Below the minimum."
    if error_type == "less_than_equal":
        maximum = _validation_limit(error, "le")
        return f"Must be no more than {maximum}." if maximum else "Above the maximum."
    return "Please enter a valid value."


def _validation_limit(error: ErrorDetails, key: str) -> str | None:
    context = error.get("ctx")
    if not isinstance(context, dict):
        return None
    limit = context.get(key)
    if isinstance(limit, Decimal):
        return str(limit)
    if isinstance(limit, (str, int, float)):
        return str(limit)
    return None


@router.get("", response_model=list[CalculatorSummary])
@limiter.limit("60/minute")
def list_calculators(
    request: Request,
    response: Response,
) -> list[CalculatorSummary]:
    response.headers["Cache-Control"] = (
        f"public, max-age={request.app.state.settings.metadata_cache_seconds}"
    )
    calculators: dict[str, BaseCalculator[CalculatorInput]] = (
        request.app.state.calculators
    )
    return [calculator_summary(calculators[slug]) for slug in sorted(calculators)]


@router.get("/{slug}", response_model=CalculatorDetail)
@limiter.limit("60/minute")
def read_calculator(
    request: Request,
    slug: str,
    response: Response,
) -> CalculatorDetail:
    response.headers["Cache-Control"] = (
        f"public, max-age={request.app.state.settings.metadata_cache_seconds}"
    )
    return calculator_detail(get_calculator(request, slug))


@router.post("/{slug}", response_model=CalculationResult)
@limiter.limit("60/minute")
def calculate(
    request: Request,
    slug: str,
    payload: dict[str, JsonValue],
) -> CalculationResult:
    calculator = get_calculator(request, slug)

    try:
        inputs = calculator.InputModel.model_validate(payload)
    except ValidationError as error:
        details: list[dict[str, str]] = []
        for item in error.errors():
            path = str(item["loc"][0]) if item["loc"] else "input"
            field = calculator.InputModel.model_fields.get(path)
            alias = (
                field.serialization_alias or field.alias or camel_case(path)
                if field is not None
                else camel_case(path)
            )
            details.append(
                {
                    "field": alias,
                    "message": _friendly_validation_message(item),
                }
            )
        raise AppError(
            code="VALIDATION_ERROR",
            message="Please check the highlighted input fields.",
            details=details,
            status_code=422,
        ) from error

    return calculator.calculate(inputs)
