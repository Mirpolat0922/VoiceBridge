import os
from pathlib import Path


def configure_runtime_environment(storage_dir: Path) -> None:
    cache_root = storage_dir / "runtime_cache"
    matplotlib_dir = cache_root / "matplotlib"
    xdg_cache_dir = cache_root / "xdg"

    matplotlib_dir.mkdir(parents=True, exist_ok=True)
    xdg_cache_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_dir))
    os.environ.setdefault("XDG_CACHE_HOME", str(xdg_cache_dir))
