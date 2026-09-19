-- Stored procedures and triggers that protect booking and review invariants.

DELIMITER $$

CREATE PROCEDURE sp_create_booking(
    IN p_guest_id BIGINT UNSIGNED,
    IN p_property_id BIGINT UNSIGNED,
    IN p_check_in DATE,
    IN p_check_out DATE,
    IN p_guest_count SMALLINT UNSIGNED,
    OUT p_booking_id BIGINT UNSIGNED
)
BEGIN
    DECLARE v_capacity SMALLINT UNSIGNED DEFAULT NULL;
    DECLARE v_host_id BIGINT UNSIGNED DEFAULT NULL;
    DECLARE v_guest_active BOOLEAN DEFAULT NULL;
    DECLARE v_guest_role_count INT DEFAULT 0;
    DECLARE v_nightly_rate DECIMAL(10,2) DEFAULT NULL;
    DECLARE v_overlap_count INT DEFAULT 0;
    DECLARE v_total_nights SMALLINT UNSIGNED;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_check_in IS NULL OR p_check_out IS NULL OR p_check_in >= p_check_out THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Check-out must be after check-in';
    END IF;

    IF p_guest_count IS NULL OR p_guest_count < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'At least one guest is required';
    END IF;

    START TRANSACTION;

    -- Every booking path locks the property first. Competing attempts for the
    -- same property therefore run their overlap checks serially.
    SELECT capacity, host_id
      INTO v_capacity, v_host_id
      FROM properties
     WHERE property_id = p_property_id
       AND is_active = TRUE
     FOR UPDATE;

    IF v_capacity IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Property is unavailable';
    END IF;

    IF p_guest_id = v_host_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Hosts cannot book their own property';
    END IF;

    IF p_guest_count > v_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Guest count exceeds property capacity';
    END IF;

    SELECT is_active
      INTO v_guest_active
      FROM users
     WHERE user_id = p_guest_id;

    SELECT COUNT(*)
      INTO v_guest_role_count
      FROM user_roles ur
      JOIN roles r ON r.role_id = ur.role_id
     WHERE ur.user_id = p_guest_id
       AND r.role_name = 'GUEST';

    IF v_guest_active IS NULL OR v_guest_active = FALSE OR v_guest_role_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'An active guest account is required';
    END IF;

    SELECT price_per_night
      INTO v_nightly_rate
      FROM availability_windows
     WHERE property_id = p_property_id
       AND is_active = TRUE
       AND start_date <= p_check_in
       AND end_date >= p_check_out
     ORDER BY price_per_night, availability_id
     LIMIT 1
     FOR UPDATE;

    IF v_nightly_rate IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No availability covers the requested dates';
    END IF;

    SELECT COUNT(*)
      INTO v_overlap_count
      FROM bookings
     WHERE property_id = p_property_id
       AND status IN ('PENDING', 'CONFIRMED')
       AND p_check_in < check_out
       AND p_check_out > check_in;

    IF v_overlap_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Property is already booked for those dates';
    END IF;

    SET v_total_nights = DATEDIFF(p_check_out, p_check_in);

    INSERT INTO bookings (
        guest_id,
        property_id,
        check_in,
        check_out,
        guest_count,
        nightly_rate,
        total_nights,
        total_amount,
        status
    ) VALUES (
        p_guest_id,
        p_property_id,
        p_check_in,
        p_check_out,
        p_guest_count,
        v_nightly_rate,
        v_total_nights,
        v_nightly_rate * v_total_nights,
        'PENDING'
    );

    SET p_booking_id = LAST_INSERT_ID();
    COMMIT;
END$$

CREATE TRIGGER trg_bookings_after_insert
AFTER INSERT ON bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_status_history (booking_id, old_status, new_status)
    VALUES (NEW.booking_id, NULL, NEW.status);
END$$

