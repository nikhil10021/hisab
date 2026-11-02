import json
from pathlib import Path

import pytest

from app.rates.loader import RateDataError, load_rates


def test_rate_loader_validates_and_loads_rate(tmp_path: Path) -> None:
    (tmp_path / "example.json").write_text(
        json.dumps(
            {
                "value": "0.05",
                "effective_from": "2026-01-01",
                "source_url": "https://example.com/rates",
                "last_verified": "2026-01-02",
            }
        ),
        encoding="utf-8",
    )

    rates = load_rates(tmp_path)

    assert rates["example"].value == "0.05"
    assert rates["example"].effective_from.isoformat() == "2026-01-01"


def test_rate_loader_rejects_bad_json(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text("{ invalid", encoding="utf-8")

    with pytest.raises(RateDataError, match="Could not read rates file broken.json"):
        load_rates(tmp_path)


def test_rate_loader_rejects_missing_required_field(tmp_path: Path) -> None:
    (tmp_path / "missing.json").write_text(
        json.dumps(
            {
                "value": "0.05",
                "effective_from": "2026-01-01",
                "source_url": "https://example.com/rates",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        RateDataError,
        match="Invalid rates file missing.json: last_verified",
    ):
        load_rates(tmp_path)


def test_rate_loader_rejects_invalid_fields(tmp_path: Path) -> None:
    (tmp_path / "invalid.json").write_text(
        json.dumps(
            {
                "value": "0.05",
                "effective_from": "not-a-date",
                "source_url": "not-a-url",
                "last_verified": "2026-01-02",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RateDataError, match="Invalid rates file invalid.json"):
        load_rates(tmp_path)
