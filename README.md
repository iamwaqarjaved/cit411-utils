# cit411_utils

> A lightweight Python utility library for text processing, data manipulation, file I/O, and HTTP helpers — built and reviewed as part of CIT 411 · Applied Generative AI, Module 6.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-green)](tests/)

---

## What This Repo Is

This package was built for **Module 6 of CIT 411 (Applied Generative AI)** at Atlantis University. The module's focus: using AI as a *"fresh eyes"* reviewer for Python package API design — specifically, whether an AI model can make useful suggestions about public function names, parameter ordering, encapsulation, and missing functions when given only the API surface (no implementation bodies).

**The result:** A 10-function utility library with a documented AI review, classification of every suggestion, defended rejections, and adopted improvements.

📄 Full AI review doc → [`docs/api_review.md`](docs/api_review.md)

---

## Installation

```bash
# Clone and install in development mode
git clone https://github.com/iamwaqarjaved/cit411-utils.git
cd cit411_utils
pip install -e ".[dev]"
```

No external dependencies — only the Python standard library.

---

## Quick Start

```python
from cit411_utils import (
    clean_text, truncate_text, slugify,
    flatten_dict, chunk_list, unique_list, safe_get,
    read_json, write_json, ensure_dir,
    fetch_url,
)
```

---

## API Reference

### 📝 Text — `cit411_utils.text`

#### `clean_text(text, *, strip_html=False, collapse_whitespace=True) → str`

Normalize a raw string: strip leading/trailing whitespace, collapse internal whitespace runs, and optionally remove HTML tags.

```python
from cit411_utils import clean_text

clean_text("  hello   world  ")
# → 'hello world'

clean_text("<p>Hello</p>", strip_html=True)
# → 'Hello'

clean_text("line1\nline2", collapse_whitespace=False)
# → 'line1\nline2'
```

---

#### `truncate_text(text, max_len, suffix="...") → str`

Shorten a string to `max_len` characters, breaking at word boundaries and appending `suffix`.

```python
from cit411_utils import truncate_text

truncate_text("Hello world, this is a long string", 14)
# → 'Hello world...'

truncate_text("Short", 20)
# → 'Short'  (unchanged)
```

> **Raises** `ValueError` if `max_len < len(suffix)`.

---

#### `slugify(text, separator="-", lowercase=True) → str`

Convert text to a URL-safe slug: normalise Unicode to ASCII, strip non-alphanumeric characters, replace spaces with `separator`.

```python
from cit411_utils import slugify

slugify("Hello World!")
# → 'hello-world'

slugify("Héllo Wörld")
# → 'hello-world'

slugify("My Article Title", separator="_", lowercase=False)
# → 'My_Article_Title'
```

---

### 🗂 Data — `cit411_utils.data`

#### `flatten_dict(d, *, sep=".") → dict`

Recursively flatten a nested dictionary, joining key paths with `sep`.

```python
from cit411_utils import flatten_dict

flatten_dict({"user": {"name": "Waqar", "address": {"city": "Miami"}}})
# → {'user.name': 'Waqar', 'user.address.city': 'Miami'}

flatten_dict({"a": {"b": 1}}, sep="/")
# → {'a/b': 1}
```

---

#### `chunk_list(items, size) → list[list]`

Split a list into successive sub-lists of length `size`. The final chunk may be shorter.

```python
from cit411_utils import chunk_list

chunk_list([1, 2, 3, 4, 5], 2)
# → [[1, 2], [3, 4], [5]]

chunk_list(range(6), 3)
# → [[0, 1, 2], [3, 4, 5]]
```

> **Raises** `ValueError` if `size < 1`.

---

#### `unique_list(items, *, key=None) → list`

Remove duplicates from a list while preserving insertion order.

```python
from cit411_utils import unique_list

unique_list([3, 1, 2, 1, 3])
# → [3, 1, 2]

# Use a key function (like sorted())
unique_list(["Apple", "banana", "apple"], key=str.lower)
# → ['Apple', 'banana']
```

> **v1.1.0:** Renamed from `dedupe_list` to align with `numpy.unique` / `pandas.Series.unique` naming conventions.

---

#### `safe_get(d, *keys, default=None) → any`

Safely traverse a nested dictionary. Returns `default` instead of raising `KeyError` when any key is missing.

