# Module 6 · AI API Design Review

> **CIT 411 — Applied Generative AI**
> Module 6: AI for API Design Review — Fresh Eyes on Your Package

---

## Overview

This document records the complete AI API design review conducted for `cit411_utils` as part of Module 6. The review used Claude (Anthropic) as the AI reviewer, providing the full public surface of the package — function signatures and docstrings only, no implementation bodies.

**Review question:** Can an AI model, given only the public API surface, act as a useful "fresh eyes" reviewer for Python package design?

---

## 1. Public API Surface Submitted for Review

The following was submitted to the AI — signatures and docstrings from `__init__.py`, with no implementation bodies.

```
cit411_utils public surface:

from .text   import clean_text, truncate_text, slugify
from .data   import flatten_dict, chunk_list, dedupe_list       # pre-review
from .files  import read_json, write_json, ensure_dir
from .net    import fetch_url, parse_headers                    # pre-review
```

**Review prompt:**

> I'm going to paste the public API of a Python utility package called `cit411_utils`.
> Please review it purely as an API design reviewer — a "fresh set of eyes."
> Evaluate only the public surface, not any implementation.
>
> Answer:
> 1. Are the names clear and consistent with Python conventions?
> 2. Is parameter ordering consistent across related functions?
> 3. Are there functions a typical user would expect but are missing?
> 4. Are there functions that probably should be private?
> 5. Any other surface-level issues?

---

## 2. AI Review — Full Response

### 1. Name Clarity & Python Conventions

Overall the names are clear. A few observations:

- **`clean_text` vs `truncate_text`** — these operate at different abstraction levels. `clean_text` normalises; `truncate_text` shortens. Consider whether a unified `text_normalize()` wrapper with a `max_len=` parameter would reduce surface area. Alternatively, leave as-is — both names are unambiguous in isolation.
- **`slugify`** — clear. PEP 8 compliant. No issue.
- **`flatten_dict`** — clear. Consistent with pandas `json_normalize`. No issue.
- **`dedupe_list`** — borderline. "dedupe" is colloquial shorthand. Consider `unique_list()` or `deduplicate_list()`. The `key=` parameter mirroring `sorted()` is a good convention choice.
- **`ensure_dir`** — excellent name. Communicates idempotency clearly.
- **`fetch_url` vs `parse_headers`** — the "fetch" and "parse" verbs are consistent with their domains. No issue.

### 2. Parameter Order Consistency

- `write_json(data, path, ...)` — data first, path second.
- `read_json(path)` — path only.

The family is asymmetric: `write_json` puts "what" before "where." That said, `(data, destination)` is the Python stdlib convention (`json.dump`, `pickle.dump`, `shutil.copy`), so this is defensible — flag it for team alignment.

- `chunk_list(items, size)` vs `dedupe_list(items, *, key=None)` — `items` as first positional is consistent. Good.
- `fetch_url(url, *, timeout, retries, headers)` — keyword-only after `url` is the right call. Good.

### 3. Missing Functions a Typical User Would Expect

- **a)** `word_count(text)` — extremely common in text utility packages.
- **b)** `validate_email(email)` — natural addition alongside `clean_text` and `slugify`.
- **c)** `safe_get(d, *keys, default=None)` — deep nested dict access pairs naturally with `flatten_dict`.
- **d)** `file_exists(path)` — minor, but often expected alongside `read_json`/`write_json`.
- **e)** `post_url(url, data, ...)` — symmetric counterpart to `fetch_url`.

### 4. Functions That Should Be Private

- **`parse_headers`** — strongest candidate for privatisation. Operates on raw HTTP header strings, which is an internal detail. A typical user will not have raw header strings — they'll use `fetch_url` and consume the body. If it exists only to support `fetch_url` internally, make it `_parse_headers`.
- **`ensure_dir`** — could be private if it only supports `write_json`, but has general utility. Reasonable to keep public.

### 5. Other Surface-Level Observations

- `read_json` return type `dict | list` makes callers do `isinstance()` checks. If actual use cases always produce dicts, narrow the annotation.
- `write_json` returning `None` — consider returning the resolved `Path` (like `ensure_dir`) for chaining.
- 10 public functions across 4 modules is a healthy size. Resist unbounded growth.

---

## 3. Classification Table

| ID   | Suggestion                                              | Verdict           | Rationale Summary                                          |
|------|---------------------------------------------------------|-------------------|------------------------------------------------------------|
| S-01 | Rename `dedupe_list` → `unique_list()`                  | ✅ ACCEPT         | Cleaner Python idiom; aligns with numpy/pandas.            |
| S-02 | Rename `clean_text` → `text_normalize()` or merge       | ❌ REJECT         | Orthogonal operations; merging violates SRP.               |
| S-03 | Make `parse_headers` private (`_parse_headers`)         | ✅ ACCEPT         | Internal HTTP detail; no standalone use case.              |
| S-04 | Add `validate_email()`                                  | ❌ REJECT         | Scope creep into RFC-compliance territory.                 |
| S-05 | Add `post_url()` counterpart                            | ⏸ DEPENDS        | Reasonable if scope grows; no current use case.            |
| S-06 | Add `safe_get(d, *keys, default=None)`                  | ✅ ACCEPT         | Genuinely pairs with `flatten_dict`. Real use cases exist. |
| S-07 | Reverse `write_json(data, path)` parameter order        | ❌ REJECT         | Follows `json.dump(obj, fp)` stdlib precedent.             |
| S-08 | Narrow `read_json` return type from `dict\|list` to `dict` | ⏸ DEPENDS    | Revisit when more consumers exist.                         |
| S-09 | `write_json()` return resolved `Path` instead of `None` | ✅ ACCEPT        | Mirrors `ensure_dir()` design. Low cost, better composability. |
| S-10 | Add `file_exists()` helper                              | ❌ REJECT         | `pathlib.Path.exists()` already in stdlib. Pure noise.     |
| S-11 | Add `word_count()` to text module                       | ⏸ DEPENDS        | Trivial to implement but marginal value. Deferred.         |

