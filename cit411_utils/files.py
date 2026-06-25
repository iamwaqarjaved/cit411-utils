"""
cit411_utils.files
------------------
File I/O utilities: JSON read/write and directory helpers.
"""

import json
import os
import pathlib


def read_json(path: "str | os.PathLike") -> "dict | list":
    """
    Read and parse a JSON file, raising clear errors on failure.

    Parameters
    ----------
    path : str | PathLike
        Path to the JSON file.

    Returns
    -------
    dict | list
        Parsed JSON value.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    json.JSONDecodeError
        If the file is not valid JSON.

    Examples
    --------
    >>> data = read_json("config.json")
    >>> data["version"]
    '1.0'
    """
    path = pathlib.Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(
    data: "dict | list",
    path: "str | os.PathLike",
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> pathlib.Path:
    """
    Serialise *data* to a JSON file.

    Parameters
    ----------
    data         : dict | list
        Serialisable Python object.
    path         : str | PathLike
        Destination file path.
    indent       : int, default 2
        JSON indentation level.
    ensure_ascii : bool, default False
        Escape non-ASCII characters.

    Returns
    -------
    pathlib.Path
        The resolved path of the written file.

    Notes
    -----
    Parent directories must already exist. Use ``ensure_dir()`` first.
    Returns the resolved Path (updated in v1.1.0) to enable chaining::

        path = write_json(data, "out/result.json")

    Examples
    --------
    >>> ensure_dir("out")
    PosixPath('out')
    >>> write_json({"key": "value"}, "out/data.json")
    PosixPath('out/data.json')
    """
    path = pathlib.Path(path).resolve()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
    return path


def ensure_dir(path: "str | os.PathLike") -> pathlib.Path:
    """
    Create *path* (and any missing parents) if it does not already exist.

    Equivalent to ``mkdir -p``. Safe to call when the directory already exists.

    Parameters
    ----------
    path : str | PathLike

    Returns
    -------
    pathlib.Path
        The resolved, guaranteed-existing directory path.

    Examples
    --------
    >>> ensure_dir("output/data/processed")
    PosixPath('output/data/processed')
    """
    path = pathlib.Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()
