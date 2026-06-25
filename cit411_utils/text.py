"""
cit411_utils.text
-----------------
String normalisation utilities: cleaning, truncation, and slugification.
"""

import re
import unicodedata


def clean_text(text: str, *, strip_html: bool = False,
               collapse_whitespace: bool = True) -> str:
    """
    Normalize a raw string for downstream use.

    Strips leading/trailing whitespace, optionally removes HTML tags,
    and collapses internal runs of whitespace to a single space.

    Parameters
    ----------
    text : str
        Input string. May contain HTML, tabs, or multi-line content.
    strip_html : bool, default False
        If True, remove all HTML/XML tags before cleaning.
    collapse_whitespace : bool, default True
        Replace runs of whitespace (\\t, \\n, multiple spaces) with a single space.

    Returns
    -------
    str
        Cleaned string.

    Examples
    --------
    >>> clean_text("  hello   world  ")
    'hello world'
    >>> clean_text("<p>Hello</p>", strip_html=True)
    'Hello'
    >>> clean_text("line1\\nline2", collapse_whitespace=False)
    'line1\\nline2'
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")

    if strip_html:
        text = re.sub(r"<[^>]+>", "", text)

    if collapse_whitespace:
        text = re.sub(r"\s+", " ", text)

    return text.strip()


def truncate_text(text: str, max_len: int, suffix: str = "...") -> str:
    """
    Shorten *text* to at most *max_len* characters, appending *suffix* if cut.

    Truncation breaks at the last whitespace boundary before *max_len* so
    words are not split, unless the text contains no whitespace at all.

    Parameters
    ----------
    text    : str
        Source string.
    max_len : int
        Maximum character count in the returned string (including suffix length).
    suffix  : str, default "..."
        Appended when the string is shortened.

    Returns
    -------
    str
        Truncated (or original) string.

    Raises
    ------
    ValueError
        If max_len < len(suffix).

    Examples
    --------
    >>> truncate_text("Hello world, this is long", 12)
    'Hello world...'
    >>> truncate_text("Short", 20)
    'Short'
    """
    if max_len < len(suffix):
        raise ValueError(
            f"max_len ({max_len}) must be >= len(suffix) ({len(suffix)})"
        )
    if len(text) <= max_len:
        return text

    cut = max_len - len(suffix)
    truncated = text[:cut]
    # break at last whitespace boundary
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + suffix


def slugify(text: str, separator: str = "-", lowercase: bool = True) -> str:
    """
    Convert *text* to a URL-safe slug.

    Normalises Unicode to ASCII, strips non-alphanumeric characters,
    and replaces spaces (and other separators) with *separator*.

    Parameters
    ----------
    text      : str
        Input string.
    separator : str, default "-"
        Character placed between words.
    lowercase : bool, default True
        Convert result to lowercase.

    Returns
    -------
    str
        URL-safe slug.

    Examples
    --------
    >>> slugify("Hello World!")
    'hello-world'
    >>> slugify("Héllo Wörld")
    'hello-world'
    >>> slugify("My Title", separator="_", lowercase=False)
    'My_Title'
    """
    # Normalise unicode → ASCII
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    if lowercase:
        text = text.lower()

    # Replace non-alphanumeric (except spaces) with nothing
    text = re.sub(r"[^\w\s-]", "", text)
    # Replace whitespace / hyphens with separator
    text = re.sub(r"[\s_-]+", separator, text)

    return text.strip(separator)
