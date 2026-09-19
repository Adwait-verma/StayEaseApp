import re
from pathlib import Path

import yaml


def _openapi_path(rule: str) -> str:
    return re.sub(r"<(?:(?:int|string):)?([^>]+)>", r"{\1}", rule)


def test_openapi_contract_is_served(client):
    response = client.get("/api/openapi.yaml")

    assert response.status_code == 200
    assert response.mimetype == "application/yaml"
    assert response.get_data(as_text=True).startswith("openapi: 3.1.0")


def test_openapi_contract_covers_every_api_operation(app):
    spec_path = Path(__file__).resolve().parents[1] / "openapi.yaml"
    contract = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    documented = {
        (method.upper(), path)
        for path, operations in contract["paths"].items()
        for method in operations
        if method.lower() in {"get", "post", "put", "patch", "delete"}
    }
    implemented = {
        (method, _openapi_path(rule.rule))
        for rule in app.url_map.iter_rules()
        if rule.rule.startswith("/api/")
        for method in rule.methods
        if method not in {"HEAD", "OPTIONS"}
    }

    assert documented == implemented
