from pathlib import Path

from flask import Blueprint, send_file

docs_bp = Blueprint("docs", __name__, url_prefix="/api")
SPEC_PATH = Path(__file__).resolve().parents[2] / "openapi.yaml"


@docs_bp.get("/openapi.yaml")
def openapi_spec():
    return send_file(
        SPEC_PATH,
        mimetype="application/yaml",
        download_name="stayease-openapi.yaml",
    )
