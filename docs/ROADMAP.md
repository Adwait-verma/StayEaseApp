# Development roadmap

## Completed portfolio MVP

- [x] Professional project narrative and architecture
- [x] Reproducible MySQL environment and versioned migrations
- [x] Normalized users, roles, properties, availability, bookings, payments, and reviews
- [x] Indexed search, row locking, overlap checks, and lifecycle constraints
- [x] JWT authentication and role/ownership authorization
- [x] Property, availability, booking, payment, cancellation, review, and admin APIs
- [x] Responsive marketplace, booking flow, and role-specific dashboards
- [x] API integration tests with an enforced coverage threshold
- [x] Continuous checks for Python, React, and MySQL migrations
- [x] Seeded demo accounts and recruiter walkthrough

## Recommended next additions

These are deliberately optional. Each should be added only when it demonstrates a new engineering skill rather than increasing feature count.

### Strong next step: observability

- Structured request logging with correlation IDs
- Error tracking and latency measurements
- A small operations panel for failed or abandoned bookings

### Strong next step: asynchronous work

- Queue booking-confirmation and cancellation emails
- Use a local development mail viewer instead of a paid email provider
- Add retry and idempotency rules for notification jobs

### Product extensions

- Favorites using the existing `favorites` table
- Property image upload with local object-storage emulation
- Map-based discovery with an open map provider
- Seasonal pricing and minimum-stay rules
- Payment-provider sandbox mode behind the current payment interface

### Deployment, only if useful

- Record a local walkthrough first; it is free and sufficient for applications
- Consider a temporary free-tier deployment only for interviews or demonstrations
- Never commit production credentials or replace the simulated payment flow with real card handling for this student project

## Known portfolio boundaries

- Payments are simulated and intentionally accept no financial information.
- The MySQL locking strategy is validated by schema checks and service tests; a dedicated concurrent load test remains future work.
- Property images are repository assets rather than user uploads.
- Public cloud availability and production monitoring are outside the current local-first scope.
