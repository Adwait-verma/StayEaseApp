# Concurrency proof

StayEase does not rely on a browser-side availability check to prevent double booking. The canonical MySQL procedure locks the selected property row before checking active overlaps and inserting a reservation.

## Automated race

`database/tests/concurrency_test.py` creates 25 independent guest accounts, opens 25 database connections, waits on a shared barrier, and releases every booking attempt for the same property and dates together.

The test succeeds only when:

- exactly one request creates a booking;
- the other 24 requests are rejected as conflicts; and
- a final database query finds exactly one active booking overlapping those dates.

GitHub Actions runs this race against MySQL 8.4 after applying every migration. Its result is written into the workflow summary so the concurrency claim is continuously reproducible rather than based on a screenshot or manual demonstration.

## Run locally

Start the database through Docker Compose, install the backend development requirements, and run:

```bash
python database/tests/concurrency_test.py --contenders 25
```

The test uses the following environment variables when they are present: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE`.

## Why the lock matters

Without a lock, two transactions can both observe that no overlap exists and then both insert a reservation. StayEase acquires the property lock first, so attempts for the same listing are evaluated serially while bookings for different properties can still proceed independently.
