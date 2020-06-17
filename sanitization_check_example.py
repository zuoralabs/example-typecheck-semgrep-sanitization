# Sketch of a simple method for using type checker and semgrep for ensuring sanitization
from __future__ import annotations

from os import environ
from typing import Callable, Any, Union

from mypy_extensions import VarArg

from my_sanitization_lib import HtmlSanitizedStr, sorry_fake_sanitize, sanitize_for_html, SanitizedStr, LiteralStr, safe_route

# adapted from https://pythonspot.com/flask-web-app-with-python/

from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Index!"


@safe_route(app, "/hello")
def hello():
    return "Hello World!"


@safe_route(app, "/members")
def members():
    return "Members"


@safe_route(app, "/membersBad1/<string:name>/")
def getMemberBad1(name) -> HtmlSanitizedStr:
    """
    No sanitization; gets caught by type checker. Note that Flask has built-in sanitization so it is still safe, but just imagine
    that we were using a framework didn't auto-sanitize.

    """
    return f"{name}</string:name>"


@safe_route(app, "/membersBad2/<string:name>/")
def getMemberBad2(name) -> HtmlSanitizedStr:
    """
    Artificially satisfy the type checker while doing insecure things. We can use semgrep to track
    everywhere we are using the fake sanitizer.

    Note that due to DeprecationWarning, IntelliJ IDEA/PyCharm should cross out usages of `sorry_fake_sanitize`.

    """
    return sorry_fake_sanitize(f"{name}</string:name>")


@safe_route(app, "/membersBad3/<string:name>/")
def getMemberBad3(name) -> HtmlSanitizedStr:
    """
    sanitizes, but loses functionality.

    """
    return sanitize_for_html(f"{name}</string:name>")


@safe_route(app, "/membersBad4/<string:name>/")
def getMemberBad4(name) -> HtmlSanitizedStr:
    """
    Violates usage requirement of LiteralStr.
    This should be caught by semgrep.

    """

    fake_literal_str = LiteralStr(str(Flask))

    out = sanitize_for_html(name) + fake_literal_str + LiteralStr('</string:name>')
    return out


@safe_route(app, "/membersBad5/<string:name>/")
def getMemberBad5(name) -> HtmlSanitizedStr:
    """
    partial sanitization, this should be caught by type checker
    """
    out = sanitize_for_html(name) + str(Flask) + LiteralStr('</string:name>')

    # Python lets you run code that doesn't type check. We can raise an error at runtime if we want to prevent this.
    # assert isinstance(out, HtmlSanitizedStr)

    return out


@safe_route(app, "/members/<string:name>/")
def getMemberGood(name) -> HtmlSanitizedStr:
    """
    Sanitizes while maintaining functionality.
    This should get a pass from type checker and semgrep

    """
    out: HtmlSanitizedStr = sanitize_for_html(name) + LiteralStr('</string:name>')
    return out


if __name__ == "__main__":
    # type checker notes
    # in IntelliJ IDEA / PyCharm, use View -> Type Info to resolve and show types

    a_normal_str = 'x' + LiteralStr('y')  # type checker should resolve to normal str
    assert type(a_normal_str) == str, type(a_normal_str)

    a_literal_str = LiteralStr('x') + LiteralStr('y')  # type checker should resolve to LiteralStr
    assert type(a_literal_str) == LiteralStr

    # type checker should resolve to SanitizedStr
    a_sanitized_str = LiteralStr('x') + SanitizedStr('y')
    assert type(a_sanitized_str) == SanitizedStr
    a_sanitized_str_2 = SanitizedStr('x') + LiteralStr('y')
    assert type(a_sanitized_str_2) == SanitizedStr

    # type checker should resolve to HtmlSanitizedStr
    an_html_sanitized_str_a = LiteralStr('x') + sanitize_for_html('y')
    assert type(an_html_sanitized_str_a) == HtmlSanitizedStr
    an_html_sanitized_str_b = sanitize_for_html('x') + LiteralStr('y')
    assert type(an_html_sanitized_str_b) == HtmlSanitizedStr

    # Should emit double sanitization warning.
    # Also does not type check if not `issubclass(HtmlSanitizedStr, str)`. (You can decide in `base_str.py`.)
    sanitize_for_html(sanitize_for_html('a'))

    # Note that semgrep rule should flag this call to `HtmlSanitizedStr`.
    HtmlSanitizedStr('x')

    # You can try running the app if you really want by setting environment var `REALLY_RUN_APP=True`.
    if environ.get('REALLY_RUN_APP', 'False') == 'True':
        app.run()
