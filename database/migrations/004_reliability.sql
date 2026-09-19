-- Replay-safe payment requests.

ALTER TABLE payments
    ADD COLUMN idempotency_key VARCHAR(100) NULL AFTER booking_id;

UPDATE payments
SET idempotency_key = CONCAT('seed-payment-', payment_id)
WHERE idempotency_key IS NULL;

ALTER TABLE payments
    MODIFY idempotency_key VARCHAR(100) NOT NULL,
    ADD CONSTRAINT uq_payments_idempotency_key UNIQUE (idempotency_key);
