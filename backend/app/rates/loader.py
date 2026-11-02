import json
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, HttpUrl, JsonValue, ValidationError

RATE_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "rates"


class RateRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: JsonValue
    effective_from: date
    source_url: HttpUrl
    last_verified: date


class RateDataError(ValueError):
    pass


def load_rates(directory: Path = RATE_DIRECTORY) -> dict[str, RateRecord]:
    if not directory.exists():
        return {}
    if not directory.is_dir():
        raise RateDataError(f"Rates path is not a directory: {directory}")

    rates: dict[str, RateRecord] = {}
    for path in sorted(directory.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as rate_file:
                data = json.load(rate_file)
        except (OSError, json.JSONDecodeError) as error:
            raise RateDataError(f"Could not read rates file {path.name}: {error}") from error

        try:
            rates[path.stem] = RateRecord.model_validate(data)
        except ValidationError as error:
            details = "; ".join(
                f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
                for item in error.errors()
            )
            raise RateDataError(
                f"Invalid rates file {path.name}: {details}"
            ) from error

    return rates
