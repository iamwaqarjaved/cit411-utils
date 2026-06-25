"""
tests/test_cit411_utils.py
--------------------------
Unit tests for cit411_utils public API.
Run with: pytest tests/ -v
"""

import pytest
from cit411_utils import (
    clean_text, truncate_text, slugify,
    flatten_dict, chunk_list, unique_list, safe_get,
    read_json, write_json, ensure_dir,
)


# ── text ──────────────────────────────────────────────────────────────────

class TestCleanText:
    def test_strips_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_collapses_internal_spaces(self):
        assert clean_text("hello   world") == "hello world"

    def test_collapses_tabs_and_newlines(self):
        assert clean_text("a\t\nb") == "a b"

    def test_strip_html(self):
        assert clean_text("<p>Hello</p>", strip_html=True) == "Hello"

    def test_no_collapse(self):
        result = clean_text("a\nb", collapse_whitespace=False)
        assert result == "a\nb"

    def test_type_error(self):
        with pytest.raises(TypeError):
            clean_text(123)


class TestTruncateText:
    def test_short_text_unchanged(self):
        assert truncate_text("Hi", 10) == "Hi"

    def test_truncates_at_word_boundary(self):
        result = truncate_text("Hello world foo", 11)
        assert result == "Hello..."
        assert len(result) <= 11

    def test_custom_suffix(self):
        result = truncate_text("Hello world", 8, suffix="…")
        assert result.endswith("…")

    def test_raises_if_max_len_too_small(self):
        with pytest.raises(ValueError):
            truncate_text("Hello", 2, suffix="...")


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello World!") == "hello-world"

    def test_unicode_normalised(self):
        assert slugify("Héllo Wörld") == "hello-world"

    def test_custom_separator(self):
        assert slugify("Hello World", separator="_") == "hello_world"

    def test_preserve_case(self):
        assert slugify("Hello World", lowercase=False) == "Hello-World"

    def test_empty_string(self):
        assert slugify("") == ""


# ── data ──────────────────────────────────────────────────────────────────

class TestFlattenDict:
    def test_nested(self):
        assert flatten_dict({"a": {"b": 1}}) == {"a.b": 1}

    def test_deep(self):
        assert flatten_dict({"x": {"y": {"z": 42}}}) == {"x.y.z": 42}

    def test_custom_sep(self):
        assert flatten_dict({"a": {"b": 1}}, sep="/") == {"a/b": 1}

    def test_flat_passthrough(self):
        assert flatten_dict({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    def test_empty(self):
        assert flatten_dict({}) == {}


class TestChunkList:
    def test_even_split(self):
        assert chunk_list([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

    def test_uneven_split(self):
        assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

    def test_empty(self):
        assert chunk_list([], 3) == []

    def test_size_larger_than_list(self):
        assert chunk_list([1, 2], 10) == [[1, 2]]

    def test_invalid_size(self):
        with pytest.raises(ValueError):
            chunk_list([1, 2, 3], 0)


class TestUniqueList:
    def test_removes_duplicates(self):
        assert unique_list([3, 1, 2, 1, 3]) == [3, 1, 2]

    def test_preserves_order(self):
        assert unique_list([4, 2, 4, 1]) == [4, 2, 1]

    def test_key_function(self):
        assert unique_list(["A", "b", "a"], key=str.lower) == ["A", "b"]

    def test_empty(self):
        assert unique_list([]) == []

    def test_no_duplicates(self):
        assert unique_list([1, 2, 3]) == [1, 2, 3]


class TestSafeGet:
    def setup_method(self):
        self.d = {"user": {"address": {"city": "Miami"}}}

    def test_deep_access(self):
        assert safe_get(self.d, "user", "address", "city") == "Miami"

    def test_missing_key_returns_default(self):
        assert safe_get(self.d, "user", "phone") is None

    def test_custom_default(self):
        assert safe_get(self.d, "user", "phone", default="N/A") == "N/A"

    def test_non_dict_intermediate(self):
        d = {"a": "string"}
        assert safe_get(d, "a", "b", default="x") == "x"

    def test_empty_keys(self):
        assert safe_get(self.d) == self.d


# ── files ─────────────────────────────────────────────────────────────────

class TestEnsureDir:
    def test_creates_directory(self, tmp_path):
        target = tmp_path / "new" / "nested"
        result = ensure_dir(target)
        assert result.exists()
        assert result.is_dir()

    def test_idempotent(self, tmp_path):
        target = tmp_path / "existing"
        ensure_dir(target)
        ensure_dir(target)  # should not raise
        assert target.exists()


class TestReadWriteJson:
    def test_round_trip(self, tmp_path):
        data = {"name": "cit411", "version": "1.1.0"}
        path = tmp_path / "test.json"
        write_json(data, path)
        result = read_json(path)
        assert result == data

    def test_write_returns_path(self, tmp_path):
        path = tmp_path / "out.json"
        result = write_json({"x": 1}, path)
        assert result == path.resolve()

    def test_read_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            read_json(tmp_path / "nonexistent.json")

    def test_read_invalid_json(self, tmp_path):
        import json
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        with pytest.raises(json.JSONDecodeError):
            read_json(bad)

    def test_indent_and_encoding(self, tmp_path):
        data = {"emoji": "🎉"}
        path = tmp_path / "enc.json"
        write_json(data, path, indent=4, ensure_ascii=False)
        content = path.read_text(encoding="utf-8")
        assert "🎉" in content
        assert "    " in content  # 4-space indent