```python
from cit411_utils import safe_get

profile = {
    "user": {
        "address": {"city": "Miami"}
    }
}

safe_get(profile, "user", "address", "city")
# → 'Miami'

safe_get(profile, "user", "phone")
# → None

safe_get(profile, "user", "phone", default="N/A")
# → 'N/A'
```

> **v1.1.0:** New function. Pairs naturally with `flatten_dict()` for nested API response processing.

---

### 📁 Files — `cit411_utils.files`

#### `read_json(path) → dict | list`

Read and parse a JSON file with clear error messages.

```python
from cit411_utils import read_json

config = read_json("config.json")
print(config["version"])
```

> **Raises** `FileNotFoundError` if the path doesn't exist; `json.JSONDecodeError` if not valid JSON.

---

#### `write_json(data, path, *, indent=2, ensure_ascii=False) → pathlib.Path`

Serialise a Python object to a JSON file. Returns the resolved `Path` of the written file.

```python
from cit411_utils import write_json, ensure_dir

# Ensure the directory exists, then write
ensure_dir("output/data")
path = write_json({"status": "ok"}, "output/data/result.json")
print(path)
# → PosixPath('/absolute/path/to/output/data/result.json')
```

> **v1.1.0:** Return type updated from `None` to `pathlib.Path` for composability.
> **Note:** Parent directories must exist — use `ensure_dir()` first.

---

#### `ensure_dir(path) → pathlib.Path`

Create a directory (and all missing parents) if it doesn't already exist. Safe to call repeatedly — equivalent to `mkdir -p`.

```python
from cit411_utils import ensure_dir

ensure_dir("output/reports/2026")
# → PosixPath('/absolute/path/to/output/reports/2026')
```

---

### 🌐 Net — `cit411_utils.net`

#### `fetch_url(url, *, timeout=10, retries=2, headers=None) → str`

Fetch the text body of a URL via HTTP GET, with automatic retry on transient failures.

```python
from cit411_utils import fetch_url

body = fetch_url("https://httpbin.org/get")
print(body[:80])

# With custom headers and timeout
body = fetch_url(
    "https://api.example.com/data",
    timeout=5,
    retries=3,
    headers={"User-Agent": "cit411/1.1"},
)
```

> **Raises** `urllib.error.URLError` after all retries are exhausted.

---

## Running the Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=cit411_utils --cov-report=term-missing
```

Expected output:

```
tests/test_cit411_utils.py::TestCleanText::test_strips_whitespace PASSED
tests/test_cit411_utils.py::TestCleanText::test_collapses_internal_spaces PASSED
...
25 passed in 0.XX s
```

---

## Module 6 — AI API Design Review Summary

This package is the subject of a structured AI review exercise. The full document is at [`docs/api_review.md`](docs/api_review.md). Summary:

| What the AI got right | What the AI got wrong |
|---|---|
| `parse_headers` should be private (S-03) | Suggested merging `clean_text` + `truncate_text` (S-02) |
| `dedupe_list` is jargon → `unique_list` (S-01) | Recommended adding `validate_email()` — out of scope (S-04) |
| `safe_get()` is a genuine gap (S-06) | Suggested reversing `write_json(data, path)` parameter order (S-07) |
| `write_json` should return `Path` (S-09) | Suggested `file_exists()` — `pathlib.Path.exists()` already exists (S-10) |

**Key finding:** AI review is most useful on the first pass — it generates a complete candidate list quickly and catches jargon/encapsulation issues a fatigued author misses. But it consistently over-suggests by reasoning from category ("text utils should have X") rather than from actual caller needs. Every suggestion needs a deliberate accept/reject decision.

---

## Changelog

### v1.1.0 (Module 6 revision)
- ✅ **Renamed** `dedupe_list()` → `unique_list()` — ecosystem alignment
- ✅ **Added** `safe_get(d, *keys, default=None)` — safe nested dict traversal
- ✅ **Updated** `write_json()` return type `None` → `pathlib.Path`
- ✅ **Made private** `parse_headers()` → `_parse_headers()` — internal HTTP detail

### v1.0.0 (initial)
- Initial release: `clean_text`, `truncate_text`, `slugify`, `flatten_dict`, `chunk_list`, `dedupe_list`, `read_json`, `write_json`, `ensure_dir`, `fetch_url`, `parse_headers`

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

**Waqar Javed** · [@iamwaqarjaved](https://github.com/iamwaqarjaved)
