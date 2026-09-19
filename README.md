# StayEase

StayEase is an accommodation marketplace built to demonstrate more than CRUD. Its core engineering problem is coordinating property availability, bookings, payments, and reviews without allowing conflicting reservations or invalid state transitions.

This repository began as a database-systems prototype. It is being developed into a portfolio-ready full-stack application with a React client, Flask API, and MySQL data layer.

## Why this project matters

Vacation-rental systems have deceptively difficult data problems. Two guests may attempt to reserve the same property at the same time, prices can vary by date range, a review must belong to a completed stay, and payment and cancellation states must remain consistent. StayEase makes those rules explicit and testable.

## Planned capabilities

- Guest, host, and administrator accounts with role-based authorization
- Property publishing, amenities, capacity, pricing, and availability windows
- Search by city, dates, party size, and price
- Transactional bookings with overlap prevention
- Simulated payment lifecycle and booking cancellation
- Verified reviews restricted to completed stays
- Guest, host, and administrator dashboards
- Database indexes, constraints, triggers, migrations, and repeatable seed data
- Automated API tests and continuous integration

## Technology

| Layer | Technology |
| --- | --- |
| Frontend | React, TypeScript, Vite |
| Backend | Flask, SQLAlchemy, JWT authentication |
| Database | MySQL 8.4 |
| Local environment | Docker Compose |
| Quality | Pytest, ESLint, GitHub Actions |

## Architecture

```text
React client
    |
    | JSON over HTTP
    v
Flask REST API
    |
    | validated services + transactions
    v
MySQL
    |- relational constraints
    |- indexed availability queries
    `- booking and review integrity rules
```

See [the architecture notes](docs/ARCHITECTURE.md) for the design boundaries and [the roadmap](docs/ROADMAP.md) for development milestones.

## Local setup

The complete application setup will use one command once the API and client milestones land:

```bash
cp .env.example .env
docker compose up --build
```

For now, the Compose file provisions MySQL and automatically loads versioned SQL files from `database/migrations/` on the first database initialization.

## Repository history

The original `Task 1.pdf` through `Task 6.sql` files are retained as the coursework baseline. The maintainable implementation lives in purpose-specific `database/`, `backend/`, `frontend/`, and `docs/` directories as those milestones are completed.

## Project status

Active development. The current milestone is replacing the exploratory SQL scripts with a consistent, migration-driven relational model.
