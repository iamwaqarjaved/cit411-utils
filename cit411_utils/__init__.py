"""
cit411_utils
============
A lightweight Python utility library for text processing, data manipulation,
file I/O, and HTTP utilities.

CIT 411 · Applied Generative AI · Module 6 — API Design Review Project
Author: Waqar Javed

Public API
----------
Text:  clean_text, truncate_text, slugify
Data:  flatten_dict, chunk_list, unique_list, safe_get
Files: read_json, write_json, ensure_dir
Net:   fetch_url
"""

from .text  import clean_text, truncate_text, slugify
from .data  import flatten_dict, chunk_list, unique_list, safe_get
from .files import read_json, write_json, ensure_dir
from .net   import fetch_url

__version__ = "1.1.0"
__all__ = [
    # text
    "clean_text",
    "truncate_text",
    "slugify",
    # data
    "flatten_dict",
    "chunk_list",
    "unique_list",
    "safe_get",
    # files
    "read_json",
    "write_json",
    "ensure_dir",
    # net
    "fetch_url",
]
