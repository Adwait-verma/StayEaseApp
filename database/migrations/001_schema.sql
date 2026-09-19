-- StayEase canonical schema for MySQL 8.4+
-- The Docker image runs this file inside MYSQL_DATABASE on first startup.

SET NAMES utf8mb4;
SET time_zone = '+00:00';

CREATE TABLE roles (
    role_id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(30) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    user_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_email CHECK (email LIKE '%_@_%.__%')
);

CREATE TABLE user_roles (
    user_id BIGINT UNSIGNED NOT NULL,
    role_id SMALLINT UNSIGNED NOT NULL,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_roles_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role
        FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE RESTRICT
);

CREATE TABLE properties (
    property_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    host_id BIGINT UNSIGNED NOT NULL,
    title VARCHAR(150) NOT NULL,
    slug VARCHAR(180) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    address_line VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    capacity SMALLINT UNSIGNED NOT NULL,
    bedrooms SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    bathrooms DECIMAL(3,1) UNSIGNED NOT NULL DEFAULT 1.0,
    base_price DECIMAL(10,2) UNSIGNED NOT NULL,
    average_rating DECIMAL(3,2) UNSIGNED NOT NULL DEFAULT 0.00,
    review_count INT UNSIGNED NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_properties_host
        FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_properties_capacity CHECK (capacity BETWEEN 1 AND 50),
    CONSTRAINT chk_properties_bedrooms CHECK (bedrooms BETWEEN 1 AND 30),
    CONSTRAINT chk_properties_bathrooms CHECK (bathrooms > 0),
    CONSTRAINT chk_properties_price CHECK (base_price > 0),
    CONSTRAINT chk_properties_rating CHECK (average_rating BETWEEN 0 AND 5)
);

CREATE TABLE property_images (
    image_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    property_id BIGINT UNSIGNED NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(180) NOT NULL,
    display_order SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    CONSTRAINT fk_property_images_property
        FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE,
    CONSTRAINT uq_property_image_order UNIQUE (property_id, display_order)
);

CREATE TABLE amenities (
    amenity_id SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    amenity_name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE property_amenities (
    property_id BIGINT UNSIGNED NOT NULL,
    amenity_id SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (property_id, amenity_id),
    CONSTRAINT fk_property_amenities_property
        FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE,
    CONSTRAINT fk_property_amenities_amenity
        FOREIGN KEY (amenity_id) REFERENCES amenities(amenity_id) ON DELETE RESTRICT
);

CREATE TABLE availability_windows (
    availability_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    property_id BIGINT UNSIGNED NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price_per_night DECIMAL(10,2) UNSIGNED NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    note VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_availability_property
        FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE,
    CONSTRAINT chk_availability_dates CHECK (start_date < end_date),
    CONSTRAINT chk_availability_price CHECK (price_per_night > 0),
    CONSTRAINT uq_availability_window UNIQUE (property_id, start_date, end_date)
);

CREATE TABLE bookings (
    booking_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    guest_id BIGINT UNSIGNED NOT NULL,
    property_id BIGINT UNSIGNED NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guest_count SMALLINT UNSIGNED NOT NULL,
    nightly_rate DECIMAL(10,2) UNSIGNED NOT NULL,
    total_nights SMALLINT UNSIGNED NOT NULL,
    total_amount DECIMAL(12,2) UNSIGNED NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    cancellation_reason VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bookings_guest
        FOREIGN KEY (guest_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_property
        FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE RESTRICT,
    CONSTRAINT chk_bookings_dates CHECK (check_in < check_out),
    CONSTRAINT chk_bookings_guests CHECK (guest_count > 0),
    CONSTRAINT chk_bookings_nights CHECK (total_nights > 0),
    CONSTRAINT chk_bookings_amount CHECK (nightly_rate > 0 AND total_amount > 0),
    CONSTRAINT chk_bookings_status
        CHECK (status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED'))
);

CREATE TABLE booking_status_history (
    history_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    booking_id BIGINT UNSIGNED NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_history_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
);

CREATE TABLE payments (
    payment_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    booking_id BIGINT UNSIGNED NOT NULL UNIQUE,
    amount DECIMAL(12,2) UNSIGNED NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    provider_reference VARCHAR(100) UNIQUE,
    paid_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE RESTRICT,
    CONSTRAINT chk_payments_amount CHECK (amount > 0),
    CONSTRAINT chk_payments_status
        CHECK (status IN ('PENDING', 'PAID', 'FAILED', 'REFUNDED'))
);

CREATE TABLE reviews (
    review_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    booking_id BIGINT UNSIGNED NOT NULL UNIQUE,
    guest_id BIGINT UNSIGNED NOT NULL,
    property_id BIGINT UNSIGNED NOT NULL,
    rating TINYINT UNSIGNED NOT NULL,
    comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_reviews_booking
        FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE RESTRICT,
    CONSTRAINT fk_reviews_guest
        FOREIGN KEY (guest_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_reviews_property
        FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE RESTRICT,
    CONSTRAINT chk_reviews_rating CHECK (rating BETWEEN 1 AND 5)
);

CREATE TABLE favorites (
    user_id BIGINT UNSIGNED NOT NULL,
    property_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, property_id),
    CONSTRAINT fk_favorites_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_favorites_property
        FOREIGN KEY (property_id) REFERENCES properties(property_id) ON DELETE CASCADE
);

CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_properties_search ON properties(city, is_active, capacity, base_price);
CREATE INDEX idx_properties_host ON properties(host_id, is_active);
CREATE INDEX idx_availability_search
    ON availability_windows(property_id, is_active, start_date, end_date);
CREATE INDEX idx_bookings_overlap
    ON bookings(property_id, status, check_in, check_out);
CREATE INDEX idx_bookings_guest ON bookings(guest_id, created_at);
CREATE INDEX idx_payments_status ON payments(status, created_at);
CREATE INDEX idx_reviews_property ON reviews(property_id, created_at);

CREATE VIEW property_catalog AS
SELECT
    p.property_id,
    p.host_id,
    p.title,
    p.slug,
    p.description,
    p.address_line,
    p.city,
    p.country,
    p.capacity,
    p.bedrooms,
    p.bathrooms,
    p.base_price,
    p.average_rating,
    p.review_count,
    p.is_active,
    u.full_name AS host_name,
    (
        SELECT pi.image_url
        FROM property_images pi
        WHERE pi.property_id = p.property_id
        ORDER BY pi.display_order
        LIMIT 1
    ) AS cover_image
FROM properties p
JOIN users u ON u.user_id = p.host_id;
