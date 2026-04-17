-- TASK 6: TRANSACTION MANAGEMENT (FINAL)

SET autocommit = 0;

-- DEMO 1: SUCCESSFUL TRANSACTION (COMMIT)
SELECT * FROM property_availability WHERE availability_id = 1;
SELECT * FROM booking WHERE availability_id = 1;

START TRANSACTION;

INSERT INTO booking
(user_id, availability_id, check_in, check_out, total_amount, status)
VALUES (6, 1, '2026-05-05', '2026-05-07', 6000, 'CONFIRMED');

INSERT INTO payment (booking_id, amount, status)
VALUES (LAST_INSERT_ID(), 6000, 'PAID');

COMMIT;



-- DEMO 2: FAILED TRANSACTION (ROLLBACK)

SELECT * FROM property_availability WHERE availability_id = 2;
SELECT * FROM booking WHERE availability_id = 2;
START TRANSACTION;

INSERT INTO booking
(user_id, availability_id, check_in, check_out, total_amount, status)
VALUES (7, 2, '2026-05-08', '2026-05-10', 5400, 'CONFIRMED');

INSERT INTO payment (booking_id, amount, status)
VALUES (9999, 6400, 'PAID'); -- will fail

ROLLBACK;


-- DEMO 3: CONSTRAINT CONFLICT (DOUBLE BOOKING)
SELECT * FROM booking WHERE availability_id = 3;

START TRANSACTION;

INSERT INTO booking
(user_id, availability_id, check_in, check_out, total_amount, status)
VALUES (8, 3, '2026-05-04', '2026-05-06', 4000, 'CONFIRMED');

COMMIT;

START TRANSACTION;

INSERT INTO booking
(user_id, availability_id, check_in, check_out, total_amount, status)
VALUES (9, 3, '2026-05-04', '2026-05-06', 4000, 'CONFIRMED');

ROLLBACK;


-- DEMO 4: DIRTY READ (RUN IN 2 SESSIONS)
-- T1: UPDATE → (not committed)
-- T2: READ → sees new value
-- T1: ROLLBACK → value disappears

-- SESSION 1
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
START TRANSACTION;
UPDATE booking SET total_amount = 9999 WHERE booking_id = 1;
-- do not commit

-- SESSION 2
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
START TRANSACTION;
SELECT total_amount FROM booking WHERE booking_id = 1;
COMMIT;

-- SESSION 1
ROLLBACK;


-- DEMO 5: NON-REPEATABLE READ (RUN IN 2 SESSIONS)
-- T1: READ → 5000
-- T2: UPDATE → COMMIT
-- T1: READ → 8000
-- SESSION 1
START TRANSACTION;
SELECT total_amount FROM booking WHERE booking_id = 1;

-- SESSION 2
UPDATE booking SET total_amount = 8000 WHERE booking_id = 1;
COMMIT;

-- SESSION 1
SELECT total_amount FROM booking WHERE booking_id = 1;
COMMIT;


-- DEMO 6: LOST UPDATE (RUN IN 2 SESSIONS)

-- SESSION 1
START TRANSACTION;
SELECT total_amount FROM booking WHERE booking_id = 1;

-- SESSION 2
START TRANSACTION;
UPDATE booking SET total_amount = 6000 WHERE booking_id = 1;
COMMIT;

-- SESSION 1
UPDATE booking SET total_amount = 5500 WHERE booking_id = 1;
COMMIT;


-- DEMO 7: NON-CONFLICTING TRANSACTIONS

START TRANSACTION;

INSERT INTO booking
VALUES (NULL, 6, 4, '2026-05-15', '2026-05-17', 5000, 'CONFIRMED');

COMMIT;

START TRANSACTION;

INSERT INTO booking
VALUES (NULL, 7, 5, '2026-05-15', '2026-05-17', 5500, 'CONFIRMED');

COMMIT;


-- END OF TASK 6