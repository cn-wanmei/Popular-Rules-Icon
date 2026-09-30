from __future__ import annotations

import importlib.util
from pathlib import Path


def test_release_writer_imports_real_renderer() -> None:
    path = Path(__file__).parents[2] / "scripts" / "build_release_from_state.py"
    spec = importlib.util.spec_from_file_location("release_writer", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.render_all_styles)
