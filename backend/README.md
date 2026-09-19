# StayEase API

The Flask API owns authentication, authorization, pricing, booking, payment, cancellation, and review rules. The client never sends trusted totals or arbitrary user IDs.

The versioned OpenAPI contract is available from `/api/openapi.yaml`. When the full application is running, Swagger UI is available at `http://localhost:3000/api-docs` for schema inspection and local request execution.

## Run locally without Docker

Create the MySQL database using the files in `../database/migrations`, copy the root `.env.example` to `.env`, and then run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python wsgi.py
```

On Windows PowerShell, activate the environment with `.\.venv\Scripts\Activate.ps1`.

## Main endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | API and database readiness |
| `POST` | `/api/auth/register` | Guest or host registration |
| `POST` | `/api/auth/login` | JWT authentication |
| `GET` | `/api/properties` | Indexed property and availability search |
| `POST` | `/api/properties` | Host property creation |
| `POST` | `/api/properties/:id/availability` | Host availability management |
| `POST` | `/api/bookings` | Transactional guest booking |
| `POST` | `/api/bookings/:id/pay` | Simulated payment confirmation |
| `POST` | `/api/bookings/:id/cancel` | Booking cancellation and simulated refund |
| `POST` | `/api/bookings/:id/complete` | Host/admin stay completion |
| `POST` | `/api/bookings/:id/review` | Verified-stay review |
| `GET` | `/api/admin/stats` | Marketplace operational metrics |

## Booking transaction

Every booking attempt locks its property row, checks a covering availability window, checks indexed active overlaps, calculates the nightly rate and total on the server, and then inserts the reservation. Requests for different properties remain independent, while requests for the same property serialize safely.

## Security

- Passwords use Python's memory-hard scrypt implementation with random salts.
- JWTs expire and are verified on every protected request.
- Role and ownership rules are resolved from the authenticated database user.
- Demo payment processing stores no card or bank information.
