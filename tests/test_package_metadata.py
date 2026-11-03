"""Package-identity consistency tests.

The package declares its version and identity in seven places: the Python
package, the mission adapter's provenance string, ``pyproject.toml``,
``manuscript/config.yaml``, ``CITATION.cff``, ``.zenodo.json``, and
``codemeta.json``. Nothing keeps them in step automatically, and they had
already drifted (the code said 0.2.0 while four metadata files still said
0.1.0, so every provenance record disagreed with every citation).

These tests read the real files and fail on divergence. They are cheap and they
catch a class of defect that no amount of unit testing on ``src/`` would.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

import goldfinger
from goldfinger.mission import MissionProvider

_PKG_ROOT = Path(__file__).resolve().parents[1]
_ORCID = "0000-0001-6232-9096"


def _pyproject_version() -> str:
    text = (_PKG_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    assert match, "pyproject.toml declares no version"
    return match.group(1)


def _cff() -> dict[str, object]:
    data = yaml.safe_load((_PKG_ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _json(name: str) -> dict[str, object]:
    data = json.loads((_PKG_ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _manuscript_config() -> dict[str, object]:
    data = yaml.safe_load((_PKG_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


@pytest.mark.parametrize(
    ("source", "version"),
    [
        ("pyproject.toml", _pyproject_version()),
        ("CITATION.cff", str(_cff()["version"])),
        (".zenodo.json", str(_json(".zenodo.json")["version"])),
        ("codemeta.json", str(_json("codemeta.json")["version"])),
        ("manuscript/config.yaml", str(dict(_manuscript_config()["paper"])["version"])),  # type: ignore[arg-type]
    ],
)
def test_declared_version_matches_the_package(source: str, version: str) -> None:
    assert version == goldfinger.__version__, (
        f"{source} declares version {version!r} but goldfinger.__version__ is "
        f"{goldfinger.__version__!r}"
    )


def test_mission_provenance_version_matches_the_package() -> None:
    """The provenance string a mission stamps must carry the package version."""
    from goldfinger.mission import _SUBPACKAGE_VERSION

    assert f"goldfinger.mission/{goldfinger.__version__}" == _SUBPACKAGE_VERSION


def test_executed_outcome_records_the_current_version_and_seed() -> None:
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    assert outcome.provenance.package_version.endswith(goldfinger.__version__)
    assert outcome.provenance.seed == goldfinger.MISSION_SEED


@pytest.mark.parametrize(
    ("source", "orcid"),
    [
        ("CITATION.cff", str(dict(_cff()["authors"][0])["orcid"])),  # type: ignore[index]
        (".zenodo.json", str(dict(_json(".zenodo.json")["creators"][0])["orcid"])),  # type: ignore[index]
    ],
)
def test_author_orcid_is_consistent(source: str, orcid: str) -> None:
    assert _ORCID in orcid, f"{source} carries an unexpected ORCID: {orcid!r}"


def test_publisher_metadata_declares_no_fabricated_identifiers() -> None:
    """The declared repository is the real one; no DOI is declared anywhere."""
    zenodo = _json(".zenodo.json")
    codemeta = _json("codemeta.json")
    assert "doi" not in zenodo, "no DOI may be declared before a deposit exists"
    assert codemeta.get("codeRepository") == "https://github.com/docxology/bond-goldfinger", (
        "codemeta.json must name the repository this package is pushed to"
    )
    config = _manuscript_config()
    publication = config.get("publication")
    assert isinstance(publication, dict)
    assert "doi" not in publication, "manuscript config must not carry a fabricated DOI"


def test_film_identity_is_single_sourced() -> None:
    assert goldfinger.FILM == MissionProvider.film == "goldfinger"
    assert goldfinger.CODENAME == "GRAND SLAM"
