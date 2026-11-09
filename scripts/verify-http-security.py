#!/usr/bin/env python3
"""Проверяет заголовки и CSRF без создания или изменения записей."""
import datetime
import http.cookiejar
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class TokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "input" and values.get("name") == "_csrf":
            self.token = values.get("value")


def client():
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )


def request(opener, url, fields=None):
    data = None if fields is None else urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=data)
    try:
        response = opener.open(req, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.code, dict(response.headers), response.read().decode()


def token(body):
    parser = TokenParser()
    parser.feed(body)
    if not parser.token:
        raise RuntimeError("В форме отсутствует CSRF-токен")
    return parser.token


base = sys.argv[1].rstrip("/")
first = client()
form_url = base + "/owners/new"
code, headers, body = request(first, form_url)
csrf = token(body)
headers = {key.lower(): value for key, value in headers.items()}
checks = [{"check": "form_available", "status": code, "passed": code == 200}]
for name, expected in [("x-frame-options", "DENY"), ("x-content-type-options", "nosniff")]:
    checks.append({"check": name, "value": headers.get(name), "passed": headers.get(name) == expected})
cookie = headers.get("set-cookie", "")
checks.append({"check": "session_cookie_samesite", "passed": "samesite=lax" in cookie.lower()})
csp = headers.get("content-security-policy", "")
checks.append({"check": "content-security-policy", "value": csp,
               "passed": all(d in csp for d in ["default-src 'self'", "frame-ancestors 'none'", "form-action 'self'", "object-src 'none'"])})
other = client()
_, _, other_body = request(other, form_url)
for label, fields, expected in [
    ("missing_token_rejected", {}, 403),
    ("invalid_token_rejected", {"_csrf": "invalid"}, 403),
    ("other_session_token_rejected", {"_csrf": token(other_body)}, 403),
    ("valid_token_reaches_form_validation", {"_csrf": csrf}, 200),
]:
    code, _, result = request(first, form_url, fields)
    passed = code == expected
    if expected == 200:
        passed = passed and 'name="firstName"' in result and 'name="_csrf"' in result
    checks.append({"check": label, "status": code, "passed": passed})
print(json.dumps({"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "target": base, "checks": checks, "passed": all(c["passed"] for c in checks)},
                 ensure_ascii=False, indent=2))
sys.exit(0 if all(c["passed"] for c in checks) else 1)