CREATE TRIGGER trg_bookings_before_update
BEFORE UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF NEW.status <> OLD.status AND NOT (
        (OLD.status = 'PENDING' AND NEW.status IN ('CONFIRMED', 'CANCELLED'))
        OR (OLD.status = 'CONFIRMED' AND NEW.status IN ('COMPLETED', 'CANCELLED'))
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid booking status transition';
    END IF;

    IF NEW.status = 'CANCELLED' AND NULLIF(TRIM(NEW.cancellation_reason), '') IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cancellation reason is required';
    END IF;

    IF NEW.check_in <> OLD.check_in
       OR NEW.check_out <> OLD.check_out
       OR NEW.property_id <> OLD.property_id
       OR NEW.guest_id <> OLD.guest_id
       OR NEW.total_amount <> OLD.total_amount THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Core booking details are immutable';
    END IF;
END$$

CREATE TRIGGER trg_bookings_after_update
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF NEW.status <> OLD.status THEN
        INSERT INTO booking_status_history (booking_id, old_status, new_status)
        VALUES (NEW.booking_id, OLD.status, NEW.status);
    END IF;
END$$

CREATE TRIGGER trg_payments_before_insert
BEFORE INSERT ON payments
FOR EACH ROW
BEGIN
    DECLARE v_total DECIMAL(12,2);
    DECLARE v_status VARCHAR(20);

    SELECT total_amount, status
      INTO v_total, v_status
      FROM bookings
     WHERE booking_id = NEW.booking_id;

    IF v_total IS NULL OR v_status <> 'PENDING' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only pending bookings can be paid';
    END IF;

    IF NEW.amount <> v_total THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Payment amount must equal booking total';
    END IF;
END$$

CREATE TRIGGER trg_payments_after_update
AFTER UPDATE ON payments
FOR EACH ROW
BEGIN
    IF OLD.status <> 'PAID' AND NEW.status = 'PAID' THEN
        UPDATE bookings
           SET status = 'CONFIRMED'
         WHERE booking_id = NEW.booking_id
           AND status = 'PENDING';
    END IF;
END$$

CREATE TRIGGER trg_reviews_before_insert
BEFORE INSERT ON reviews
FOR EACH ROW
BEGIN
    DECLARE v_guest_id BIGINT UNSIGNED;
    DECLARE v_property_id BIGINT UNSIGNED;
    DECLARE v_status VARCHAR(20);

    SELECT guest_id, property_id, status
      INTO v_guest_id, v_property_id, v_status
      FROM bookings
     WHERE booking_id = NEW.booking_id;

    IF v_guest_id IS NULL OR v_status <> 'COMPLETED' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only completed stays can be reviewed';
    END IF;

    SET NEW.guest_id = v_guest_id;
    SET NEW.property_id = v_property_id;
END$$

CREATE TRIGGER trg_reviews_after_insert
AFTER INSERT ON reviews
FOR EACH ROW
BEGIN
    UPDATE properties
       SET average_rating = ROUND(
               ((average_rating * review_count) + NEW.rating) / (review_count + 1),
               2
           ),
           review_count = review_count + 1
     WHERE property_id = NEW.property_id;
END$$

CREATE TRIGGER trg_reviews_before_update
BEFORE UPDATE ON reviews
FOR EACH ROW
BEGIN
    IF NEW.booking_id <> OLD.booking_id
       OR NEW.guest_id <> OLD.guest_id
       OR NEW.property_id <> OLD.property_id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Review ownership is immutable';
    END IF;
END$$

CREATE TRIGGER trg_reviews_after_update
AFTER UPDATE ON reviews
FOR EACH ROW
BEGIN
    IF NEW.rating <> OLD.rating THEN
        UPDATE properties
           SET average_rating = ROUND(
               ((average_rating * review_count) - OLD.rating + NEW.rating) / review_count,
               2
           )
         WHERE property_id = NEW.property_id;
    END IF;
END$$

CREATE TRIGGER trg_reviews_after_delete
AFTER DELETE ON reviews
FOR EACH ROW
BEGIN
    UPDATE properties
       SET average_rating = CASE
               WHEN review_count <= 1 THEN 0
               ELSE ROUND(((average_rating * review_count) - OLD.rating) / (review_count - 1), 2)
           END,
           review_count = CASE WHEN review_count = 0 THEN 0 ELSE review_count - 1 END
     WHERE property_id = OLD.property_id;
END$$

DELIMITER ;
