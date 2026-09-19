# Recruiter walkthrough

This walkthrough keeps the conversation on engineering decisions instead of spending interview time on setup. Start the application with Docker Compose and use the seeded accounts from the root README.

## Five-minute demo

### 1. Introduce the problem — 30 seconds

> StayEase is an accommodation marketplace built around booking correctness. The main problem I solved is preventing overlapping reservations while keeping guest, host, and admin workflows separate.

Open the home page and point out date, city, and guest filtering.

### 2. Show the product — 90 seconds

1. Open a property and select an available date range.
2. Sign in as the guest and create a booking.
3. Confirm the simulated payment and show the updated guest dashboard.
4. Explain that totals come from stored availability, not from a browser-supplied value.

### 3. Show role boundaries — 60 seconds

1. Sign in as the host and show listing and availability management.
2. Explain that a host can manage only their own properties.
3. Sign in as the administrator and show marketplace totals and booking status counts.

### 4. Explain the difficult part — 60 seconds

Open `database/migrations/002_integrity.sql` and explain the booking invariant:

```text
new_check_in < existing_check_out
AND new_check_out > existing_check_in
```

The transaction locks one property, checks a covering availability window, checks active overlaps, calculates the total, and inserts the reservation. Locking turns two competing requests into an ordered decision instead of allowing both to pass a check-then-insert race.

### 5. End with evidence — 60 seconds

Open the repository's Actions page and the API tests. Mention:

- authentication and role/ownership checks;
- rejection of a second overlapping booking;
- payment, cancellation, refund, completion, and verified-review rules;
- an enforced backend coverage floor;
- production frontend build and MySQL migration smoke test on every push.

## Honest resume bullets

Choose two or three bullets you can explain confidently:

- Built a full-stack accommodation marketplace using React, TypeScript, Flask, SQLAlchemy, and MySQL, with guest, host, and administrator workflows.
- Designed a transactional reservation flow using row-level locking and indexed date-overlap detection to prevent conflicting bookings.
- Implemented JWT authentication, role- and ownership-based authorization, scrypt password hashing, and server-side price calculation.
- Added automated coverage for critical booking, payment, refund, review, and admin journeys, enforced through GitHub Actions alongside frontend and MySQL checks.
- Containerized the three-tier application with Docker Compose and deterministic demo data for a one-command local presentation.

## Interview questions to prepare for

- Why is a database transaction necessary if the API already checks for an overlap?
- Why are date ranges modeled as half-open intervals?
- What changes would be required for multiple API instances?
- Why is a JWT not trusted for current permissions without loading the user?
- Which rules belong in application code, and which are reinforced in MySQL?
- How would you make payment confirmation idempotent with a real provider?
- What would you monitor in production?

## No-cost presentation options

- Run the project locally with Docker Compose during an interview.
- Record a two- to three-minute screen capture and link it from your portfolio.
- Add two compressed screenshots to `docs/images/` and embed them in the README.
- Use the repository's passing checks as reproducible technical evidence.

A permanent public deployment is useful but not necessary for this project.
