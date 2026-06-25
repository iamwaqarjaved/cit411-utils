"""
cit411_utils.data
-----------------
Dictionary and list manipulation utilities.
"""


def flatten_dict(d: dict, *, sep: str = ".") -> dict:
    """
    Recursively flatten a nested dictionary.

    Joins key paths with *sep*.

    Parameters
    ----------
    d   : dict
        Possibly nested input dictionary.
    sep : str, default "."
        Separator between key levels.

    Returns
    -------
    dict
        Flat {dotted.key: value} mapping.

    Examples
    --------
    >>> flatten_dict({"a": {"b": 1}})
    {'a.b': 1}
    >>> flatten_dict({"x": {"y": {"z": 42}}}, sep="/")
    {'x/y/z': 42}
    """
    def _flatten(obj, parent_key=""):
        items = {}
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            if isinstance(v, dict):
                items.update(_flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    return _flatten(d)


def chunk_list(items: list, size: int) -> list:
    """
    Split *items* into successive sub-lists of length *size*.

    The final chunk may be shorter than *size* if len(items) is not
    evenly divisible.

    Parameters
    ----------
    items : list
        Input sequence.
    size  : int
        Maximum items per chunk (must be >= 1).

    Returns
    -------
    list[list]
        List of sub-lists.

    Raises
    ------
    ValueError
        If size < 1.

    Examples
    --------
    >>> chunk_list([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    >>> chunk_list([], 3)
    []
    """
    if size < 1:
        raise ValueError(f"size must be >= 1, got {size}")
    return [items[i : i + size] for i in range(0, len(items), size)]


def unique_list(items: list, *, key=None) -> list:
    """
    Return a copy of *items* with duplicates removed, preserving order.

    Parameters
    ----------
    items : list
        Source list (elements must be hashable, or *key* must map them
        to hashable values).
    key   : callable | None, default None
        Optional function applied to each element before comparing.
        Mirrors the *key* parameter on sorted().

    Returns
    -------
    list
        Deduplicated, order-preserved copy.

    Notes
    -----
    Renamed from ``dedupe_list`` in v1.1.0 to align with the numpy/pandas
    ecosystem convention (``numpy.unique``, ``Series.unique``).

    Examples
    --------
    >>> unique_list([3, 1, 2, 1, 3])
    [3, 1, 2]
    >>> unique_list(["A", "b", "a"], key=str.lower)
    ['A', 'b']
    """
    seen = set()
    result = []
    for item in items:
        k = key(item) if key is not None else item
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


def safe_get(d: dict, *keys, default=None):
    """
    Safely traverse a nested dictionary using a sequence of keys.

    Returns *default* at the first key that is missing or where the
    current value is not a dict (instead of raising KeyError).

    Parameters
    ----------
    d       : dict
        The top-level mapping to traverse.
    *keys
        Sequence of keys to traverse in order.
    default : any, default None
        Value returned on any traversal failure.

    Returns
    -------
    any
        The nested value, or *default*.

    Notes
    -----
    Added in v1.1.0. Pairs naturally with ``flatten_dict`` for workflows
    that need both deep access and flattened representations.

    Examples
    --------
    >>> d = {"user": {"address": {"city": "Miami"}}}
    >>> safe_get(d, "user", "address", "city")
    'Miami'
    >>> safe_get(d, "user", "phone", default="N/A")
    'N/A'
    >>> safe_get(d, "missing", "key")  # returns None
    """
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is default:
            return default
    return current
