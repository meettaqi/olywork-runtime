# Public release status

The `olywork-runtime` repository is an independently authored runtime foundation. This status
records the checks completed for the public repository itself.

## Complete

- Separate repository and history from the private Olywork core.
- Apache-2.0 license and attribution notice.
- No credentials, customer data, hosted billing, private catalog, or production infrastructure.
- Contract schemas, HTTP adapter, MCP dispatcher, authentication boundary, and SSRF validation.
- Request-size protection and declared argument validation.
- Contract tests and CI on Python 3.11, 3.12, and 3.13.
- Deployment and security guidance.

## Intentionally out of scope

- Hosted Olywork account operations, billing, catalog ranking, and provider credentials.
- Database persistence, migrations, OAuth provider implementations, and production orchestration.
- A claim that the private Olywork core is independently authored.

The public package must not be described as a complete supported self-host service until those
out-of-scope components are independently implemented, reviewed, and documented.
