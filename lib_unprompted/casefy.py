"""Utilities for string case conversion."""

__version__ = "0.1.2"

import re
from typing import List


def camelcase(string: str) -> str:
    """Convert a string into camelCase.

    Args:
        string (:obj:`str`): 
            The string to convert to camelCase.

    Returns:
        :obj:`str`: The camelCased string.
    """
    if not string:
        return ""
    # Turn into snake_case, then remove "_" and capitalize first letter
    string = "".join(f"{s[0].upper()}{s[1:].lower()}"
                     for s in re.split(r'_', snakecase(string)) if s)
    # Make first letter lower
    return f"{string[0].lower()}{string[1:]}" if string else ""


def pascalcase(string: str) -> str:
    """Convert a string into PascalCase.

    Args:
        string (:obj:`str`):
            The string to convert to CamelCase.

    Returns:
        :obj:`str`: The CamelCased string.
    """
    if not string:
        return ""
    return capitalcase(camelcase(string))


def snakecase(string: str, keep_together: List[str] = None) -> str:
    """Convert a string into snake_case.

    Args:
        string (:obj:`str`):
            The string to convert to snake_case.
        keep_together (:obj:`List[str]`, `optional`):
            (Upper) characters to not split, e.g., "HTTP".

    Returns:
        :obj:`str`: The snake_cased string.
    """
    if not string:
        return ""
    leading_underscore: bool = string[0] == "_"
    trailing_underscore: bool = string[-1] == "_"
    # If all uppercase, turn into lowercase
    if string.isupper():
        string = string.lower()
    if keep_together:
        for keep in keep_together:
            string = string.replace(keep, f"_{keep.lower()}_")
    # Manage separators
    string = re.sub(r"[\W]", "_", string)
    # Manage capital letters and numbers
    string = re.sub(r"([A-Z]|\d+)", r"_\1", string)
    # Add "_" after numbers
    string = re.sub(r"(\d+)", r"\1_", string).lower()
    # Remove repeated "_"
    string = re.sub(r"[_]{2,}", "_", string)
    string = re.sub(r"^_", "", string) if not leading_underscore else string
    return re.sub(r"_$", "", string) if not trailing_underscore else string


def constcase(string: str) -> str:
    """Convert a string into CONST_CASE.

    Args:
        string (:obj:`str`):
            The string to convert.

    Returns:
        :obj:`str`: The CONST_CASED string.
    """
    if not string:
        return ""
    return uppercase(snakecase(string))


def kebabcase(string: str) -> str:
    """Convert a string into kebab-case.

    Args:
        string (:obj:`str`):
            The string to convert to kebab-case.

    Returns:
        :obj:`str`: The kebab-cased string.
    """
    if not string:
        return ""
    string = snakecase(string).replace("_", "-")
    return string.strip("-")


def upperkebabcase(string: str) -> str:
    """Convert a string into UPPER-KEBAB-CASE.

    Args:
        string (:obj:`str`):
            The string to convert.

    Returns:
        :obj:`str`: The UPPER-KEBAB-CASED string.
    """
    if not string:
        return ""
    return uppercase(kebabcase(string))


def separatorcase(
    string: str,
    separator: str,
    keep_together: List[str] = None
) -> str:
    """Convert a string into a case with an arbitrary separator.

    Args:
        string (:obj:`str`):
            The string to convert.
        separator (:obj:`str`):
            The separator to use.

    Returns:
        :obj:`str`: The separator cased string.
    """
    if not string:
        return ""
    string_conv = snakecase(string, keep_together).replace('_', separator)
    before = ("" if (string[0].isalnum()
                     or string[:len(separator)] == separator
                     or string_conv[:len(separator):] == separator)
                 else separator)
    after = ("" if (string[-1].isalnum()
                    or string[:-len(separator)] == separator
                    or string_conv[:-len(separator)] == separator)
                else separator)
    return f"{before}{string_conv}{after}"


def sentencecase(string: str) -> str:
    """Convert a string into Sentence case.

    For example: ``"fooBar"`` → ``"Foo bar"``.

    Args:
        string (:obj:`str`):
            The string to convert to a sentence.

    Returns:
        :obj:`str`: The converted string.
    """
    if not string:
        return ""
    # Add space between separators and numbers
    string = " ".join(s for s in re.split(r"([\W_\d])", string) if s)
    # Remove separators (except numbers)
    string = " ".join(re.sub(r"[\W_]", " ", string).split())
    # Manage capital letters
    return re.sub(r"([A-Z])", r" \1", string).capitalize()


def titlecase(string: str) -> str:
    """Convert a string into Title Sentence Case.

    Args:
        string (:obj:`str`):
            The string to convert.

    Returns:
        :obj:`str`: The Title Sentence Cased string.
    """
    if not string:
        return ""
    return " ".join(w.capitalize() for w in sentencecase(string).split())


def alphanumcase(string: str) -> str:
    """Removes all non-alphanumeric symbols (including spaces).

    For example: ``"foo 123 _Bar!"`` → ``"foo134Bar"``.

    Args:
        string (:obj:`str`):
            The string to convert.

    Returns:
        :obj:`str`: The string containing only alphanumeric symbols.
    """
    if not string:
        return ""
    return re.sub(r"[\W_]", "", string)


def lowercase(string: str) -> str:
    """Lowercase a string.

    Args:
        string (:obj:`str`):
            The string to convert.

    Returns:
        :obj:`str`: The lowercased string.
    """
    if not string:
        return ""
    return string.lower()


def uppercase(string: str) -> str:
    """Convert string into UPPER CASE.

    Args:
        string (:obj:`str`):
            The string to convert.

    Returns:
        :obj:`str`: The UPPER CASED string.
    """
    if not string:
        return ""
    return string.upper()


def capitalcase(string: str) -> str:
    """Capitalize the first letter of a string.

    The casing of all the other letters will remain unaltered, e.g.,
    ``"fooBar"`` → ``"FooBar"``.

    Args:
        string (:obj:`str`):
            The string to capitalize.

    Returns:
        :obj:`str`: The capitalized string.
    """
    if not string:
        return ""
    return f"{string[0].upper()}{string[1:]}" if string else ""
