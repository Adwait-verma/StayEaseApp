-- QUERY 0: Find users who have NOT made any bookings
SELECT name, email
FROM user
WHERE user_id NOT IN (
    SELECT user_id
    FROM booking
);

-- 1. Get all users and their hosted properties(JOIN)
SELECT *
FROM user, property
WHERE user.user_id = property.host_id;


-- 2. Get average base price of properties where base price is greater than 5000
SELECT AVG(base_price) AS avg_price_above_5000
FROM property
WHERE base_price > 5000;


-- 3. Count number of properties available in each city
SELECT city, COUNT(property_id) AS property_count
FROM property
GROUP BY city;


-- 4. Get average payment amount for completed payments only
SELECT AVG(amount) AS avg_paid_amount
FROM payment
WHERE status = 'PAID';



-- 5. Get all active users
SELECT user_id, name, email
FROM user
WHERE is_active = TRUE;


-- 6. List all properties located in Goa
SELECT title, city, base_price
FROM property
WHERE city = 'Goa';


-- 7. Get all properties along with their host names
SELECT p.title, u.name AS host_name
FROM property p
JOIN user u ON p.host_id = u.user_id;


-- 8. Get all bookings with the user who made them
SELECT b.booking_id, u.name, b.check_in, b.check_out
FROM booking b
JOIN user u ON b.user_id = u.user_id;


-- 9. Get booking details along with property titles
SELECT b.booking_id, p.title, b.check_in, b.check_out
FROM booking b
JOIN property_availability pa ON b.availability_id = pa.availability_id
JOIN property p ON pa.property_id = p.property_id;


-- 10. Count total number of bookings made by each user
SELECT user_id, COUNT(*) AS total_bookings
FROM booking
GROUP BY user_id;


-- 11. Calculate average rating for each property
SELECT p.title, AVG(r.rating) AS avg_rating
FROM review r
JOIN booking b ON r.booking_id = b.booking_id
JOIN property_availability pa ON b.availability_id = pa.availability_id
JOIN property p ON pa.property_id = p.property_id
GROUP BY p.property_id;


-- 12. Find users who have made more than one booking
SELECT user_id, COUNT(*) AS total_bookings
FROM booking
GROUP BY user_id
HAVING COUNT(*) > 1;


-- 13. Find properties with base price higher than average price
SELECT title, base_price
FROM property
WHERE base_price > (
    SELECT AVG(base_price) FROM property
);


-- 14. Get users who have made at least one booking
SELECT name
FROM user u
WHERE EXISTS (
    SELECT 1
    FROM booking b
    WHERE b.user_id = u.user_id
);


-- 15. Find properties that have never been booked
SELECT p.title
FROM property p
WHERE NOT EXISTS (
    SELECT 1
    FROM property_availability pa
    JOIN booking b ON pa.availability_id = b.availability_id
    WHERE pa.property_id = p.property_id
);


-- 16. Calculate total revenue generated per property (only PAID payments)
SELECT p.title, SUM(pay.amount) AS total_revenue
FROM payment pay
JOIN booking b ON pay.booking_id = b.booking_id
JOIN property_availability pa ON b.availability_id = pa.availability_id
JOIN property p ON pa.property_id = p.property_id
WHERE pay.status = 'PAID'
GROUP BY p.property_id;


-- 17. Categorize bookings based on their status
SELECT booking_id,
       CASE
           WHEN status = 'COMPLETED' THEN 'Finished'
           WHEN status = 'CANCELLED' THEN 'Cancelled'
           ELSE 'Active'
       END AS booking_state
FROM booking;


-- 18. Calculate number of nights for each booking
SELECT booking_id,
       DATEDIFF(check_out, check_in) AS nights
FROM booking;


-- 19. List all hosts and their properties
SELECT u.name AS host_name, p.title
FROM user u
JOIN user_role ur ON u.user_id = ur.user_id
JOIN role r ON ur.role_id = r.role_id
JOIN property p ON u.user_id = p.host_id
WHERE r.role_name = 'HOST';


-- 20. Find the top-rated property based on average rating
SELECT p.title, AVG(r.rating) AS avg_rating
FROM review r
JOIN booking b ON r.booking_id = b.booking_id
JOIN property_availability pa ON b.availability_id = pa.availability_id
JOIN property p ON pa.property_id = p.property_id
GROUP BY p.property_id
ORDER BY avg_rating DESC
LIMIT 1;




SELECT * 
FROM property_availability 
WHERE is_available = FALSE;

SELECT * FROM user;
UPDATE user
SET is_active = FALSE
WHERE user_id = 10;