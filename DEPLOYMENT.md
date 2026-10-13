# Deployment guidance

`olywork-runtime` is a library and protocol foundation. It is not a turnkey production server.

## Local development

Run the contract tests from the repository root:

```text
python -m pytest tests
```

A deployment must provide an HTTP server that adapts the WSGI application and must supply a
verifier backed by an environment-specific secret store. Never commit a bearer token.

## Production requirements

Before exposing the runtime publicly, the operator must provide:

- TLS termination and a trusted reverse proxy;
- secret storage outside the repository and process logs;
- network egress controls and the supplied SSRF validator;
- request size, timeout, rate, and concurrency limits;
- structured error handling that does not echo credentials;
- health checks, access logs with authorization values redacted, and an incident process;
- a dependency and license review for any server or WSGI adapter added by the operator.

The hosted Olywork service is not part of this repository. Do not point this package at production
credentials without completing those controls and reviewing the applicable license notices.
