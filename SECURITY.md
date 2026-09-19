# Security policy

StayEase is a portfolio application and must not be used to process real reservations or financial information.

## Security design

- Passwords are salted and hashed with scrypt.
- Protected API routes verify short-lived JWTs and reload the current user.
- Role and ownership checks are performed on the server.
- Prices and totals are calculated from database-backed availability.
- Database and signing credentials are supplied through environment variables.
- Browser origins are explicitly configurable through `CORS_ORIGINS`.
- The demo payment flow stores no card, bank, or identity-document data.

## Reporting a problem

Please open a private GitHub security advisory for sensitive findings. Use a regular issue only when the report contains no secret, exploit detail, personal data, or active vulnerability information.

## Demo credentials

The documented accounts are intentionally seeded local data. Never reuse their passwords for a personal account or a public deployment. Replace all values from `.env.example` before exposing an environment to the internet.
