"""Docker-less Lambda bundling: `uv export` + manylinux wheels into the asset output."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import jsii
from aws_cdk import ILocalBundling, aws_lambda as lambda_


@jsii.implements(ILocalBundling)
class UvLocalBundling:
    def __init__(self, source_dir: Path, architecture: lambda_.Architecture) -> None:
        self._source_dir = source_dir.resolve()
        # jsii Architecture enums are not equal by identity/`==`; compare .name.
        self._platform = (
            "aarch64-manylinux2014"
            if architecture.name == "arm64"
            else "x86_64-manylinux2014"
        )

    def try_bundle(self, output_dir: str, *_args, **_kwargs) -> bool:
        output = Path(output_dir)
        try:
            with tempfile.TemporaryDirectory(prefix="uv-lambda-") as tmp:
                requirements = Path(tmp) / "requirements.txt"
                self._run(
                    [
                        "uv",
                        "export",
                        "--directory",
                        str(self._source_dir),
                        "--frozen",
                        "--no-dev",
                        "--no-editable",
                        "--no-emit-project",
                        "--no-hashes",
                        "-o",
                        str(requirements),
                    ]
                )
                # --only-binary prevents falling back to host/source builds.
                self._run(
                    [
                        "uv",
                        "pip",
                        "install",
                        "--no-installer-metadata",
                        "--no-compile-bytecode",
                        "--python-version",
                        "3.14",
                        "--python-platform",
                        self._platform,
                        "--only-binary",
                        ":all:",
                        "--target",
                        str(output),
                        "-r",
                        str(requirements),
                    ]
                )
            for path in self._source_dir.glob("*.py"):
                shutil.copy2(path, output / path.name)
            return True
        except (OSError, subprocess.CalledProcessError):
            return False

    @staticmethod
    def _run(cmd: list[str]) -> None:
        subprocess.run(cmd, check=True, capture_output=True)
