"""TC-09 / AC-06: imported data persists across application restart using the
same SQLite file, without recomputing or losing any rows."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import VALID_CSV, make_settings


def test_data_persists_across_simulated_restart(tmp_path):
    db_path = tmp_path / "persist.db"
    settings = make_settings(db_path)

    app1 = create_app(settings)
    client1 = TestClient(app1)
    response = client1.post(
        "/api/datasets/import", files={"file": ("valid.csv", VALID_CSV, "text/csv")}
    )
    assert response.status_code == 201
    dataset_id = response.json()["dataset_id"]
    app1.state.engine.dispose()  # simulate process shutdown

    # "Restart": build a brand new app/engine bound to the same database file.
    app2 = create_app(make_settings(db_path))
    client2 = TestClient(app2)

    summary_response = client2.get(f"/api/datasets/{dataset_id}/summary")
    assert summary_response.status_code == 200
    body = summary_response.json()
    assert body["lead_count"] == 170  # 100 + 50 + 20 from VALID_CSV
    assert body["qualified_lead_count"] == 15  # 10 + 5 + 0

    campaigns_response = client2.get(f"/api/datasets/{dataset_id}/campaigns")
    assert len(campaigns_response.json()["campaigns"]) == 3
    app2.state.engine.dispose()
