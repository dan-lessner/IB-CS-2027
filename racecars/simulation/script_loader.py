"""Load student driver scripts and track generator scripts at runtime."""

import logging
import os
import sys
import importlib.util

_LOGGER = logging.getLogger("racecars.script_loader")


class ScriptInfo:
    def __init__(self, name: str, path: str, file_name: str):
        # Metadata plus a cached Auto class once imported.
        self.name = name
        self.path = path
        self.file_name = file_name
        self.auto_class = None


class TrackGeneratorInfo:
    def __init__(self, generator_id: str, name: str, path: str, file_name: str):
        # Metadata for a track generator script plus a cached module once imported.
        self.id = generator_id
        self.name = name
        self.path = path
        self.file_name = file_name
        self.module = None


def load_scripts_from_folder(folder_path: str):
    # Discover candidate files first, then convert each into ScriptInfo objects.
    files = _find_script_files(folder_path)
    scripts = []

    for path in files:
        file_name = os.path.basename(path)
        script_name = _filename_without_extension(file_name)
        scripts.append(ScriptInfo(script_name, path, file_name))

    return scripts


def load_auto_class(script_info: ScriptInfo):
    # Lazy import: only import a script when it is actually selected as a controller.
    if script_info is None:
        _LOGGER.warning("load_auto_class() was called with script_info=None.")
        return None
    if script_info.auto_class is not None:
        return script_info.auto_class

    _ensure_repo_root_on_sys_path()
    module_name = _module_name_from_path(script_info.path)
    try:
        module = _load_module(script_info.path, module_name)
    except Exception as ex:
        _LOGGER.exception(
            "Failed to import script '%s' from '%s' (%s: %s).",
            script_info.name,
            script_info.path,
            type(ex).__name__,
            ex
        )
        return None
    if module is None:
        _LOGGER.warning("Script module could not be loaded for '%s'.", script_info.path)
        return None
    if not hasattr(module, "Auto"):
        _LOGGER.warning("Script '%s' does not define required class Auto.", script_info.path)
        return None

    auto_class = getattr(module, "Auto")
    script_info.auto_class = auto_class
    return auto_class


def load_track_generators_from_folder(folder_path: str):
    # Discover files, import each, and build TrackGeneratorInfo for valid generators.
    files = _find_script_files(folder_path)
    generators = []

    _ensure_repo_root_on_sys_path()
    for path in files:
        file_name = os.path.basename(path)
        module_name = _module_name_from_path(path)
        try:
            module = _load_module(path, module_name)
        except Exception as ex:
            _LOGGER.exception(
                "Failed to import track generator '%s' (%s: %s).", path, type(ex).__name__, ex
            )
            continue
        if module is None:
            _LOGGER.warning("Track generator module could not be loaded: '%s'.", path)
            continue
        if not hasattr(module, "META"):
            _LOGGER.warning("Track generator '%s' does not define required META dict.", path)
            continue
        if not hasattr(module, "generate_track"):
            _LOGGER.warning("Track generator '%s' does not define required generate_track().", path)
            continue

        meta = getattr(module, "META")
        generator_id = meta.get("id", _filename_without_extension(file_name))
        generator_name = meta.get("name", generator_id)

        info = TrackGeneratorInfo(generator_id, generator_name, path, file_name)
        info.module = module
        generators.append(info)

    return generators


def load_track_generator_module(generator_info: TrackGeneratorInfo):
    # Module is loaded eagerly in load_track_generators_from_folder; this is a no-op if cached.
    if generator_info is None:
        _LOGGER.warning("load_track_generator_module() was called with generator_info=None.")
        return None
    if generator_info.module is not None:
        return generator_info.module

    _ensure_repo_root_on_sys_path()
    module_name = _module_name_from_path(generator_info.path)
    try:
        module = _load_module(generator_info.path, module_name)
    except Exception as ex:
        _LOGGER.exception(
            "Failed to import track generator '%s' (%s: %s).",
            generator_info.path, type(ex).__name__, ex
        )
        return None
    if module is None:
        _LOGGER.warning("Track generator module could not be loaded: '%s'.", generator_info.path)
        return None

    generator_info.module = module
    return module


def _find_script_files(folder_path: str):
    # Keep list deterministic to make the UI order stable.
    if not os.path.isdir(folder_path):
        _LOGGER.warning("Scripts folder not found: %s", folder_path)
        return []

    files = []
    names = os.listdir(folder_path)
    for name in names:
        if _is_python_file(name) and not name.startswith("_"):
            full_path = os.path.join(folder_path, name)
            files.append(full_path)

    files.sort()
    return files


def _is_python_file(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(".py")


def _load_module(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        _LOGGER.warning("Import spec creation failed for script '%s'.", path)
        return None
    loader = spec.loader
    if loader is None:
        _LOGGER.warning("Import loader creation failed for script '%s'.", path)
        return None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def _module_name_from_path(path: str) -> str:
    base = os.path.basename(path)
    name = _filename_without_extension(base)
    # Using full normalized path keeps module name stable and unique per file.
    normalized = os.path.abspath(path).lower()
    suffix = "".join(ch if ch.isalnum() else "_" for ch in normalized)
    return "script_" + name + "_" + suffix


def _filename_without_extension(name: str) -> str:
    dot_index = name.rfind(".")

    if dot_index <= 0:
        return name

    return name[:dot_index]


def _ensure_repo_root_on_sys_path():
    this_dir = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(this_dir, ".."))
    if repo_root in sys.path:
        return
    sys.path.insert(0, repo_root)
