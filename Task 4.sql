
-- TASK 1: Find users who have NOT made any bookings
-- Used to identify inactive users for engagement strategies
SELECT name, email
FROM user
WHERE user_id NOT IN (
SELECT user_id FROM booking
);

---

-- TASK 2: Get all active users
-- Used to display currently active users in the system
SELECT user_id, name, email
FROM user
WHERE is_active = TRUE;

---

-- TASK 3: List all properties in a specific city (Goa)
-- Used in property search functionality
SELECT title, city, base_price
FROM property
WHERE city = 'Goa';

---

-- TASK 4: Count number of properties in each city
-- Used for analytics and filtering options
SELECT city, COUNT(property_id) AS property_count
FROM property
GROUP BY city;

---

-- TASK 5: Average payment amount (only successful payments)
-- Used for financial insights
SELECT AVG(amount) AS avg_paid_amount
FROM payment
WHERE status = 'PAID';

---


-- TASK 6: Get all properties with their host names
-- Used to display property listings with host details
SELECT p.title, u.name AS host_name
FROM property p
JOIN user u ON p.host_id = u.user_id;

---

-- TASK 7: Get booking details with user information
-- Used in booking history display
SELECT b.booking_id, u.name, b.check_in, b.check_out
FROM booking b
JOIN user u ON b.user_id = u.user_id;

---

-- TASK 8: Get booking details with property titles
-- Used to show complete booking info in UI
SELECT b.booking_id, p.title, b.check_in, b.check_out
FROM booking b
JOIN property_availability pa ON b.availability_id = pa.availability_id
JOIN property p ON pa.property_id = p.property_id;

---

-- TASK 9: Total number of bookings per user
-- Used for user activity tracking
SELECT user_id, COUNT(*) AS total_bookings
FROM booking
GROUP BY user_id;

---

-- TASK 10: Average rating per property
-- Used for displaying property ratings in UI
SELECT p.title, AVG(r.rating) AS avg_rating
FROM review r
JOIN booking b ON r.booking_id = b.booking_id
JOIN property_availability pa ON b.availability_id = pa.availability_id
JOIN property p ON pa.property_id = p.property_id
GROUP BY p.property_id;

---


-- TASK 11: Users with more than one booking
-- Used to identify frequent users
SELECT user_id, COUNT(*) AS total_bookings
FROM booking
GROUP BY user_id
HAVING COUNT(*) > 1;

---

-- TASK 12: Properties priced above average
-- Used for premium listing insights
SELECT title, base_price
FROM property
WHERE base_price > (
SELECT AVG(base_price) FROM property
);

---

-- TASK 13: Users who have made at least one booking
-- Used for active user filtering
SELECT name
FROM user u
WHERE EXISTS (
SELECT 1
FROM booking b
WHERE b.user_id = u.user_id
);

---

-- TASK 14: Properties that have never been booked
-- Used to identify underperforming listings
SELECT p.title
FROM property p
WHERE NOT EXISTS (
SELECT 1
FROM property_availability pa
JOIN booking b ON pa.availability_id = b.availability_id
WHERE pa.property_id = p.property_id
);

---

-- TASK 15: Total revenue per property (PAID only)
-- Used for business analytics and host earnings
SELECT p.title, SUM(pay.amount) AS total_revenue
FROM payment pay
JOIN booking b ON pay.booking_id = b.booking_id
JOIN property_availability pa ON b.availability_id = pa.availability_id
JOIN property p ON pa.property_id = p.property_id
WHERE pay.status = 'PAID'
GROUP BY p.property_id;


