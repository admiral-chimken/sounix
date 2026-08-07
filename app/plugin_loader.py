import importlib.util
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
PLUGINS_DIR = PROJECT_DIR / "plugins"


def load_plugins():
    plugins = {}

    if not PLUGINS_DIR.exists():
        return plugins

    for plugin_file in PLUGINS_DIR.glob("*.py"):
        if plugin_file.name.startswith("_"):
            continue

        try:
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem,
                plugin_file,
            )

            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            command = getattr(module, "COMMAND", None)
            run = getattr(module, "run", None)

            if command and callable(run):
                plugins[command.lower()] = run

        except Exception as error:
            print(
                f"Sounix plugin error in {plugin_file.name}: {error}"
            )

    return plugins