---

## 4. Defended Rejections

### Rejection 1 — S-02: Do Not Rename `clean_text()` or Merge with `truncate_text()`

**AI suggestion:** *"Consider a unified `text_normalize()` wrapper with a `max_len=` parameter."*

**Defense:**

This suggestion conflates two separate design responsibilities. `clean_text` performs normalization — collapsing whitespace, stripping HTML — and has no opinion about length. `truncate_text` performs a structural cut at a character boundary. These are orthogonal operations:

- `clean_text` never raises on valid input.
- `truncate_text` raises `ValueError` when `max_len` is too short for the suffix.

A unified `text_normalize(text, max_len=None)` would violate the Single Responsibility Principle. Callers who only want whitespace normalization should not have to reason about a `max_len=` parameter that defaults to `None` and silently has no effect. Furthermore, `text_normalize()` is overloaded terminology — in data pipelines it also means statistical normalization, Unicode normalization, and database normalization. `clean_text()` is unambiguous.

**Decision: REJECT.**

---

### Rejection 2 — S-04: Do Not Add `validate_email()`

**AI suggestion:** *"If the package exposes `clean_text` and `slugify`, an email validator is the next natural addition."*

**Defense:**

This is a textbook example of the AI reasoning from category ("text utility library") rather than from this package's actual purpose. A correct `validate_email()` must handle RFC 5321 local-part rules, internationalized domain names, and optionally MX record lookup for live validation. A naive regex-based version would give callers false confidence.

The standard library already provides the `email` module. Third-party solutions like `email-validator` solve this properly. Adding a weak version to `cit411_utils` would be API surface that embarrasses the package.

**Decision: REJECT.**

---

### Rejection 3 — S-07: Do Not Reverse `write_json(data, path)` Parameter Order

**AI suggestion:** *"The family is asymmetric: `write_json` puts data before path."*

**Defense:**

The `(data, path)` ordering deliberately mirrors the Python stdlib convention for serialization operations:

```python
json.dump(obj, fp)       # object → destination
pickle.dump(obj, file)   # object → destination
shutil.copy(src, dst)    # content → destination
```

Reversing to `(path, data)` would break the principle of least surprise for any developer who has used the standard library. The "asymmetry" between `read_json(path)` and `write_json(data, path)` is not an inconsistency — these are operations with fundamentally different argument profiles.

**Decision: REJECT.**

---

## 5. Adopted Improvements

### Improvement 1 — S-01: `dedupe_list` → `unique_list()`

`unique_list()` describes the result state and has direct precedent in `numpy.unique()` and `pandas.Series.unique()`. A developer searching for deduplication already knows "unique" from the ecosystem. "dedupe" reads as jargon.

**Change:** Renamed in `data.py` and re-exported from `__init__.py`.

---

### Improvement 2 — S-06: Add `safe_get(d, *keys, default=None)`

This fills a real gap: callers who use `flatten_dict()` on incoming data also need to safely traverse un-flattened dicts from external APIs. The stdlib offers no clean solution — nested `.get()` chains are verbose. This function is not trivially composable from builtins (unlike `file_exists()`).

**Change:** Added to `data.py`, exported from `__init__.py`.

---

### Improvement 3 — S-09: `write_json()` Returns `pathlib.Path`

Makes `write_json()` consistent with `ensure_dir()`. Both create/write to filesystem paths — returning the resolved `Path` enables clean chaining with zero breaking change for callers who ignore the return value.

**Change:** Return type updated from `None` to `pathlib.Path`.

---

## 6. Reflection: AI vs. Colleague Review

### What AI Does Well

The most useful AI suggestion was `parse_headers` privatisation (S-03) — exactly the kind of thing fresh eyes catch: "why is this public?" It requires no domain knowledge, just a cold read of the surface.

`dedupe_list → unique_list` (S-01) is another win: the original author cannot see the jargon because they've been using the name for weeks. The AI, encountering it cold, flags it immediately.

### Where AI Falls Short

The AI's failure mode is pattern-matching from category to expectation. S-04, S-10, and S-11 all share the same structure: *"other utils libraries have X, so you should too."* This ignores intentional scope.

The parameter order suggestion (S-07) is a subtler failure: the AI noticed surface asymmetry and flagged it as inconsistency without recognising that `(data, destination)` is the dominant Python stdlib convention.

### When to Use Each

| Situation | Best tool |
|-----------|-----------|
| Before sharing an API for the first time | AI review — catches obvious encapsulation mistakes, naming jargon |
| Deciding on parameter order conventions | Colleague — needs stdlib familiarity and project context |
| Scope decisions ("should this be in this package?") | Colleague — needs to know actual downstream callers |
| Spotting unexported-but-should-be-private functions | AI — pure surface scan, no context needed |
| Naming improvements on green-field code | AI — no author bias, cold read |

**Best workflow:** AI review first (generate the full candidate list), then colleague review to filter with context. In this assignment, the AI produced 11 suggestions for a 10-function package — 4 genuinely actionable, 4 reject-with-defense, 3 deferred. That's a useful ratio, but only when the developer applies deliberate defense rather than adopting wholesale.

### The "AI as Authority" Failure Mode

An uncritical developer who adopted all 11 suggestions would have merged `clean_text` and `truncate_text` into a worse function, added a weak email validator that gives false confidence, and reversed `write_json`'s parameter order to conflict with `json.dump`. The discipline of writing a documented defense is what makes AI review useful. Without it, you get churn, not improvement.
