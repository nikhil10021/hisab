from fastapi.testclient import TestClient

from app.core.settings import Settings
from app.main import create_app


def test_versioned_api_replaces_legacy_unversioned_routes() -> None:
    with TestClient(
        create_app(
            Settings(),
            calculator_package="tests.unit",
        )
    ) as client:
        assert client.get("/api/health").status_code == 404
        assert client.get("/api/v1/calculators").json()[0]["slug"] == (
            "dummy-calculator"
        )
