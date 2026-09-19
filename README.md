# StayEase

[![CI](https://github.com/Adwait-verma/StayEaseApp/actions/workflows/ci.yml/badge.svg)](https://github.com/Adwait-verma/StayEaseApp/actions/workflows/ci.yml)

StayEase is a full-stack accommodation marketplace focused on a problem that is easy to describe and difficult to implement correctly: two guests must never reserve the same property for overlapping dates.

The application supports guest, host, and administrator journeys through a responsive React client, a role-aware Flask API, and a MySQL data layer with transactional safeguards. It runs entirely on a student laptop; paid hosting and external services are not required.

![StayEase coastal villa illustration](frontend/public/images/goa-villa.svg)

## What it demonstrates

- JWT authentication with guest, host, and administrator permissions
- Property publishing, availability windows, capacity, and date-aware pricing
- Search by city, dates, party size, and price
- Conflict-safe booking with row locking and indexed overlap detection
- Server-calculated totals and a simulated payment/refund lifecycle
- Reviews restricted to completed stays
- Guest, host, and administrator dashboards
- Versioned schema, constraints, triggers, stored procedures, and repeatable seed data
- Automated API coverage plus frontend and MySQL checks on every push

## Engineering highlights

### A booking is a transaction, not a form submission

For a selected property, the API locks the property row before it checks availability and active reservations. The database uses half-open date ranges, so a new guest may check in on the previous guest's check-out date while genuine overlaps are rejected.

```text
requested_check_in < existing_check_out
AND requested_check_out > existing_check_in
```

### The browser is not trusted

Identity and roles come from the verified token. Ownership comes from the database. Prices, stay length, and totals are calculated on the server rather than accepted from the client.

### State changes are explicit

Booking, payment, cancellation, completion, and review rules are enforced in the service and reinforced by relational constraints and triggers. The payment flow is deliberately simulated and stores no card data.

## Technology

| Layer | Technology |
| --- | --- |
| Web | React 19, TypeScript, Vite, responsive CSS |
| API | Flask, SQLAlchemy, PyJWT, scrypt password hashing |
| Data | MySQL 8.4, migrations, procedures, triggers, indexes |
| Local environment | Docker Compose, Nginx |
| Quality | Pytest, coverage, Ruff, ESLint, GitHub Actions |

## Run the complete application

Docker Desktop is the only prerequisite.

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:3000`. The API is available at `http://localhost:5000/api`, and MySQL is initialized automatically from `database/migrations/` the first time the database volume is created.

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp`.

### Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Administrator | `admin@stayease.local` | `Admin123!` |
| Host | `host@stayease.local` | `Host123!` |
| Guest | `guest@stayease.local` | `Guest123!` |

These credentials are local demonstration data. Passwords are stored as salted scrypt hashes.

## Quality checks

```bash
cd backend
python -m venv .venv
pip install -r requirements-dev.txt
pytest
ruff check app tests
```

```bash
cd frontend
npm ci
npm run lint
npm run build
```

The API suite covers authentication, authorization, property publishing, search, conflict detection, payment, refunds, completed-stay reviews, and administrator reporting. The configured coverage floor is 80%.

## Repository map

```text
backend/                 Flask API, domain models, and API tests
database/migrations/     Canonical schema, integrity rules, and seed data
frontend/                React application and Nginx container
docs/                    Architecture, roadmap, and recruiter walkthrough
.github/workflows/       Automated API, web, and MySQL verification
Task *.pdf / Task *.sql  Preserved coursework baseline
```

Read [the architecture decisions](docs/ARCHITECTURE.md), [the API reference](backend/README.md), or follow [the five-minute demo](docs/DEMO.md).

## Project status and cost

The portfolio MVP is complete and designed for a local demonstration. Public deployment is an optional future step, not a requirement: Docker Compose, the seeded workflow, automated checks, and a short screen recording provide reproducible evidence without a hosting bill.

## Project evolution

The root `Task 1.pdf` through `Task 6.sql` files and their Git history preserve the original database-coursework baseline from [ahinnraj/StayEaseApp](https://github.com/ahinnraj/StayEaseApp). The application structure, normalized migrations, transactional workflow, API, interface, tests, and documentation in this repository form the subsequent portfolio implementation. No upstream license was present, so the repository intentionally does not add or imply one.
