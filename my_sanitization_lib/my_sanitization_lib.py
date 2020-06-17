"""
Note: Can't subclass str because of "Liskov substitution principle"
https://stackoverflow.com/questions/54346721/mypy-argument-of-method-incompatible-with-supertype
"""

from __future__ import annotations

import warnings
from html import escape
from typing import Generic, NewType, Union, Type, TypeVar, Sequence, Any, Tuple, Callable, Dict

from flask import Flask
from toolz import compose

from .str_base import SpecialStr, acceptable_others


class SanitizedStr(SpecialStr):
    pass


class HtmlSanitizedStr(SpecialStr):
    pass


class LiteralStr(SpecialStr):
    """
    Use semgrep to check that all usages of LiteralStr are actually with a literal str.
    """
    pass


acceptable_others.update({
    SanitizedStr: (LiteralStr,),
    HtmlSanitizedStr: (LiteralStr,),
})


def sorry_fake_sanitize(x: str) -> HtmlSanitizedStr:
    warnings.warn('fake sanitizer used', DeprecationWarning, stacklevel=2)
    return HtmlSanitizedStr(x)


def sanitize_for_html(x: str) -> HtmlSanitizedStr:
    if isinstance(x, HtmlSanitizedStr):
        warnings.warn('double sanitization', stacklevel=2)
        return x
    else:
        return HtmlSanitizedStr(escape(x))


RouteFunction = Callable[..., HtmlSanitizedStr]


def safe_route(app: Flask, rule, **options) -> Callable[[RouteFunction], None]:
    """Like `Flask.app.route` but takes only a function that returns HtmlSanitizedStr

    :param app:
    :param rule: see `Flask.app.route`
    :param options: see `Flask.app.route`
    :return: see `Flask.app.route`
    """
    original_decorator = app.route(rule, **options)

    def decorator(fn: RouteFunction):
        return original_decorator(compose(str, fn))  # type: ignore

    return decorator
