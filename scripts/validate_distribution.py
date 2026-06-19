"""Validate release artifacts before publishing to PyPI."""

from __future__ import annotations

import sys
from email.parser import Parser
from pathlib import Path
from zipfile import ZipFile


def _fail(message: str) -> None:
    print(f"distribution validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def _metadata_path(names: list[str]) -> str:
    matches = [name for name in names if name.endswith(".dist-info/METADATA")]
    if len(matches) != 1:
        _fail(f"expected one METADATA file in wheel, found {len(matches)}")
    return matches[0]


def validate_wheel(wheel: Path) -> None:
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        if "peakbagger/browser_transport.py" not in names:
            _fail("wheel is missing peakbagger/browser_transport.py")

        metadata = Parser().parsestr(archive.read(_metadata_path(names)).decode())

    extras = set(metadata.get_all("Provides-Extra", []))
    if "browser" not in extras:
        _fail("wheel metadata is missing Provides-Extra: browser")

    requirements = metadata.get_all("Requires-Dist", [])
    has_patchright_extra = any(
        req.startswith("patchright") and 'extra == "browser"' in req for req in requirements
    )
    if not has_patchright_extra:
        _fail('wheel metadata is missing patchright dependency for extra == "browser"')


def main() -> None:
    dist_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")
    wheels = sorted(dist_dir.glob("peakbagger-*.whl"))
    if len(wheels) != 1:
        _fail(f"expected one peakbagger wheel in {dist_dir}, found {len(wheels)}")

    validate_wheel(wheels[0])
    print(f"validated {wheels[0]}")


if __name__ == "__main__":
    main()
