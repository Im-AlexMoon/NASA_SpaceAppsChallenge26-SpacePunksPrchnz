"""Live PSI API checks. Run with: pytest -m integration"""

import pytest

from flamesafe.ingestion.psi_client import PSIClient

pytestmark = pytest.mark.integration


def test_live_search_returns_combustion_records():
    client = PSIClient()
    combustion = client.list_investigations("Combustion Science")
    assert len(combustion) > 0
    assert all(s["Accession"].startswith("PSI-") for s in combustion)


def test_live_unknown_file_is_404():
    assert PSIClient().probe("PSI-69", "__flamesafe_nonexistent__.csv") == 404
