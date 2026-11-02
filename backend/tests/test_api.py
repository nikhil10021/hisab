from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(
        create_app(
            Settings(
                environment="dev",
                allowed_origins="http://localhost:5173",
            )
        )
    ) as test_client:
        yield test_client


def test_health_and_calculator_routes(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}

    calculators_response = client.get("/api/calculators")
    assert calculators_response.status_code == 200
    calculators = calculators_response.json()
    assert {item["slug"] for item in calculators} == {"sip", "lumpsum"}
    assert set(calculators[0]) == {
        "slug",
        "name",
        "category",
        "icon",
        "description",
    }

    detail_response = client.get("/api/calculators/sip")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["slug"] == "sip"
    assert detail["last_updated"] is None
    assert [item["key"] for item in detail["inputs"]] == [
        "monthly_investment",
        "annual_rate_percent",
        "years",
    ]
    assert detail["inputs"][0]["type"] == "currency"
    assert detail["inputs"][0]["min"] == 1

    calculation_response = client.post(
        "/api/calculators/sip",
        json={
            "monthly_investment": "100",
            "annual_rate_percent": "12",
            "years": 1,
        },
    )
    assert calculation_response.status_code == 200
    assert calculation_response.json()["summary"][2]["value"] == "1268.25"
    assert calculation_response.json()["charts"][0]["type"] == "pie"
    assert calculation_response.json()["charts"][1]["type"] == "area"


def test_post_returns_friendly_validation_error(client: TestClient) -> None:
    response = client.post(
        "/api/calculators/sip",
        json={
            "monthly_investment": "0",
            "annual_rate_percent": "12",
            "years": 1,
        },
    )

    assert response.status_code == 422
    issue = response.json()["detail"][0]
    assert issue["key"] == "monthly_investment"
    assert "greater than or equal to" in issue["message"]
    assert "input" not in issue


def test_unknown_calculator_returns_404(client: TestClient) -> None:
    assert client.get("/api/calculators/unknown").status_code == 404
    assert (
        client.post("/api/calculators/unknown", json={}).status_code
        == 404
    )


def test_production_hides_api_documentation() -> None:
    with TestClient(create_app(Settings(environment="prod"))) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404
        assert client.get("/api/health").status_code == 200


def test_settings_load_environment_and_cors_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        "https://hisab.example, https://admin.hisab.example",
    )

    settings = Settings(_env_file=None)

    assert settings.environment == "prod"
    assert settings.cors_origins == [
        "https://hisab.example",
        "https://admin.hisab.example",
    ]
