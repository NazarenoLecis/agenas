"""
Utility per gestire i percorsi del progetto.

La configurazione viene letta da config/project_config.py.
Non vengono usati YAML, classi, argparse o file __init__.py.
"""

from pathlib import Path
import importlib.util


def get_project_root():
    return Path(__file__).resolve().parents[1]


def load_project_config():
    root = get_project_root()
    config_path = root / "config" / "project_config.py"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}")
    spec = importlib.util.spec_from_file_location("project_config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_path(relative_path):
    return get_project_root() / relative_path


def get_configured_path(path_key):
    config = load_project_config()
    if path_key not in config.PATHS:
        raise KeyError(f"Missing path key: {path_key}")
    return get_project_root() / config.PATHS[path_key]


def ensure_folder(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_project_folders():
    config = load_project_config()
    root = get_project_root()
    for relative_path in config.PATHS.values():
        target = root / relative_path
        if str(target).endswith(".csv"):
            ensure_folder(target.parent)
        else:
            ensure_folder(target)
