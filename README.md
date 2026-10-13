# Olywork runtime foundation

This is the independent runtime foundation for Option A. The relay is deliberately small: it
forwards an already formed upstream request and returns the upstream status, headers, and body.
It does not know about catalogs, billing, teams, OAuth, or provider-specific payloads.

The package is not wired into Olywork Cloud. Integration requires a separate security review,
SSRF policy, authentication layer, and contract test suite.

Run the standalone tests with `python -m pytest packages/olywork-runtime/tests` from the repository
root, or install this directory as its own Python package.
