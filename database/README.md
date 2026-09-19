# Database

The canonical MySQL implementation lives in `migrations/`. Docker executes these files alphabetically the first time the database volume is created:

1. `001_schema.sql` creates normalized tables, indexes, and the property-catalog view.
2. `002_integrity.sql` installs transactional booking, lifecycle, payment, and review rules.
3. `003_seed.sql` adds deterministic portfolio data.

The root-level `Task *.sql` files are retained only as the original coursework baseline.

## Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Administrator | `admin@stayease.local` | `Admin123!` |
| Host | `host@stayease.local` | `Host123!` |
| Guest | `guest@stayease.local` | `Guest123!` |

These credentials are local demonstration data. Their passwords are stored as memory-hard scrypt hashes, not plaintext.

## Booking concurrency

`sp_create_booking` locks the selected property before checking availability and overlapping bookings. All application booking paths use the same lock order, so two concurrent attempts for the same property cannot both pass the overlap check.

Active overlaps use half-open date ranges:

```sql
requested_check_in < existing_check_out
AND requested_check_out > existing_check_in
```

This allows a new guest to check in on the same date that the previous guest checks out.

## Resetting local data

Removing the local Docker volume and restarting Compose recreates the schema and seed data. This is destructive and should only be used for disposable local development data.
