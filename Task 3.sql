DROP DATABASE IF EXISTS easenow;
CREATE DATABASE easenow;
USE easenow;

-- =========================
-- USER
-- =========================
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    total_spent DECIMAL(12,2) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM user;

-- =========================
-- ROLE
-- =========================
CREATE TABLE role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE user_role (
    user_id INT,
    role_id INT,
    PRIMARY KEY(user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role(role_id) ON DELETE CASCADE
);

-- =========================
-- PROPERTY
-- =========================
CREATE TABLE property (
    property_id INT AUTO_INCREMENT PRIMARY KEY,
    host_id INT,
    title VARCHAR(150),
    description TEXT,
    city VARCHAR(100),
    base_price DECIMAL(10,2),

    -- trigger fields
    total_reviews INT DEFAULT 0,
    sum_ratings INT DEFAULT 0,
    avg_rating DECIMAL(3,2) DEFAULT 0,

    FOREIGN KEY (host_id) REFERENCES user(user_id)
);

-- =========================
-- AVAILABILITY
-- =========================
CREATE TABLE property_availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    property_id INT,
    start_date DATE,
    end_date DATE,
    price_per_night DECIMAL(10,2),
    CHECK (start_date < end_date),
    FOREIGN KEY (property_id) REFERENCES property(property_id)
);

-- =========================
-- BOOKING
-- =========================
CREATE TABLE booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    availability_id INT,
    check_in DATE,
    check_out DATE,
    total_nights INT,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'CONFIRMED'
        CHECK (status IN ('CONFIRMED','CANCELLED','COMPLETED')),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (availability_id) REFERENCES property_availability(availability_id),
    CHECK (check_in < check_out)
);

-- =========================
-- PAYMENT
-- =========================
CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    amount DECIMAL(10,2),
    status VARCHAR(20),
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
);

-- =========================
-- REVIEW
-- =========================
CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    user_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);


-- ROLES
INSERT INTO role VALUES
(1,'ADMIN'),
(2,'HOST'),
(3,'GUEST');

-- USERS (2 admins, 3 hosts, 5 users)
INSERT INTO user (name,email,password) VALUES
('Admin1','admin1@mail.com','123'),
('Admin2','admin2@mail.com','123'),

('Host1','host1@mail.com','123'),
('Host2','host2@mail.com','123'),
('Host3','host3@mail.com','123'),

('User1','user1@mail.com','123'),
('User2','user2@mail.com','123'),
('User3','user3@mail.com','123'),
('User4','user4@mail.com','123'),
('User5','user5@mail.com','123');

-- USER ROLE
INSERT INTO user_role VALUES
(1,1),(2,1),
(3,2),(4,2),(5,2),
(6,3),(7,3),(8,3),(9,3),(10,3);

-- PROPERTIES
INSERT INTO property (host_id,title,description,city,base_price) VALUES
(3,'Property1','Nice stay','Goa',3000),
(3,'Property2','Nice stay','Goa',3200),
(4,'Property3','Nice stay','Delhi',2000),
(4,'Property4','Nice stay','Delhi',2500),
(5,'Property5','Nice stay','Mumbai',4000),
(5,'Property6','Nice stay','Mumbai',4200),
(3,'Property7','Nice stay','Goa',3500),
(4,'Property8','Nice stay','Delhi',2700),
(5,'Property9','Nice stay','Mumbai',4500),
(3,'Property10','Nice stay','Goa',2800);

-- AVAILABILITY
INSERT INTO property_availability
(property_id,start_date,end_date,price_per_night)
VALUES
(1,'2026-05-01','2026-05-10',3000),
(2,'2026-05-01','2026-05-10',3200),
(3,'2026-05-01','2026-05-10',2000),
(4,'2026-05-01','2026-05-10',2500),
(5,'2026-05-01','2026-05-10',4000),
(6,'2026-05-01','2026-05-10',4200),
(7,'2026-05-01','2026-05-10',3500),
(8,'2026-05-01','2026-05-10',2700),
(9,'2026-05-01','2026-05-10',4500),
(10,'2026-05-01','2026-05-10',2800);

-- BOOKINGS (NO OVERLAP, TRIGGER SAFE)

SELECT * FROM booking;
INSERT INTO booking
(user_id,availability_id,check_in,check_out,total_amount,status)
VALUES
(6,1,'2026-05-01','2026-05-03',6000,'COMPLETED'),
(7,2,'2026-05-01','2026-05-03',6400,'CONFIRMED'),
(8,3,'2026-05-01','2026-05-03',4000,'COMPLETED'),
(9,4,'2026-05-01','2026-05-03',5000,'CONFIRMED'),
(10,5,'2026-05-01','2026-05-03',8000,'COMPLETED'),
(6,6,'2026-05-01','2026-05-03',8400,'CONFIRMED'),
(7,7,'2026-05-01','2026-05-03',7000,'COMPLETED'),
(8,8,'2026-05-01','2026-05-03',5400,'CONFIRMED'),
(9,9,'2026-05-01','2026-05-03',9000,'COMPLETED'),
(10,10,'2026-05-01','2026-05-03',5600,'CONFIRMED');

-- PAYMENTS
INSERT INTO payment (booking_id,amount,status) VALUES
(1,6000,'PAID'),
(2,6400,'PAID'),
(3,4000,'PAID'),
(4,5000,'PAID'),
(5,8000,'PAID'),
(6,8400,'PENDING'),
(7,7000,'PAID'),
(8,5400,'PAID'),
(9,9000,'PAID'),
(10,5600,'FAILED');

-- REVIEWS
INSERT INTO review (booking_id,user_id,rating,comment) VALUES
(1,6,5,'Excellent'),
(2,7,4,'Nice'),
(3,8,5,'Great'),
(4,9,3,'Okay'),
(5,10,4,'Good'),
(6,6,5,'Loved it'),
(7,7,4,'Nice stay'),
(8,8,3,'Average'),
(9,9,5,'Perfect'),
(10,10,2,'Not great');

