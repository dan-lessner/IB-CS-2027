import os
import sys
import importlib.util


class ScriptInfo:
    def __init__(self, name: str, path: str, file_name: str):
        self.name = name
        self.path = path
        self.file_name = file_name
        self.auto_class = None


def load_scripts_from_folder(folder_path: str):
    files = _find_script_files(folder_path)
    scripts = []

    index = 0
    while index < len(files):
        path = files[index]
        file_name = os.path.basename(path)
        script_name = _filename_without_extension(file_name)
        scripts.append(ScriptInfo(script_name, path, file_name))
        index += 1

    return scripts


def load_auto_class(script_info: ScriptInfo):
    if script_info is None:
        return None
    if script_info.auto_class is not None:
        return script_info.auto_class

    _ensure_repo_root_on_sys_path()
    module_name = _module_name_from_path(script_info.path)
    try:
        module = _load_module(script_info.path, module_name)
    except Exception:
        return None
    if module is None:
        return None
    if not hasattr(module, "Auto"):
        return None

    auto_class = getattr(module, "Auto")
    script_info.auto_class = auto_class
    return auto_class


def _find_script_files(folder_path: str):
    if not os.path.isdir(folder_path):
        return []

    files = []
    names = os.listdir(folder_path)
    index = 0
    while index < len(names):
        name = names[index]
        if _is_python_file(name) and not name.startswith("_"):
            full_path = os.path.join(folder_path, name)
            files.append(full_path)
        index += 1

    files.sort()
    return files


def _is_python_file(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(".py")


def _load_module(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        return None
    loader = spec.loader
    if loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def _module_name_from_path(path: str) -> str:
    base = os.path.basename(path)
    name = _filename_without_extension(base)
    # Using full normalized path keeps module name stable and unique per file.
    normalized = os.path.abspath(path).lower()
    suffix = ""
    i = 0
    while i < len(normalized):
        ch = normalized[i]
        if ch.isalnum():
            suffix = suffix + ch
        else:
            suffix = suffix + "_"
        i += 1
    return "script_" + name + "_" + suffix


def _filename_without_extension(name: str) -> str:
    dot_index = -1
    index = 0
    while index < len(name):
        if name[index] == ".":
            dot_index = index
        index += 1

    if dot_index <= 0:
        return name

    result = ""
    index = 0
    while index < dot_index:
        result = result + name[index]
        index += 1
    return result


def _ensure_repo_root_on_sys_path():
    this_dir = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(this_dir, ".."))
    index = 0
    while index < len(sys.path):
        if sys.path[index] == repo_root:
            return
        index += 1
    sys.path.insert(0, repo_root)
