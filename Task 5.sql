DELIMITER $$

-- T1: DATE RANGE
CREATE TRIGGER check_date_range
BEFORE INSERT ON booking
FOR EACH ROW
BEGIN
    DECLARE s DATE;
    DECLARE e DATE;

    SELECT start_date, end_date INTO s,e
    FROM property_availability
    WHERE availability_id = NEW.availability_id;

    IF NEW.check_in < s OR NEW.check_out > e THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid booking range';
    END IF;
END$$

-- T2: OVERLAP
CREATE TRIGGER check_overlap
BEFORE INSERT ON booking
FOR EACH ROW
BEGIN
    IF EXISTS(
        SELECT 1 FROM booking
        WHERE availability_id = NEW.availability_id
        AND status IN ('CONFIRMED', 'COMPLETED')
        AND NOT (
            NEW.check_out <= check_in OR
            NEW.check_in >= check_out
        )
    )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Overlap booking';
    END IF;
END$$

-- T3: ACTIVE USER
CREATE TRIGGER check_user_active
BEFORE INSERT ON booking
FOR EACH ROW
BEGIN
    DECLARE act BOOLEAN;

    SELECT is_active INTO act FROM user
    WHERE user_id = NEW.user_id;

    IF act = FALSE THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Inactive user';
    END IF;
END$$

-- T4: TOTAL NIGHTS
CREATE TRIGGER calc_nights
BEFORE INSERT ON booking
FOR EACH ROW
BEGIN
    SET NEW.total_nights = DATEDIFF(NEW.check_out, NEW.check_in);

    IF NEW.total_nights <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid nights';
    END IF;
END$$

-- T5: USER SPENDING
CREATE TRIGGER update_spending
AFTER UPDATE ON booking
FOR EACH ROW
BEGIN
    IF NEW.status = 'CONFIRMED' AND OLD.status <> 'CONFIRMED' THEN
        UPDATE user
        SET total_spent = total_spent + NEW.total_amount
        WHERE user_id = NEW.user_id;
    END IF;
END$$

-- T6: PROPERTY RATING
CREATE TRIGGER update_rating
AFTER INSERT ON review
FOR EACH ROW
BEGIN
    DECLARE pid INT;

    SELECT pa.property_id INTO pid
    FROM booking b
    JOIN property_availability pa
    ON b.availability_id = pa.availability_id
    WHERE b.booking_id = NEW.booking_id;

    UPDATE property
    SET total_reviews = total_reviews + 1,
        sum_ratings = sum_ratings + NEW.rating,
        avg_rating = (sum_ratings + NEW.rating) / (total_reviews + 1)
    WHERE property_id = pid;
END$$

DELIMITER ;
