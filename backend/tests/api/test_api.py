from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.settings import Settings
from app.main import create_app
from tests.unit.dummy_calculator import DummyCalculator


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(
        create_app(
            Settings(environment="dev"),
            calculator_package="tests.unit",
        )
    ) as test_client:
        yield test_client


def test_health_and_only_versioned_routes_are_available(
    client: TestClient,
) -> None:
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    assert client.get("/api/health").status_code == 404
    assert client.get("/health").status_code == 404


def test_calculator_list_and_detail_use_camel_case_and_live_only(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/calculators")

    assert response.status_code == 200
    assert response.headers["cache-control"].startswith("public")
    calculators = response.json()
    assert [item["slug"] for item in calculators] == ["dummy-calculator"]
    assert calculators[0]["isLive"] is True

    detail_response = client.get("/api/v1/calculators/dummy-calculator")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["seo"]["title"] == "Dummy Calculator"
    assert detail["inputs"] == [
        {
            "key": "sampleAmount",
            "label": "Sample amount",
            "type": "currency",
            "default": "10.00",
            "min": "1.005",
            "max": "100.009",
            "step": "0.50",
            "unit": "INR",
            "help": "A test-only amount.",
        }
    ]


def test_calculate_accepts_camel_case_and_returns_decimal_strings(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/calculators/dummy-calculator",
        json={"sampleAmount": "42.25"},
    )

    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"summary", "charts", "table", "notes"}
    assert result["summary"][0]["value"] == "42.25"


def test_calculate_returns_human_friendly_validation_error(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/calculators/dummy-calculator",
        json={"sampleAmount": "0"},
    )

    assert response.status_code == 422
    error = response.json()
    assert set(error) == {"code", "message", "details"}
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == "sampleAmount"
    assert error["details"][0]["message"] == "Must be at least 1.005."


def test_unknown_calculator_uses_standard_error_shape(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/calculators/not-found-calculator")

    assert response.status_code == 404
    assert set(response.json()) == {"code", "message", "details"}
    assert response.json()["code"] == "CALCULATOR_NOT_FOUND"


def test_production_disables_openapi_and_documentation() -> None:
    with TestClient(
        create_app(
            Settings(environment="prod"),
            calculator_package="tests.unit",
        )
    ) as production_client:
        assert production_client.get("/docs").status_code == 404
        assert production_client.get("/redoc").status_code == 404
        assert production_client.get("/openapi.json").status_code == 404
        assert production_client.get("/api/v1/health").status_code == 200


def test_cors_uses_only_configured_origins() -> None:
    with TestClient(
        create_app(
            Settings(
                environment="dev",
                allowed_origins="https://hisab.example",
            ),
            calculator_package="tests.unit",
        )
    ) as cors_client:
        allowed = cors_client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://hisab.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        denied = cors_client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://untrusted.example",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert allowed.headers["access-control-allow-origin"] == "https://hisab.example"
    assert "access-control-allow-origin" not in denied.headers


def test_request_size_limit_returns_standard_error() -> None:
    with TestClient(
        create_app(
            Settings(max_request_size_bytes=32),
            calculator_package="tests.unit",
        )
    ) as limited_client:
        response = limited_client.post(
            "/api/v1/calculators/dummy-calculator",
            content=b'{"padding":"' + b"x" * 100 + b'"}',
            headers={"content-type": "application/json"},
        )

    assert response.status_code == 413
    assert response.json()["code"] == "REQUEST_TOO_LARGE"


def test_rate_limit_returns_standard_error() -> None:
    with TestClient(
        create_app(
            Settings(),
            calculator_package="tests.unit",
        )
    ) as limited_client:
        responses = [limited_client.get("/api/v1/health") for _ in range(61)]

    assert responses[-1].status_code == 429
    assert responses[-1].json()["code"] == "RATE_LIMIT_EXCEEDED"


def test_unexpected_errors_do_not_expose_exception_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_secret_error(
        cls: type[DummyCalculator],
        inputs: object,
    ) -> None:
        raise RuntimeError("internal detail")

    monkeypatch.setattr(
        DummyCalculator,
        "calculate",
        classmethod(raise_secret_error),
    )
    with TestClient(
        create_app(Settings(), calculator_package="tests.unit"),
        raise_server_exceptions=False,
    ) as error_client:
        response = error_client.post(
            "/api/v1/calculators/dummy-calculator",
            json={"sampleAmount": "42"},
        )

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert "internal detail" not in response.text
